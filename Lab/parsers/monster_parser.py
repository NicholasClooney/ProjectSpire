#!/usr/bin/env python3
"""Parse decompiled STS2 monster C# into structured JSON.

Conservative approach:
- Only emits facts explicit in the monster source.
- Move IDs and titles are derived from localization keys, not the C# state
  machine (which uses internal IDs that differ from localization keys).
- Monsters with no name key in localization are skipped (test helpers,
  deprecated entries, non-combat entities).
- HP values capture both base and ascension-scaled variants where present.
- Move effects (damage, block, powers, status cards, heal) are extracted from
  handler bodies and enriched onto localization-derived moves where IDs match.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common import (
    DEFAULT_LANGUAGE,
    DECOMPILED_DIR,
    IMAGE_DIR,
    LAB_DIR,
    LOCALIZATION_DIR,
    class_name_to_id,
    infer_version_from_path,
    latest_decompiled_version,
    list_decompiled_versions,
    load_localization,
    source_version,
    to_jsonable,
)


MONSTERS_SUBDIR = "MegaCrit.Sts2.Core.Models.Monsters"
PARSER_VERSION = "0.2.0"
SCHEMA_VERSION = "0.2.0"

MONSTER_IMAGE_DIR = IMAGE_DIR / "monsters"

INTENT_KINDS: dict[str, str] = {
    "SingleAttackIntent": "SingleAttack",
    "MultiAttackIntent": "MultiAttack",
    "DefendIntent": "Defend",
    "BuffIntent": "Buff",
    "DebuffIntent": "Debuff",
    "StatusIntent": "Status",
    "HealIntent": "Heal",
    "HiddenIntent": "Hidden",
    "StunIntent": "Stun",
    "EscapeIntent": "Escape",
    "SummonIntent": "Summon",
    "SleepIntent": "Sleep",
    "CardDebuffIntent": "CardDebuff",
    "DeathBlowIntent": "DeathBlow",
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class MonsterHp:
    min: int
    max: int
    min_ascension: int | None = None
    max_ascension: int | None = None


@dataclass
class IntentInfo:
    kind: str
    damage: int | None = None
    damage_ascension: int | None = None
    times: int | None = None


@dataclass
class PowerEffect:
    name: str
    amount: int | None = None
    amount_ascension: int | None = None


@dataclass
class StatusCardEffect:
    card: str
    count: int | None = None
    pile: str | None = None


@dataclass
class MoveEffects:
    intents: list[IntentInfo] = field(default_factory=list)
    block: int | None = None
    block_ascension: int | None = None
    powers: list[PowerEffect] = field(default_factory=list)
    status_cards: list[StatusCardEffect] = field(default_factory=list)
    heal: int | None = None


@dataclass
class MonsterMove:
    id: str
    title: str
    effects: MoveEffects | None = None


@dataclass
class MonsterLocalization:
    table: str
    name_key: str


@dataclass
class MonsterAsset:
    kind: str
    path: str
    source: str


@dataclass
class ResolvedMonster:
    name: str
    moves: list[MonsterMove] = field(default_factory=list)


@dataclass
class RawMonsterInfo:
    parser_version: str
    class_name: str
    file: str
    hp: MonsterHp | None
    localization: MonsterLocalization
    assets: list[MonsterAsset] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class MonsterInfo:
    schema_version: str
    id: str
    raw: RawMonsterInfo
    resolved: ResolvedMonster | dict[str, Any]


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------


def is_monster_model(content: str) -> bool:
    return bool(re.search(r":\s*MonsterModel\b", content))


def _parse_hp_property(content: str, prop: str) -> tuple[int, int | None] | None:
    """Return (base_value, ascension_value_or_None) for MinInitialHp or MaxInitialHp."""
    # Simple integer: public override int MinInitialHp => 75;
    simple = re.search(rf"override int {prop}\s*=>\s*(-?\d+)\s*;", content)
    if simple:
        return int(simple.group(1)), None

    # Ascension-scaled: GetValueIfAscension(level, ascension_val, base_val)
    asc = re.search(
        rf"override int {prop}\s*=>\s*AscensionHelper\.GetValueIfAscension\([^,]+,\s*(\d+),\s*(\d+)\)",
        content,
    )
    if asc:
        return int(asc.group(2)), int(asc.group(1))

    return None


def extract_hp(content: str) -> MonsterHp | None:
    min_result = _parse_hp_property(content, "MinInitialHp")
    if min_result is None:
        return None

    # MaxInitialHp => MinInitialHp — uses same value as min
    if re.search(r"override int MaxInitialHp\s*=>\s*MinInitialHp\s*;", content):
        max_result = min_result
    else:
        max_result = _parse_hp_property(content, "MaxInitialHp")

    if max_result is None:
        return None
    return MonsterHp(
        min=min_result[0],
        max=max_result[0],
        min_ascension=min_result[1],
        max_ascension=max_result[1],
    )


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def extract_monster_assets(monster_id: str) -> list[MonsterAsset]:
    assets: list[MonsterAsset] = []
    slug = monster_id.lower()

    path = MONSTER_IMAGE_DIR / f"{slug}.webp"
    if path.exists():
        assets.append(
            MonsterAsset(
                kind="portrait",
                path=str(path.relative_to(LAB_DIR.parent)),
                source="Lab.resources.images.monsters",
            )
        )

    beta_path = MONSTER_IMAGE_DIR / "beta" / f"{slug}.webp"
    if beta_path.exists():
        assets.append(
            MonsterAsset(
                kind="beta_portrait",
                path=str(beta_path.relative_to(LAB_DIR.parent)),
                source="Lab.resources.images.monsters",
            )
        )

    return assets


# ---------------------------------------------------------------------------
# Symbol table and expression resolution
# ---------------------------------------------------------------------------


def _parse_symbol_table(content: str) -> dict[str, tuple[int, int | None]]:
    """Build a map of property/field name → (base_value, ascension_value_or_None)."""
    table: dict[str, tuple[int, int | None]] = {}

    # const int _fieldName = N;
    for m in re.finditer(r"\bconst\s+int\s+(\w+)\s*=\s*(-?\d+)\s*;", content):
        table[m.group(1)] = (int(m.group(2)), None)

    # [modifier] int PropName => N;
    for m in re.finditer(r"\bint\s+(\w+)\s*=>\s*(-?\d+)m?\s*;", content):
        name = m.group(1)
        if name not in ("MinInitialHp", "MaxInitialHp"):
            table[name] = (int(m.group(2)), None)

    # [modifier] int PropName => AscensionHelper.GetValueIfAscension(level, asc, base);
    for m in re.finditer(
        r"\bint\s+(\w+)\s*=>\s*AscensionHelper\.GetValueIfAscension\([^,]+,\s*(-?\d+),\s*(-?\d+)\)",
        content,
    ):
        name = m.group(1)
        if name not in ("MinInitialHp", "MaxInitialHp"):
            table[name] = (int(m.group(3)), int(m.group(2)))

    return table


def _resolve_expr(expr: str, table: dict[str, tuple[int, int | None]]) -> tuple[int | None, int | None]:
    """Try to resolve a C# int expression to (base, ascension)."""
    expr = expr.strip().rstrip("m")

    if re.match(r"^-?\d+$", expr):
        return int(expr), None

    if re.match(r"^\w+$", expr) and expr in table:
        return table[expr]

    # "PropName * something" or "N * something"
    lhs = re.match(r"^(\w+)\s*\*", expr)
    if lhs:
        tok = lhs.group(1)
        if re.match(r"^\d+$", tok):
            return int(tok), None
        if tok in table:
            return table[tok]

    # First numeric literal as last resort
    num = re.search(r"(-?\d+)", expr)
    if num:
        return int(num.group(1)), None

    return None, None


# ---------------------------------------------------------------------------
# Method body extraction
# ---------------------------------------------------------------------------


def _extract_method_body(content: str, method_name: str) -> str | None:
    """Extract a method body using brace counting."""
    m = re.search(
        r"\b" + re.escape(method_name) + r"\s*\(",
        content,
    )
    if not m:
        return None

    start = content.find("{", m.end())
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(content)):
        ch = content[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[start : i + 1]
    return None


# ---------------------------------------------------------------------------
# Move state machine parsing
# ---------------------------------------------------------------------------


def _find_balanced_end(text: str, open_pos: int) -> int:
    """Find the closing paren matching the one at open_pos. Returns index of ')'."""
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def _parse_intent_str(intent_class: str, args_content: str, table: dict[str, tuple[int, int | None]]) -> IntentInfo:
    kind = INTENT_KINDS.get(intent_class, intent_class)
    args_content = args_content.strip()

    if not args_content:
        return IntentInfo(kind=kind)

    # Lambda: () => PropName
    lambda_m = re.match(r"\(\)\s*=>\s*(\w+)", args_content)
    if lambda_m:
        args = [lambda_m.group(1)]
    else:
        args = [a.strip() for a in args_content.split(",")]

    if kind == "SingleAttack" and args:
        val, asc = _resolve_expr(args[0], table)
        return IntentInfo(kind=kind, damage=val, damage_ascension=asc)
    if kind == "MultiAttack" and len(args) >= 2:
        val, asc = _resolve_expr(args[0], table)
        times, _ = _resolve_expr(args[1], table)
        return IntentInfo(kind=kind, damage=val, damage_ascension=asc, times=times)
    if kind == "Status" and args:
        count, _ = _resolve_expr(args[0], table)
        return IntentInfo(kind=kind, times=count)
    if kind == "DeathBlow" and args:
        val, asc = _resolve_expr(args[0], table)
        return IntentInfo(kind=kind, damage=val, damage_ascension=asc)

    return IntentInfo(kind=kind)


_INTENT_RE = re.compile(r"new\s+(\w+Intent)\s*\(")


def _parse_move_states(
    body: str, table: dict[str, tuple[int, int | None]]
) -> list[tuple[str, str, list[IntentInfo]]]:
    """Parse GenerateMoveStateMachine body. Returns (cs_id, handler, intents) tuples."""
    results = []

    for m in re.finditer(r'new MoveState\(\s*"([^"]+)"\s*,\s*(\w+)', body):
        cs_id = m.group(1)
        handler = m.group(2)

        # Find the opening paren of the MoveState(...) call
        call_open = body.rfind("(", m.start(), m.end())
        call_close = _find_balanced_end(body, call_open)

        # Remainder after handler name: ", new Intent1(...), ..."
        remainder = body[m.end() : call_close]

        intents: list[IntentInfo] = []
        pos = 0
        while pos < len(remainder):
            im = _INTENT_RE.search(remainder, pos)
            if not im:
                break
            intent_class = im.group(1)
            paren_open = im.end() - 1
            paren_close = _find_balanced_end(remainder, paren_open)
            args_content = remainder[paren_open + 1 : paren_close]
            intents.append(_parse_intent_str(intent_class, args_content, table))
            pos = paren_close + 1

        results.append((cs_id, handler, intents))

    return results


# ---------------------------------------------------------------------------
# Handler body effect extraction
# ---------------------------------------------------------------------------


def _extract_handler_effects(
    handler_name: str,
    content: str,
    table: dict[str, tuple[int, int | None]],
    intents: list[IntentInfo],
) -> MoveEffects | None:
    body = _extract_method_body(content, handler_name)
    effects = MoveEffects(intents=intents)

    if body:
        # Block: GainBlock(creature, amount, ...)
        bm = re.search(r"GainBlock\([^,]+,\s*([^,)]+)", body)
        if bm:
            val, asc = _resolve_expr(bm.group(1), table)
            effects.block = val
            effects.block_ascension = asc

        # Powers: PowerCmd.Apply<Name>(creature, amount, ...)
        for pm in re.finditer(r"PowerCmd\.Apply<(\w+)>\([^,]+,\s*([^,)]+)", body):
            power_name = re.sub(r"Power$", "", pm.group(1))
            val, asc = _resolve_expr(pm.group(2), table)
            effects.powers.append(PowerEffect(name=power_name, amount=val, amount_ascension=asc))

        # Status cards: CardPileCmd.AddToCombatAndPreview<Card>(targets, PileType.X, count, ...)
        for cm in re.finditer(
            r"AddToCombatAndPreview<(\w+)>\([^,]+,\s*PileType\.(\w+),\s*([^,)]+)",
            body,
        ):
            val, _ = _resolve_expr(cm.group(3), table)
            effects.status_cards.append(StatusCardEffect(card=cm.group(1), count=val, pile=cm.group(2)))

        # Heal: CreatureCmd.Heal(creature, amount)
        hm = re.search(r"CreatureCmd\.Heal\([^,]+,\s*([^,)]+)", body)
        if hm:
            val, _ = _resolve_expr(hm.group(1), table)
            effects.heal = val

    # Return None if no data was extracted
    if (
        not effects.intents
        and effects.block is None
        and not effects.powers
        and not effects.status_cards
        and effects.heal is None
    ):
        return None

    return effects


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def build_resolved_monster(
    monster_id: str,
    content: str,
    localization: dict[str, str],
) -> ResolvedMonster:
    name = localization[f"{monster_id}.name"]

    table = _parse_symbol_table(content)
    state_machine_body = _extract_method_body(content, "GenerateMoveStateMachine")
    cs_moves = _parse_move_states(state_machine_body, table) if state_machine_body else []

    # Map C# ID variants → (handler, intents). Both raw and _MOVE-stripped forms are stored.
    cs_by_id: dict[str, tuple[str, list[IntentInfo]]] = {}
    for cs_id, handler, intents in cs_moves:
        cs_by_id.setdefault(cs_id, (handler, intents))
        stripped = re.sub(r"_MOVE$", "", cs_id)
        cs_by_id.setdefault(stripped, (handler, intents))

    # Case-insensitive lookup table (for loc IDs like "Crash" vs C# "CRASH")
    cs_by_id_upper: dict[str, tuple[str, list[IntentInfo]]] = {
        k.upper(): v for k, v in cs_by_id.items()
    }

    move_prefix = f"{monster_id}.moves."
    moves: list[MonsterMove] = []
    seen: set[str] = set()
    for key in sorted(localization):
        if key.startswith(move_prefix) and key.endswith(".title"):
            move_id = key[len(move_prefix) : -len(".title")]
            if move_id in seen:
                continue
            seen.add(move_id)
            title = localization[key]

            # Match localization move ID to C# handler (try progressively looser forms)
            effects: MoveEffects | None = None
            handler_name: str | None = None
            intents: list[IntentInfo] = []

            if move_id in cs_by_id:
                handler_name, intents = cs_by_id[move_id]
            elif move_id.upper() in cs_by_id_upper:
                handler_name, intents = cs_by_id_upper[move_id.upper()]
            else:
                # Dotted IDs like "TACKLE.WEAKENING_SPORES" → try "TACKLE_WEAKENING_SPORES"
                candidate = move_id.replace(".", "_")
                if candidate in cs_by_id:
                    handler_name, intents = cs_by_id[candidate]
                elif candidate.upper() in cs_by_id_upper:
                    handler_name, intents = cs_by_id_upper[candidate.upper()]

            if handler_name:
                effects = _extract_handler_effects(handler_name, content, table, intents)

            moves.append(MonsterMove(id=move_id, title=title, effects=effects))

    return ResolvedMonster(name=name, moves=moves)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def default_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "monsters.json"


def parse_monster(
    filepath: Path,
    localization: dict[str, str] | None = None,
) -> MonsterInfo | None:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    monster_id = class_name_to_id(class_name)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    name_key = f"{monster_id}.name"

    if localization and name_key not in localization:
        return None

    hp = extract_hp(content)
    assets = extract_monster_assets(monster_id)

    notes: list[str] = []
    if hp is None:
        notes.append("Could not parse HP values from source.")

    resolved: ResolvedMonster | dict[str, Any] = {}
    if localization and name_key in localization:
        resolved = build_resolved_monster(monster_id, content, localization)

    return MonsterInfo(
        schema_version=SCHEMA_VERSION,
        id=monster_id,
        raw=RawMonsterInfo(
            parser_version=PARSER_VERSION,
            class_name=class_name,
            file=display_path,
            hp=hp,
            localization=MonsterLocalization(
                table="monsters",
                name_key=name_key,
            ),
            assets=assets,
            notes=notes,
        ),
        resolved=resolved,
    )


def parse_many(
    monster_dir: Path,
    localization: dict[str, str] | None = None,
) -> list[MonsterInfo]:
    monsters = []
    for path in sorted(monster_dir.glob("*.cs")):
        content = path.read_text(encoding="utf-8")
        if not is_monster_model(content):
            continue
        result = parse_monster(path, localization)
        if result is not None:
            monsters.append(result)
    return monsters


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_monster_output(monster: MonsterInfo, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{monster.id.lower()}.json"
    output_path.write_text(
        json.dumps(to_jsonable(monster), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_many_monsters(monsters: list[MonsterInfo], output_dir: Path) -> list[Path]:
    return [write_monster_output(m, output_dir) for m in monsters]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def prompt_for_version(versions: list[str], default_version: str) -> str:
    print("Available decompiled versions:", file=sys.stderr)
    for index, version in enumerate(versions, start=1):
        default_marker = " (default)" if version == default_version else ""
        print(f"  {index}. {version}{default_marker}", file=sys.stderr)
    response = input(f"Choose a version [default: {default_version}]: ").strip()
    if not response:
        return default_version
    if response.isdigit():
        selected_index = int(response) - 1
        if 0 <= selected_index < len(versions):
            return versions[selected_index]
    if response in versions:
        return response
    raise ValueError(f"Unknown version selection: {response}")


def resolve_monsters_dir(path_arg: str | None, version: str | None) -> tuple[Path, str | None]:
    if path_arg:
        path = Path(path_arg).resolve()
        return path, infer_version_from_path(path)

    available_versions = list_decompiled_versions()
    selected_version = version
    if selected_version is None:
        latest = latest_decompiled_version()
        selected_version = prompt_for_version(available_versions, latest) if sys.stdin.isatty() else latest
    return DECOMPILED_DIR / selected_version / MONSTERS_SUBDIR, selected_version


def default_output_dir(version: str | None) -> Path:
    return LAB_DIR / "data" / version / "monsters" if version else LAB_DIR / "data" / "monsters"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Monster .cs file or monsters directory")
    parser.add_argument("--version", help="Decompiler version, e.g. v0.103.2")
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Localization language (default: {DEFAULT_LANGUAGE})",
    )
    parser.add_argument("--localization", type=Path, help="Path to monsters.json (overrides default)")
    parser.add_argument("--raw-only", action="store_true", help="Skip localization resolution")
    parser.add_argument("--output-dir", type=Path, help="Directory for per-monster JSON output")
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing files")
    args = parser.parse_args()

    input_path, inferred_version = resolve_monsters_dir(args.path, args.version)
    version = args.version or inferred_version
    localization_path = args.localization or default_localization_path(args.language)
    localization = {} if args.raw_only else load_localization(localization_path)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(version)

    if input_path.is_file():
        monster = parse_monster(input_path, localization)
        if monster is None:
            print(f"Skipped (no localization key): {input_path.stem}", file=sys.stderr)
            return
        if args.stdout:
            print(json.dumps(to_jsonable(monster), indent=2, sort_keys=False))
            return
        output_path = write_monster_output(monster, output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        monsters = parse_many(input_path, localization)
        if args.stdout:
            print(json.dumps(to_jsonable(monsters), indent=2, sort_keys=False))
            return
        paths = write_many_monsters(monsters, output_dir)
        elapsed = time.perf_counter() - started_at
        print(f"Wrote {len(paths)} monster files to {output_dir} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
