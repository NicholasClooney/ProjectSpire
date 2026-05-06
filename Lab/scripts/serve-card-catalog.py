#!/usr/bin/env python3
"""Serve the generated Neow's Cafe card catalog for local development."""

from __future__ import annotations

import argparse
import functools
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_DIR = LAB_ROOT / "catalog"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_VERSION = "v0.103.2"
CACHEABLE_EXTENSIONS = {
    ".css",
    ".gif",
    ".jpeg",
    ".jpg",
    ".js",
    # ".json",
    ".png",
    ".svg",
    ".webp",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the generated card catalog with local-dev cache headers."
    )
    parser.add_argument(
        "--catalog-dir",
        default=os.environ.get("CATALOG_DIR", str(DEFAULT_CATALOG_DIR)),
        help="Catalog root directory. Defaults to Lab/catalog.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", DEFAULT_HOST),
        help=f"Bind host. Defaults to {DEFAULT_HOST}.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", DEFAULT_PORT)),
        help=f"Bind port. Defaults to {DEFAULT_PORT}.",
    )
    parser.add_argument(
        "--version",
        default=os.environ.get("VERSION", DEFAULT_VERSION),
        help=f"Catalog version to validate. Defaults to {DEFAULT_VERSION}.",
    )
    return parser.parse_args()


class CardCatalogHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        if path_extension(self.path) in CACHEABLE_EXTENSIONS:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        super().end_headers()


def path_extension(path: str) -> str:
    path = path.split("?", 1)[0].split("#", 1)[0]
    dot = path.rfind(".")
    if dot == -1:
        return ""
    return path[dot:].lower()


def main() -> int:
    args = parse_args()
    catalog_dir = Path(args.catalog_dir).expanduser().resolve()
    version_dir = catalog_dir / args.version

    if not version_dir.is_dir():
        print(f"Catalog was not found at: {version_dir}", file=sys.stderr)
        print("Generate it first with: Lab/scripts/create-card-catalog.py --clean", file=sys.stderr)
        return 1

    print("Serving card catalog:")
    print(f"  Root: {catalog_dir}")
    print(f"  URL:  http://{args.host}:{args.port}/{args.version}/manifest.json")

    handler = functools.partial(CardCatalogHandler, directory=str(catalog_dir))
    server = ThreadingHTTPServer((args.host, args.port), handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
