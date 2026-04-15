#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_DLL="$HOME/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64/sts2.dll"
DEFAULT_OUT_DIR="$ROOT_DIR/decompiled"

DLL_PATH="${STS2_DLL_PATH:-$DEFAULT_DLL}"
OUT_DIR="${STS2_DECOMPILED_DIR:-$DEFAULT_OUT_DIR}"
CLEAN=0

usage() {
  cat <<'USAGE'
Usage: scripts/decompile-sts2.sh [options]

Decompile the local Slay the Spire 2 sts2.dll with ilspycmd.

Options:
  --dll PATH     Path to sts2.dll. Defaults to the Steam macOS ARM64 install path.
  --out DIR      Output directory. Defaults to ./decompiled.
  --clean        Remove ./decompiled before decompiling.
  -h, --help     Show this help.

Environment overrides:
  STS2_DLL_PATH          Alternative sts2.dll path.
  STS2_DECOMPILED_DIR   Alternative output directory.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dll)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Missing value for --dll" >&2
        exit 2
      fi
      DLL_PATH="$1"
      ;;
    --out)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Missing value for --out" >&2
        exit 2
      fi
      OUT_DIR="$1"
      ;;
    --clean)
      CLEAN=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if ! command -v ilspycmd >/dev/null 2>&1; then
  echo "ilspycmd was not found on PATH." >&2
  echo "Install it with: dotnet tool install --global ilspycmd" >&2
  echo "Then make sure ~/.dotnet/tools is on PATH." >&2
  exit 1
fi

if [[ ! -f "$DLL_PATH" ]]; then
  echo "sts2.dll was not found at:" >&2
  echo "  $DLL_PATH" >&2
  echo "Pass --dll PATH or set STS2_DLL_PATH if your Steam library is elsewhere." >&2
  exit 1
fi

if [[ "$CLEAN" -eq 1 ]]; then
  if [[ "$OUT_DIR" != "$DEFAULT_OUT_DIR" ]]; then
    echo "Refusing --clean for a custom output directory:" >&2
    echo "  $OUT_DIR" >&2
    echo "Remove that directory manually, or use --clean with the default ./decompiled output." >&2
    exit 1
  fi
  rm -rf "$OUT_DIR"
elif [[ -d "$OUT_DIR" ]] && [[ -n "$(find "$OUT_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "Output directory already exists and is not empty:" >&2
  echo "  $OUT_DIR" >&2
  echo "Use --clean to regenerate ./decompiled, or choose another directory with --out." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "Decompiling:"
echo "  DLL: $DLL_PATH"
echo "  Out: $OUT_DIR"

ilspycmd -p -o "$OUT_DIR" "$DLL_PATH"
