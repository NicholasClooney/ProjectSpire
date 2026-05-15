#!/usr/bin/env python3
"""Serve the generated Neow's Cafe card catalog for local development."""

from __future__ import annotations

import argparse
import functools
import gzip
import hashlib
import io
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
    ".png",
    ".svg",
    ".webp",
}

# In-memory ETag cache: maps (absolute_path, mtime) -> etag string.
# Recomputed only when a file's mtime changes.
_etag_cache: dict[tuple[str, float], str] = {}


def etag_for(path: Path) -> str | None:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    key = (str(path), mtime)
    if key not in _etag_cache:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        _etag_cache[key] = f'"{digest}"'
    return _etag_cache[key]


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
    def do_GET(self) -> None:
        if path_extension(self.path) != ".json":
            super().do_GET()
            return

        resolved = self._resolved_path()
        try:
            raw = resolved.read_bytes()
        except OSError:
            self.send_error(404, "File not found")
            return

        accept = self.headers.get("Accept-Encoding", "")
        if "gzip" in accept:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                gz.write(raw)
            body = buf.getvalue()
            encoding = "gzip"
        else:
            body = raw
            encoding = None

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if encoding:
            self.send_header("Content-Encoding", encoding)
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self) -> None:
        ext = path_extension(self.path)
        if ext in CACHEABLE_EXTENSIONS:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        elif ext == ".json":
            self.send_header("Cache-Control", "no-store")
            etag = etag_for(self._resolved_path())
            if etag:
                self.send_header("ETag", etag)
        super().end_headers()

    def _resolved_path(self) -> Path:
        clean = self.path.split("?", 1)[0].split("#", 1)[0]
        return Path(self.directory) / clean.lstrip("/")  # type: ignore[attr-defined]


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
        print("Generate it first with: Lab/scripts/create-catalog.py --clean", file=sys.stderr)
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
