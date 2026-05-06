#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CATALOG_DIR="${CATALOG_DIR:-"$ROOT_DIR/catalog"}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"
VERSION="${VERSION:-v0.103.2}"

if [[ ! -d "$CATALOG_DIR/$VERSION" ]]; then
  echo "Catalog was not found at: $CATALOG_DIR/$VERSION" >&2
  echo "Generate it first with: Lab/scripts/create-card-catalog.py --clean" >&2
  exit 1
fi

echo "Serving card catalog:"
echo "  Root: $CATALOG_DIR"
echo "  URL:  http://$HOST:$PORT/$VERSION/manifest.json"

exec python3 -m http.server "$PORT" --bind "$HOST" --directory "$CATALOG_DIR"
