#!/usr/bin/env python3
"""Recover Slay the Spire 2 resources from the installed PCK."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PCK = (
    Path.home()
    / "Library/Application Support/Steam/steamapps/common/Slay the Spire 2"
    / "SlayTheSpire2.app/Contents/Resources/Slay the Spire 2.pck"
)
DEFAULT_OUT = ROOT_DIR / "unpacked"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recover the local Slay the Spire 2 PCK with Godot RE Tools."
    )
    parser.add_argument(
        "--pck",
        default=os.environ.get("STS2_PCK_PATH", str(DEFAULT_PCK)),
        help="Path to 'Slay the Spire 2.pck'.",
    )
    parser.add_argument(
        "--out",
        default=os.environ.get("STS2_UNPACKED_DIR", str(DEFAULT_OUT)),
        help="Output directory. Defaults to Lab/unpacked.",
    )
    parser.add_argument(
        "--gdretools",
        default=os.environ.get("GDRETOOLS", "gdretools"),
        help="Godot RE Tools CLI path. Defaults to gdretools on PATH.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the output directory before recovering.",
    )
    return parser.parse_args()


def command_exists(command: str) -> bool:
    if "/" in command:
        return Path(command).is_file()
    return shutil.which(command) is not None


def main() -> int:
    args = parse_args()
    pck_path = Path(args.pck).expanduser()
    out_dir = Path(args.out).expanduser()

    if not command_exists(args.gdretools):
        print(f"Godot RE Tools CLI was not found: {args.gdretools}", file=sys.stderr)
        print(
            "Create ~/.bin/gdretools or pass --gdretools PATH.",
            file=sys.stderr,
        )
        return 1

    if not pck_path.is_file():
        print("PCK was not found at:", file=sys.stderr)
        print(f"  {pck_path}", file=sys.stderr)
        print("Pass --pck PATH or set STS2_PCK_PATH.", file=sys.stderr)
        return 1

    if args.clean:
        shutil.rmtree(out_dir, ignore_errors=True)
    elif out_dir.exists() and any(out_dir.iterdir()):
        print("Output directory already exists and is not empty:", file=sys.stderr)
        print(f"  {out_dir}", file=sys.stderr)
        print("Use --clean or choose another directory with --out.", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    print("Recovering Slay the Spire 2 resources:")
    print(f"  PCK: {pck_path}")
    print(f"  Out: {out_dir}")

    subprocess.run(
        [
            args.gdretools,
            "--headless",
            f"--recover={pck_path}",
            f"--output={out_dir}",
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
