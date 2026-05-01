#!/usr/bin/env python3
"""Extract a tracked subset of recovered Slay the Spire 2 resources."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - only hit on machines without PyYAML.
    yaml = None


ROOT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT_DIR.parent
DEFAULT_ALLOWLIST = ROOT_DIR / "resources.allowlist.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract a small tracked resource subset from recovered STS2 files."
    )
    parser.add_argument(
        "--source",
        help="Recovered resource source. Defaults to source_root in allowlist.",
    )
    parser.add_argument(
        "--out",
        help="Output directory. Defaults to output_root in allowlist.",
    )
    parser.add_argument(
        "--allowlist",
        default=str(DEFAULT_ALLOWLIST),
        help="YAML allowlist. Defaults to Lab/resources.allowlist.yaml.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the output directory before extracting.",
    )
    return parser.parse_args()


def resolve_repo_path(path: str | os.PathLike[str]) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def load_allowlist(path: Path) -> dict[str, Any]:
    if yaml is None:
        print("PyYAML is required to read the resource allowlist.", file=sys.stderr)
        print("Install it with: python3 -m pip install PyYAML", file=sys.stderr)
        raise SystemExit(1)
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Allowlist must be a mapping: {path}")
    return loaded


def is_excluded(relative_path: Path, patterns: list[str]) -> bool:
    path_text = relative_path.as_posix()
    basename = relative_path.name
    return any(fnmatch(path_text, pattern) or fnmatch(basename, pattern) for pattern in patterns)


def iter_included_files(root: Path, includes: list[str], excludes: list[str]) -> list[Path]:
    files: dict[Path, None] = {}
    for pattern in includes:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if is_excluded(relative, excludes):
                continue
            files[path] = None
    return list(files.keys())


def clone_copy(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["cp", "-c", str(source), str(output)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        return
    shutil.copy2(source, output)


def convert_webp(source: Path, output: Path, quality: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["cwebp", "-quiet", "-q", str(quality), str(source), "-o", str(output)],
        check=True,
    )


def main() -> int:
    args = parse_args()
    allowlist_path = Path(args.allowlist).expanduser()
    if not allowlist_path.is_absolute():
        allowlist_path = Path.cwd() / allowlist_path
    if not allowlist_path.is_file():
        print("Allowlist was not found at:", file=sys.stderr)
        print(f"  {allowlist_path}", file=sys.stderr)
        return 1

    if shutil.which("cwebp") is None:
        print("cwebp was not found on PATH.", file=sys.stderr)
        print("Install WebP tools before extracting image resources.", file=sys.stderr)
        return 1

    config = load_allowlist(allowlist_path)
    source_root = resolve_repo_path(args.source or config["source_root"]).resolve()
    output_root = resolve_repo_path(args.out or config["output_root"]).resolve()

    if not source_root.is_dir():
        print("Source directory was not found:", file=sys.stderr)
        print(f"  {source_root}", file=sys.stderr)
        return 1

    if args.clean:
        shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "version": 1,
        "source_root": str(source_root),
        "output_root": str(output_root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": [],
    }

    for entry in config.get("entries", []):
        name = entry["name"]
        from_root = source_root / entry["from"]
        to_root = output_root / entry["to"]
        includes = entry.get("include", [])
        excludes = entry.get("exclude", [])
        transform = entry["transform"]

        if not from_root.is_dir():
            print(f"Skipping {name}: source directory was not found: {from_root}", file=sys.stderr)
            continue

        for source in iter_included_files(from_root, includes, excludes):
            relative = source.relative_to(from_root)

            if transform == "copy":
                output = to_root / relative
                clone_copy(source, output)
                manifest["entries"].append(
                    {
                        "entry": name,
                        "transform": transform,
                        "source": source.relative_to(source_root).as_posix(),
                        "output": output.relative_to(output_root).as_posix(),
                        "bytes": output.stat().st_size,
                    }
                )
            elif transform == "webp-q85":
                if source.suffix.lower() != ".png":
                    print(f"Skipping non-PNG for webp-q85: {source}", file=sys.stderr)
                    continue
                output = to_root / relative.with_suffix(".webp")
                convert_webp(source, output, quality=85)
                source_bytes = source.stat().st_size
                output_bytes = output.stat().st_size
                manifest["entries"].append(
                    {
                        "entry": name,
                        "transform": transform,
                        "source": source.relative_to(source_root).as_posix(),
                        "output": output.relative_to(output_root).as_posix(),
                        "source_bytes": source_bytes,
                        "output_bytes": output_bytes,
                        "quality": 85,
                        "ratio": round(output_bytes / source_bytes, 4),
                    }
                )
            else:
                print(f"Unknown transform for {name}: {transform}", file=sys.stderr)
                return 1

    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Extracted {len(manifest['entries'])} files")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
