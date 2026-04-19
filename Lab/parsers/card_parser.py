#!/usr/bin/env python3
"""Parse decompiled STS2 card C# into a safer JSON shape.

This parser is intentionally conservative:
- It only emits facts that are explicit in the card source.
- It separates hover-tip references from actual card creation.
- It treats descriptions as localization-derived, not card-source-derived.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
LAB_DIR = SCRIPT_PATH.parent.parent
DECOMPILED_DIR = LAB_DIR / "decompiled"
CARDS_SUBDIR = "MegaCrit.Sts2.Core.Models.Cards"
PARSER_VERSION = "0.1.0"

CARD_TYPE_NAME = {
    "Attack": "Attack",
    "Skill": "Skill",
    "Power": "Power",
    "Status": "Status",
    "Curse": "Curse",
}

CARD_RARITY_NAME = {
    "Basic": "Basic",
    "Common": "Common",
    "Uncommon": "Uncommon",
    "Rare": "Rare",
    "Special": "Special",
    "Token": "Token",
}

TARGET_TYPE_NAME = {
    "Self": "Self",
    "AnyEnemy": "AnyEnemy",
    "AllEnemies": "AllEnemies",
    "NoTarget": "NoTarget",
    "None": "None",
}


@dataclass
class CardRelation:
    kind: str
    target: str
    source: str


@dataclass
class AppliedPower:
    power: str
    target_expr: str
    amount_expr: str


@dataclass
class UpgradeDelta:
    var: str
    delta: int


@dataclass
class LocalizationInfo:
    title_key: str
    description_key: str
    title: str | None = None
    description_raw: str | None = None


@dataclass
class CardInfo:
    parser_version: str
    id: str
    class_name: str
    name: str
    file: str
    cost: int
    type: str
    rarity: str
    target: str
    localization: LocalizationInfo
    vars: dict[str, int] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    upgrades: list[UpgradeDelta] = field(default_factory=list)
    applies_powers: list[AppliedPower] = field(default_factory=list)
    relations: list[CardRelation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def class_name_to_id(class_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()


def load_localization(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_version_key(name: str) -> tuple[int, ...]:
    if not name.startswith("v"):
        return (-1,)
    parts = re.findall(r"\d+", name[1:])
    if not parts:
        return (-1,)
    return tuple(int(part) for part in parts)


def list_decompiled_versions() -> list[str]:
    if not DECOMPILED_DIR.exists():
        return []
    versions = [path.name for path in DECOMPILED_DIR.iterdir() if path.is_dir() and path.name.startswith("v")]
    return sorted(versions, key=parse_version_key)


def latest_decompiled_version() -> str:
    versions = list_decompiled_versions()
    if not versions:
        raise ValueError(f"No decompiled versions found under {DECOMPILED_DIR}")
    return versions[-1]


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


def resolve_cards_dir(path_arg: str | None, version: str | None) -> tuple[Path, str | None]:
    if path_arg:
        path = Path(path_arg).resolve()
        inferred_version = infer_version_from_path(path)
        if path.is_dir():
            return path, inferred_version
        return path, inferred_version

    available_versions = list_decompiled_versions()
    selected_version = version
    if selected_version is None:
        latest = latest_decompiled_version()
        if sys.stdin.isatty():
            selected_version = prompt_for_version(available_versions, latest)
        else:
            selected_version = latest
    cards_dir = DECOMPILED_DIR / selected_version / CARDS_SUBDIR
    return cards_dir, selected_version


def infer_version_from_path(path: Path) -> str | None:
    parts = path.parts
    for index, part in enumerate(parts):
        if part == "decompiled" and index + 1 < len(parts):
            candidate = parts[index + 1]
            if candidate.startswith("v"):
                return candidate
    return None


def default_output_dir(version: str | None) -> Path:
    if version:
        return LAB_DIR / "data" / version / "cards"
    return LAB_DIR / "data" / "cards"


def extract_constructor_fields(content: str) -> tuple[int, str, str, str]:
    match = re.search(
        r":\s*base\(\s*(-?\d+)\s*,\s*CardType\.(\w+)\s*,\s*CardRarity\.(\w+)\s*,\s*TargetType\.(\w+)",
        content,
    )
    if not match:
        raise ValueError("Could not locate card base constructor")
    cost = int(match.group(1))
    card_type = CARD_TYPE_NAME.get(match.group(2), match.group(2))
    rarity = CARD_RARITY_NAME.get(match.group(3), match.group(3))
    target = TARGET_TYPE_NAME.get(match.group(4), match.group(4))
    return cost, card_type, rarity, target


def extract_vars(content: str) -> dict[str, int]:
    vars_found: dict[str, int] = {}

    simple_var_patterns = [
        (r"new DamageVar\((\d+)m", "Damage"),
        (r"new BlockVar\((\d+)m", "Block"),
        (r"new CardsVar\((\d+)\)", "Cards"),
        (r"new EnergyVar\((\d+)\)", "Energy"),
        (r"new HpLossVar\((\d+)m", "HpLoss"),
    ]
    for pattern, var_name in simple_var_patterns:
        for match in re.finditer(pattern, content):
            vars_found[var_name] = int(match.group(1))

    for match in re.finditer(r'new DynamicVar\("(\w+)"\s*,\s*(\d+)m\)', content):
        vars_found[match.group(1)] = int(match.group(2))

    for match in re.finditer(r"new PowerVar<(\w+)>\((\d+)m\)", content):
        power_name = match.group(1)
        base_name = power_name[:-5] if power_name.endswith("Power") else power_name
        value = int(match.group(2))
        vars_found[power_name] = value
        vars_found.setdefault(base_name, value)

    return vars_found


def extract_keywords(content: str) -> list[str]:
    found: list[str] = []
    keyword_names = [
        "Exhaust",
        "Innate",
        "Ethereal",
        "Retain",
        "Unplayable",
        "Sly",
        "Eternal",
    ]
    for keyword in keyword_names:
        if re.search(rf"CardKeyword\.{keyword}", content):
            found.append(keyword)
    for keyword, pattern in [
        ("Ethereal", r"IsEthereal\s*=>\s*true"),
        ("Innate", r"IsInnate\s*=>\s*true"),
        ("Retain", r"IsRetain(?:able)?\s*=>\s*true"),
        ("Unplayable", r"IsUnplayable\s*=>\s*true"),
    ]:
        if keyword not in found and re.search(pattern, content):
            found.append(keyword)
    return found


def extract_tags(content: str) -> list[str]:
    tags: list[str] = []
    for tag in ("Strike", "Defend", "Minion", "OstyAttack", "Shiv"):
        if re.search(rf"CardTag\.{tag}", content):
            tags.append(tag)
    return tags


def extract_upgrades(content: str) -> list[UpgradeDelta]:
    upgrades: dict[str, int] = {}

    for match in re.finditer(r"(?<!\w)(\w+)\.UpgradeValueBy\((-?\d+)m\)", content):
        upgrades[match.group(1)] = int(match.group(2))

    for match in re.finditer(r'\["(\w+)"\]\.UpgradeValueBy\((-?\d+)m\)', content):
        upgrades.setdefault(match.group(1), int(match.group(2)))

    return [UpgradeDelta(var=var_name, delta=delta) for var_name, delta in sorted(upgrades.items())]


def extract_applied_powers(content: str) -> list[AppliedPower]:
    applied: list[AppliedPower] = []
    for match in re.finditer(
        r"PowerCmd\.Apply<(\w+)>\(([^,]+),\s*([^,]+),\s*[^,]+,\s*this\)",
        content,
    ):
        power_name = match.group(1)
        applied.append(
            AppliedPower(
                power=power_name[:-5] if power_name.endswith("Power") else power_name,
                target_expr=match.group(2).strip(),
                amount_expr=match.group(3).strip(),
            )
        )
    return applied


def extract_relations(content: str) -> list[CardRelation]:
    relations: list[CardRelation] = []

    for match in re.finditer(r"HoverTipFactory\.FromCard(?:WithCardHoverTips)?<(\w+)>", content):
        relations.append(CardRelation(kind="hover_tip_card", target=class_name_to_id(match.group(1)), source="HoverTipFactory.FromCard"))

    for match in re.finditer(r"HoverTipFactory\.FromPower<(\w+)>", content):
        relations.append(CardRelation(kind="hover_tip_power", target=match.group(1), source="HoverTipFactory.FromPower"))

    for match in re.finditer(r"HoverTipFactory\.FromOrb<(\w+)>", content):
        relations.append(CardRelation(kind="hover_tip_orb", target=match.group(1), source="HoverTipFactory.FromOrb"))

    for match in re.finditer(r"CreateCard<(\w+)>", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="CreateCard"))

    for match in re.finditer(r"(\w+)\.CreateInHand\(", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="CreateInHand"))

    for match in re.finditer(r"AddToCombatAndPreview<(\w+)>", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="AddToCombatAndPreview"))

    deduped: list[CardRelation] = []
    seen: set[tuple[str, str, str]] = set()
    for relation in relations:
        key = (relation.kind, relation.target, relation.source)
        if key not in seen:
            seen.add(key)
            deduped.append(relation)
    return deduped


def parse_card(filepath: Path, localization: dict[str, str] | None = None) -> CardInfo:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    card_id = class_name_to_id(class_name)
    cost, card_type, rarity, target = extract_constructor_fields(content)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    title_key = f"{card_id}.title"
    description_key = f"{card_id}.description"

    notes: list[str] = []
    if description_key not in localization:
        notes.append("Description is not present in the C# file; supply localization data to populate it.")

    return CardInfo(
        parser_version=PARSER_VERSION,
        id=card_id,
        class_name=class_name,
        name=localization.get(title_key, class_name),
        file=display_path,
        cost=cost,
        type=card_type,
        rarity=rarity,
        target=target,
        localization=LocalizationInfo(
            title_key=title_key,
            description_key=description_key,
            title=localization.get(title_key),
            description_raw=localization.get(description_key),
        ),
        vars=extract_vars(content),
        keywords=extract_keywords(content),
        tags=extract_tags(content),
        upgrades=extract_upgrades(content),
        applies_powers=extract_applied_powers(content),
        relations=extract_relations(content),
        notes=notes,
    )


def parse_many(card_dir: Path, localization: dict[str, str] | None = None) -> list[CardInfo]:
    return [parse_card(path, localization) for path in sorted(card_dir.glob("*.cs"))]


def to_jsonable(value: Any) -> Any:
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_jsonable(val) for key, val in asdict(value).items()}
    return value


def write_card_output(card: CardInfo, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{card.id.lower()}.json"
    output_path.write_text(
        json.dumps(to_jsonable(card), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_many_cards(cards: list[CardInfo], output_dir: Path) -> list[Path]:
    return [write_card_output(card, output_dir) for card in cards]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Card .cs file or card directory")
    parser.add_argument("--version", help="Decompiler version under Lab/decompiled/, for example v0.103.2")
    parser.add_argument("--localization", type=Path, help="Optional JSON map of localization keys to strings")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for per-card JSON output",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing per-card files",
    )
    args = parser.parse_args()

    input_path, inferred_version = resolve_cards_dir(args.path, args.version)
    localization = load_localization(args.localization)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(args.version or inferred_version)

    if input_path.is_file():
        card = parse_card(input_path, localization)
        if args.stdout:
            print(json.dumps(to_jsonable(card), indent=2, sort_keys=False))
            return
        output_path = write_card_output(card, output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        cards = parse_many(input_path, localization)
        if args.stdout:
            print(json.dumps(to_jsonable(cards), indent=2, sort_keys=False))
            return
        paths = write_many_cards(cards, output_dir)
        elapsed_seconds = time.perf_counter() - started_at
        print(
            f"Wrote {len(paths)} card files to {output_dir} "
            f"in {elapsed_seconds:.3f}s"
        )


if __name__ == "__main__":
    main()
