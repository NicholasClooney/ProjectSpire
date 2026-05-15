# 0007 - Card Catalog Server Compression

Date: 2026-05-08

## Context

`cards.index.json` for v0.103.2 is 464 KB uncompressed. The local dev server had no compression, so every fetch transferred the full payload. iOS `URLSession` already advertises `Accept-Encoding: gzip` automatically, so adding server-side gzip required no client changes.

## Changes

`Lab/scripts/serve-catalog.py` gained a `do_GET` override on `CardCatalogHandler`. For JSON requests it reads the file, compresses with gzip if the client sent `Accept-Encoding: gzip`, and writes the response with the correct `Content-Length` and `Content-Encoding: gzip` headers. Non-JSON requests fall through to `SimpleHTTPRequestHandler` unchanged. `end_headers` and ETag logic are unaffected.

Compressed sizes at default gzip level:

| Encoding | Size |
|----------|------|
| None | 464 KB |
| gzip | 39 KB |
| brotli | 28 KB |

Brotli was not added; it requires a third-party package and the gzip reduction (~91%) is sufficient for local dev.

## Verification

```sh
python3 -m py_compile Lab/scripts/serve-catalog.py
```

Compiles clean.
