#!/usr/bin/env python3
"""Parse decompiled STS2 potion C# into structured JSON.

Conservative approach:
- Only emits facts explicit in the potion source.
- Pool membership is derived from PotionPool class files (and epoch files for
  character-specific pools), not the potion itself.
- Resolves titles, descriptions, and selection_screen_prompt from localization
  as a second pass.
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
    HoverTip,
    IMAGE_DIR,
    LAB_DIR,
    LOCALIZATION_DIR,
    ResolvedText,
    class_name_to_id,
    dynamic_var_type_names,
    extract_tips,
    extract_vars,
    infer_version_from_path,
    latest_decompiled_version,
    list_decompiled_versions,
    load_localization,
    resolve_text,
    source_version,
    to_jsonable,
)


POTIONS_SUBDIR = "MegaCrit.Sts2.Core.Models.Potions"
POTION_POOLS_SUBDIR = "MegaCrit.Sts2.Core.Models.PotionPools"
EPOCHS_SUBDIR = "MegaCrit.Sts2.Core.Timeline.Epochs"
PARSER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"

POTION_IMAGE_DIR = IMAGE_DIR / "potions"

POTION_RARITY_NAME = {
    "Common": "Common",
    "Event": "Event",
    "None": "None",
    "Rare": "Rare",
    "Token": "Token",
    "Uncommon": "Uncommon",
}

POTION_USAGE_NAME = {
    "AnyTime": "AnyTime",
    "Automatic": "Automatic",
    "CombatOnly": "CombatOnly",
}

TARGET_TYPE_NAME = {
    "AllEnemies": "AllEnemies",
    "AnyEnemy": "AnyEnemy",
    "AnyPlayer": "AnyPlayer",
    "Self": "Self",
    "TargetedNoCreature": "TargetedNoCreature",
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class PotionLocalization:
    table: str
    title_key: str
    description_key: str


@dataclass
class PotionAsset:
    kind: str
    path: str
    source: str


@dataclass
class ResolvedPotion:
    title: str
    description: ResolvedText
    selection_screen_prompt: ResolvedText | None = None


@dataclass
class RawPotionInfo:
    parser_version: str
    class_name: str
    file: str
    rarity: str
    usage: str
    target_type: str
    pools: list[str]
    localization: PotionLocalization
    vars: dict[str, int] = field(default_factory=dict)
    tips: list[HoverTip] = field(default_factory=list)
    assets: list[PotionAsset] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class PotionInfo:
    schema_version: str
    id: str
    raw: RawPotionInfo
    resolved: ResolvedPotion | dict[str, Any]


# ---------------------------------------------------------------------------
# Pool map
# ---------------------------------------------------------------------------


def _pool_name_from_class(class_name: str) -> str:
    return re.sub(r"PotionPool$", "", class_name).lower()


def _extract_direct_potions(content: str) -> list[str]:
    """Return relic IDs from direct ModelDb.Potion<ClassName>() calls."""
    return [class_name_to_id(m.group(1)) for m in re.finditer(r"ModelDb\.Potion<(\w+)>\(\)", content)]


def load_potion_pool_map(version: str | None) -> dict[str, list[str]]:
    """Return a map of potion_id → sorted list of pool names."""
    if version is None:
        return {}
    pool_dir = DECOMPILED_DIR / version / POTION_POOLS_SUBDIR
    epochs_dir = DECOMPILED_DIR / version / EPOCHS_SUBDIR
    if not pool_dir.exists():
        raise FileNotFoundError(f"Missing potion pool source directory for {version}: {pool_dir}")

    potion_pools: dict[str, list[str]] = {}

    for path in sorted(pool_dir.glob("*PotionPool.cs")):
        class_name = path.stem
        pool_name = _pool_name_from_class(class_name)
        content = path.read_text(encoding="utf-8")

        potion_ids: list[str] = _extract_direct_potions(content)

        # Character-specific pools delegate to an epoch class: {EpochClass}.Potions
        for epoch_match in re.finditer(r"(\w+Epoch)\.Potions", content):
            epoch_class = epoch_match.group(1)
            epoch_path = epochs_dir / f"{epoch_class}.cs"
            if epoch_path.exists():
                epoch_content = epoch_path.read_text(encoding="utf-8")
                potion_ids.extend(_extract_direct_potions(epoch_content))

        for potion_id in potion_ids:
            potion_pools.setdefault(potion_id, [])
            if pool_name not in potion_pools[potion_id]:
                potion_pools[potion_id].append(pool_name)

    for pools in potion_pools.values():
        pools.sort()

    return potion_pools


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------


def is_potion_model(content: str) -> bool:
    return bool(re.search(r":\s*PotionModel\b", content))


def extract_rarity(content: str) -> str:
    match = re.search(r"PotionRarity\.(\w+)", content)
    if not match:
        raise ValueError("Could not locate PotionRarity property")
    return POTION_RARITY_NAME.get(match.group(1), match.group(1))


def extract_usage(content: str) -> str:
    match = re.search(r"PotionUsage\.(\w+)", content)
    if not match:
        raise ValueError("Could not locate PotionUsage property")
    return POTION_USAGE_NAME.get(match.group(1), match.group(1))


def extract_target_type(content: str) -> str:
    # Some files have a property body rather than an expression; take last match
    matches = list(re.finditer(r"TargetType\.(\w+)", content))
    if not matches:
        raise ValueError("Could not locate TargetType property")
    return TARGET_TYPE_NAME.get(matches[-1].group(1), matches[-1].group(1))


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def potion_image_path(potion_id: str) -> Path:
    return POTION_IMAGE_DIR / f"{potion_id.lower()}.webp"


def extract_potion_assets(potion_id: str) -> list[PotionAsset]:
    assets: list[PotionAsset] = []
    path = potion_image_path(potion_id)
    if path.exists():
        assets.append(
            PotionAsset(
                kind="portrait",
                path=str(path.relative_to(LAB_DIR.parent)),
                source="Lab.resources.images.potions",
            )
        )
    return assets


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def build_resolved_potion(
    potion_id: str,
    vars_by_name: dict[str, int],
    localization: dict[str, str],
) -> ResolvedPotion:
    title_key = f"{potion_id}.title"
    description_key = f"{potion_id}.description"
    missing = [key for key in (title_key, description_key) if key not in localization]
    if missing:
        raise ValueError(f"Missing required localization keys for {potion_id}: {', '.join(missing)}")

    prompt_key = f"{potion_id}.selectionScreenPrompt"
    display_vars: dict[str, Any] = dict(vars_by_name)

    selection_screen_prompt: ResolvedText | None = None
    if prompt_key in localization:
        selection_screen_prompt = resolve_text(localization[prompt_key], display_vars, set(), upgraded=False)

    return ResolvedPotion(
        title=localization[title_key],
        description=resolve_text(localization[description_key], display_vars, set(), upgraded=False),
        selection_screen_prompt=selection_screen_prompt,
    )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def default_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "potions.json"


def parse_potion(
    filepath: Path,
    localization: dict[str, str] | None = None,
    potion_pools: dict[str, list[str]] | None = None,
) -> PotionInfo:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    potion_id = class_name_to_id(class_name)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    potion_pools = potion_pools or {}
    version = source_version(filepath)

    rarity = extract_rarity(content)
    usage = extract_usage(content)
    target_type = extract_target_type(content)
    pools = potion_pools.get(potion_id, [])
    vars_by_name = extract_vars(content, dynamic_var_type_names(version) if version else {})
    tips = extract_tips(content)
    assets = extract_potion_assets(potion_id)

    title_key = f"{potion_id}.title"
    description_key = f"{potion_id}.description"
    notes: list[str] = []
    if localization and description_key not in localization:
        notes.append("Localization keys not found; potion may be deprecated or unreleased.")

    resolved: ResolvedPotion | dict[str, Any] = {}
    if localization and description_key in localization:
        resolved = build_resolved_potion(potion_id, vars_by_name, localization)

    return PotionInfo(
        schema_version=SCHEMA_VERSION,
        id=potion_id,
        raw=RawPotionInfo(
            parser_version=PARSER_VERSION,
            class_name=class_name,
            file=display_path,
            rarity=rarity,
            usage=usage,
            target_type=target_type,
            pools=pools,
            localization=PotionLocalization(
                table="potions",
                title_key=title_key,
                description_key=description_key,
            ),
            vars=vars_by_name,
            tips=tips,
            assets=assets,
            notes=notes,
        ),
        resolved=resolved,
    )


def parse_many(
    potion_dir: Path,
    localization: dict[str, str] | None = None,
    potion_pools: dict[str, list[str]] | None = None,
) -> list[PotionInfo]:
    potions = []
    for path in sorted(potion_dir.glob("*.cs")):
        content = path.read_text(encoding="utf-8")
        if not is_potion_model(content):
            continue
        potions.append(parse_potion(path, localization, potion_pools))
    return potions


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_potion_output(potion: PotionInfo, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{potion.id.lower()}.json"
    output_path.write_text(
        json.dumps(to_jsonable(potion), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_many_potions(potions: list[PotionInfo], output_dir: Path) -> list[Path]:
    return [write_potion_output(potion, output_dir) for potion in potions]


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


def resolve_potions_dir(path_arg: str | None, version: str | None) -> tuple[Path, str | None]:
    if path_arg:
        path = Path(path_arg).resolve()
        return path, infer_version_from_path(path)

    available_versions = list_decompiled_versions()
    selected_version = version
    if selected_version is None:
        latest = latest_decompiled_version()
        selected_version = prompt_for_version(available_versions, latest) if sys.stdin.isatty() else latest
    return DECOMPILED_DIR / selected_version / POTIONS_SUBDIR, selected_version


def default_output_dir(version: str | None) -> Path:
    return LAB_DIR / "data" / version / "potions" if version else LAB_DIR / "data" / "potions"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Potion .cs file or potion directory")
    parser.add_argument("--version", help="Decompiler version, e.g. v0.103.2")
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Localization language (default: {DEFAULT_LANGUAGE})",
    )
    parser.add_argument("--localization", type=Path, help="Path to potions.json (overrides default)")
    parser.add_argument("--raw-only", action="store_true", help="Skip localization resolution")
    parser.add_argument("--output-dir", type=Path, help="Directory for per-potion JSON output")
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing files")
    args = parser.parse_args()

    input_path, inferred_version = resolve_potions_dir(args.path, args.version)
    version = args.version or inferred_version
    localization_path = args.localization or default_localization_path(args.language)
    localization = {} if args.raw_only else load_localization(localization_path)
    potion_pools = load_potion_pool_map(version)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(version)

    if input_path.is_file():
        potion = parse_potion(input_path, localization, potion_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(potion), indent=2, sort_keys=False))
            return
        output_path = write_potion_output(potion, output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        potions = parse_many(input_path, localization, potion_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(potions), indent=2, sort_keys=False))
            return
        paths = write_many_potions(potions, output_dir)
        elapsed = time.perf_counter() - started_at
        print(f"Wrote {len(paths)} potion files to {output_dir} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
