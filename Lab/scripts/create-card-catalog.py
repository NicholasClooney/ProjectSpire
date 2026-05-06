#!/usr/bin/env python3
"""Create a static serving catalog for Neow's Cafe card data."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = LAB_ROOT.parent
DEFAULT_VERSION = "v0.103.2"
DEFAULT_OUT_ROOT = LAB_ROOT / "catalog"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a static, symlink-backed card catalog for Neow's Cafe."
    )
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help=f"Card data version. Defaults to {DEFAULT_VERSION}.",
    )
    parser.add_argument(
        "--cards",
        help="Source card JSON directory. Defaults to Lab/data/<version>/cards.",
    )
    parser.add_argument(
        "--portraits",
        default=str(LAB_ROOT / "resources/images/packed/card_portraits"),
        help="Source card portrait directory.",
    )
    parser.add_argument(
        "--out-root",
        default=str(DEFAULT_OUT_ROOT),
        help="Catalog output root. Defaults to Lab/catalog.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the versioned catalog directory before generating.",
    )
    return parser.parse_args()


def resolve_path(path: str | os.PathLike[str]) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def catalog_symlink(source: Path, link: Path) -> str:
    return os.path.relpath(source, start=link.parent)


def replace_symlink(source: Path, link: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        if link.is_dir() and not link.is_symlink():
            shutil.rmtree(link)
        else:
            link.unlink()
    link.symlink_to(catalog_symlink(source, link))


def read_card(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Card JSON must be an object: {path}")
    return loaded


def first_portrait_path(card: dict[str, Any], portrait_root: Path) -> str | None:
    for asset in card.get("raw", {}).get("assets", []):
        if asset.get("kind") != "portrait":
            continue
        raw_path = asset.get("path")
        if not raw_path:
            continue
        asset_path = resolve_path(raw_path).resolve()
        try:
            relative = asset_path.relative_to(portrait_root)
        except ValueError:
            return asset_path.as_posix()
        return f"images/card_portraits/{relative.as_posix()}"
    return None


def energy_cost(card: dict[str, Any]) -> dict[str, Any]:
    raw = card.get("raw", {})
    cost = raw.get("energy_cost")
    if isinstance(cost, dict) and isinstance(cost.get("kind"), str):
        result: dict[str, Any] = {"kind": cost["kind"].lower()}
        if "value" in cost:
            result["value"] = cost["value"]
        return result
    if isinstance(raw.get("cost"), int):
        return {"kind": "int", "value": raw["cost"]}
    return {"kind": "unknown"}


def card_summary(path: Path, card: dict[str, Any], portrait_root: Path) -> dict[str, Any]:
    raw = card.get("raw", {})
    base = card.get("resolved", {}).get("base", {})
    description = base.get("description", {})
    plain_description = description.get("plain") if isinstance(description, dict) else None

    return {
        "id": card["id"],
        "slug": path.stem,
        "title": base.get("title", card["id"]),
        "description": plain_description or "",
        "energyCost": energy_cost(card),
        "type": str(raw.get("type", "")).lower(),
        "rarity": str(raw.get("rarity", "")).lower(),
        "pool": str(raw.get("card_pool", "")).lower(),
        "portraitPath": first_portrait_path(card, portrait_root),
        "detailPath": f"cards/{path.name}",
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    version = args.version
    cards_root = resolve_path(args.cards or LAB_ROOT / f"data/{version}/cards").resolve()
    portrait_root = resolve_path(args.portraits).resolve()
    out_root = resolve_path(args.out_root).resolve()
    catalog_root = out_root / version

    if not cards_root.is_dir():
        print("Card source directory was not found:", file=sys.stderr)
        print(f"  {cards_root}", file=sys.stderr)
        return 1
    if not portrait_root.is_dir():
        print("Portrait source directory was not found:", file=sys.stderr)
        print(f"  {portrait_root}", file=sys.stderr)
        return 1

    if args.clean:
        shutil.rmtree(catalog_root, ignore_errors=True)
    catalog_root.mkdir(parents=True, exist_ok=True)

    card_paths = sorted(cards_root.glob("*.json"))
    cards = [card_summary(path, read_card(path), portrait_root) for path in card_paths]

    cards_index = {
        "schemaVersion": "neows-cafe-card-catalog.v1",
        "gameVersion": version,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cards": cards,
    }

    index_path = catalog_root / "cards.index.json"
    write_json(index_path, cards_index)

    replace_symlink(cards_root, catalog_root / "cards")
    replace_symlink(portrait_root, catalog_root / "images/card_portraits")

    manifest = {
        "schemaVersion": "neows-cafe-catalog-manifest.v1",
        "gameVersion": version,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cardsIndexPath": "cards.index.json",
        "cardCount": len(cards),
        "assetBasePath": "images/",
        "locales": ["eng"],
        "checksums": {
            "cards.index.json": f"sha256:{sha256_file(index_path)}",
        },
        "sources": {
            "cards": cards_root.relative_to(REPO_ROOT).as_posix(),
            "cardPortraits": portrait_root.relative_to(REPO_ROOT).as_posix(),
        },
    }
    write_json(catalog_root / "manifest.json", manifest)

    print(f"Generated {len(cards)} card summaries")
    print(f"Catalog: {catalog_root}")
    print(f"Manifest: {catalog_root / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
