#!/usr/bin/env python3
"""Parse decompiled STS2 monster C# into structured JSON.

Conservative approach:
- Only emits facts explicit in the monster source.
- Move IDs and titles are derived from localization keys, not the C# state
  machine (which uses internal IDs that differ from localization keys).
- Monsters with no name key in localization are skipped (test helpers,
  deprecated entries, non-combat entities).
- HP values capture both base and ascension-scaled variants where present.
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
PARSER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"

MONSTER_IMAGE_DIR = IMAGE_DIR / "monsters"


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
class MonsterMove:
    id: str
    title: str


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
# Resolution
# ---------------------------------------------------------------------------


def build_resolved_monster(
    monster_id: str,
    localization: dict[str, str],
) -> ResolvedMonster:
    name = localization[f"{monster_id}.name"]

    move_prefix = f"{monster_id}.moves."
    moves: list[MonsterMove] = []
    seen: set[str] = set()
    for key in sorted(localization):
        if key.startswith(move_prefix) and key.endswith(".title"):
            move_id = key[len(move_prefix):-len(".title")]
            if move_id not in seen:
                seen.add(move_id)
                moves.append(MonsterMove(id=move_id, title=localization[key]))

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
        resolved = build_resolved_monster(monster_id, localization)

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
