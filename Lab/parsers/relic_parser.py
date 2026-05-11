#!/usr/bin/env python3
"""Parse decompiled STS2 relic C# into structured JSON.

Conservative approach:
- Only emits facts explicit in the relic source.
- Pool membership is derived from RelicPool class files, not the relic itself.
- Resolves titles, descriptions, and flavor from localization as a second pass.
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


RELICS_SUBDIR = "MegaCrit.Sts2.Core.Models.Relics"
RELIC_POOLS_SUBDIR = "MegaCrit.Sts2.Core.Models.RelicPools"
PARSER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"

RELIC_IMAGE_DIR = IMAGE_DIR / "relics"

RELIC_RARITY_NAME = {
    "Ancient": "Ancient",
    "Common": "Common",
    "Event": "Event",
    "None": "None",
    "Rare": "Rare",
    "Shop": "Shop",
    "Starter": "Starter",
    "Uncommon": "Uncommon",
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class RelicLocalization:
    table: str
    title_key: str
    description_key: str


@dataclass
class RelicAsset:
    kind: str
    path: str
    source: str


@dataclass
class ResolvedRelic:
    title: str
    description: ResolvedText
    flavor: ResolvedText | None = None
    event_description: ResolvedText | None = None


@dataclass
class RawRelicInfo:
    parser_version: str
    class_name: str
    file: str
    rarity: str
    pools: list[str]
    localization: RelicLocalization
    vars: dict[str, int] = field(default_factory=dict)
    tips: list[HoverTip] = field(default_factory=list)
    assets: list[RelicAsset] = field(default_factory=list)
    has_pickup_effect: bool | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class RelicInfo:
    schema_version: str
    id: str
    raw: RawRelicInfo
    resolved: ResolvedRelic | dict[str, Any]


# ---------------------------------------------------------------------------
# Pool map
# ---------------------------------------------------------------------------


def _pool_name_from_class(class_name: str) -> str:
    return re.sub(r"RelicPool$", "", class_name).lower()


def load_relic_pool_map(version: str | None) -> dict[str, list[str]]:
    """Return a map of relic_id → sorted list of pool names."""
    if version is None:
        return {}
    pool_dir = DECOMPILED_DIR / version / RELIC_POOLS_SUBDIR
    if not pool_dir.exists():
        raise FileNotFoundError(f"Missing relic pool source directory for {version}: {pool_dir}")

    relic_pools: dict[str, list[str]] = {}
    for path in sorted(pool_dir.glob("*RelicPool.cs")):
        class_name = path.stem
        pool_name = _pool_name_from_class(class_name)
        content = path.read_text(encoding="utf-8")
        for match in re.finditer(r"ModelDb\.Relic<(\w+)>\(\)", content):
            relic_id = class_name_to_id(match.group(1))
            relic_pools.setdefault(relic_id, [])
            if pool_name not in relic_pools[relic_id]:
                relic_pools[relic_id].append(pool_name)

    for pools in relic_pools.values():
        pools.sort()

    return relic_pools


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------


def is_relic_model(content: str) -> bool:
    return bool(re.search(r":\s*RelicModel\b", content))


def extract_rarity(content: str) -> str:
    match = re.search(r"RelicRarity\.(\w+)", content)
    if not match:
        raise ValueError("Could not locate RelicRarity property")
    return RELIC_RARITY_NAME.get(match.group(1), match.group(1))


def extract_has_pickup_effect(content: str) -> bool | None:
    return True if re.search(r"HasUponPickupEffect\s*=>\s*true", content) else None


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def relic_image_path(relic_id: str, is_beta: bool) -> Path:
    slug = relic_id.lower()
    if is_beta:
        return RELIC_IMAGE_DIR / "beta" / f"{slug}.webp"
    return RELIC_IMAGE_DIR / f"{slug}.webp"


def extract_relic_assets(relic_id: str) -> list[RelicAsset]:
    assets: list[RelicAsset] = []
    for kind, is_beta in (("portrait", False), ("beta_portrait", True)):
        path = relic_image_path(relic_id, is_beta)
        if path.exists():
            assets.append(
                RelicAsset(
                    kind=kind,
                    path=str(path.relative_to(LAB_DIR.parent)),
                    source="Lab.resources.images.relics",
                )
            )
    return assets


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def build_resolved_relic(
    relic_id: str,
    vars_by_name: dict[str, int],
    localization: dict[str, str],
) -> ResolvedRelic:
    title_key = f"{relic_id}.title"
    description_key = f"{relic_id}.description"
    missing = [key for key in (title_key, description_key) if key not in localization]
    if missing:
        raise ValueError(f"Missing required localization keys for {relic_id}: {', '.join(missing)}")

    flavor_key = f"{relic_id}.flavor"
    event_description_key = f"{relic_id}.eventDescription"

    display_vars: dict[str, Any] = dict(vars_by_name)

    flavor: ResolvedText | None = None
    if flavor_key in localization:
        flavor = resolve_text(localization[flavor_key], display_vars, set(), upgraded=False)

    event_description: ResolvedText | None = None
    if event_description_key in localization:
        event_description = resolve_text(localization[event_description_key], display_vars, set(), upgraded=False)

    return ResolvedRelic(
        title=localization[title_key],
        description=resolve_text(localization[description_key], display_vars, set(), upgraded=False),
        flavor=flavor,
        event_description=event_description,
    )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def default_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "relics.json"


def parse_relic(
    filepath: Path,
    localization: dict[str, str] | None = None,
    relic_pools: dict[str, list[str]] | None = None,
) -> RelicInfo:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    relic_id = class_name_to_id(class_name)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    relic_pools = relic_pools or {}
    version = source_version(filepath)

    rarity = extract_rarity(content)
    pools = relic_pools.get(relic_id, [])
    vars_by_name = extract_vars(content, dynamic_var_type_names(version) if version else {})
    tips = extract_tips(content)
    assets = extract_relic_assets(relic_id)
    has_pickup_effect = extract_has_pickup_effect(content)

    title_key = f"{relic_id}.title"
    description_key = f"{relic_id}.description"
    notes: list[str] = []
    if localization and description_key not in localization:
        notes.append("Localization keys not found; relic may be deprecated or unreleased.")

    resolved: ResolvedRelic | dict[str, Any] = {}
    if localization and description_key in localization:
        resolved = build_resolved_relic(relic_id, vars_by_name, localization)

    return RelicInfo(
        schema_version=SCHEMA_VERSION,
        id=relic_id,
        raw=RawRelicInfo(
            parser_version=PARSER_VERSION,
            class_name=class_name,
            file=display_path,
            rarity=rarity,
            pools=pools,
            localization=RelicLocalization(
                table="relics",
                title_key=title_key,
                description_key=description_key,
            ),
            vars=vars_by_name,
            tips=tips,
            assets=assets,
            has_pickup_effect=has_pickup_effect,
            notes=notes,
        ),
        resolved=resolved,
    )


def parse_many(
    relic_dir: Path,
    localization: dict[str, str] | None = None,
    relic_pools: dict[str, list[str]] | None = None,
) -> list[RelicInfo]:
    relics = []
    for path in sorted(relic_dir.glob("*.cs")):
        content = path.read_text(encoding="utf-8")
        if not is_relic_model(content):
            continue
        relics.append(parse_relic(path, localization, relic_pools))
    return relics


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_relic_output(relic: RelicInfo, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{relic.id.lower()}.json"
    output_path.write_text(
        json.dumps(to_jsonable(relic), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_many_relics(relics: list[RelicInfo], output_dir: Path) -> list[Path]:
    return [write_relic_output(relic, output_dir) for relic in relics]


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


def resolve_relics_dir(path_arg: str | None, version: str | None) -> tuple[Path, str | None]:
    if path_arg:
        path = Path(path_arg).resolve()
        return path, infer_version_from_path(path)

    available_versions = list_decompiled_versions()
    selected_version = version
    if selected_version is None:
        latest = latest_decompiled_version()
        selected_version = prompt_for_version(available_versions, latest) if sys.stdin.isatty() else latest
    return DECOMPILED_DIR / selected_version / RELICS_SUBDIR, selected_version


def default_output_dir(version: str | None) -> Path:
    return LAB_DIR / "data" / version / "relics" if version else LAB_DIR / "data" / "relics"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Relic .cs file or relic directory")
    parser.add_argument("--version", help="Decompiler version, e.g. v0.103.2")
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Localization language (default: {DEFAULT_LANGUAGE})",
    )
    parser.add_argument("--localization", type=Path, help="Path to relics.json (overrides default)")
    parser.add_argument("--raw-only", action="store_true", help="Skip localization resolution")
    parser.add_argument("--output-dir", type=Path, help="Directory for per-relic JSON output")
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing files")
    args = parser.parse_args()

    input_path, inferred_version = resolve_relics_dir(args.path, args.version)
    version = args.version or inferred_version
    localization_path = args.localization or default_localization_path(args.language)
    localization = {} if args.raw_only else load_localization(localization_path)
    relic_pools = load_relic_pool_map(version)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(version)

    if input_path.is_file():
        relic = parse_relic(input_path, localization, relic_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(relic), indent=2, sort_keys=False))
            return
        output_path = write_relic_output(relic, output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        relics = parse_many(input_path, localization, relic_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(relics), indent=2, sort_keys=False))
            return
        paths = write_many_relics(relics, output_dir)
        elapsed = time.perf_counter() - started_at
        print(f"Wrote {len(paths)} relic files to {output_dir} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
