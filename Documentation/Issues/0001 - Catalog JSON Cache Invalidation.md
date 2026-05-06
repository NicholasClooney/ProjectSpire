# 0001 - Catalog JSON Cache Invalidation

Status: Unsolved
Date: 2026-05-06
Areas: `Lab/scripts/serve-card-catalog.py`, `Lab/scripts/create-card-catalog.py`, `Apps/Apple/Neow's Cafe`

## Symptom

After regenerating `Lab/catalog/v0.103.2/cards.index.json` (commit `5360bc4` added `beta_portrait` resolution so `ABRASIVE` got `images/card_portraits/silent/beta/abrasive.webp`), the Neow's Cafe app still shows no portrait for `ABRASIVE`. The on-disk catalog and the symlinked image are correct.

## Cause

`Lab/scripts/serve-card-catalog.py` sends `Cache-Control: public, max-age=31536000, immutable` for every cacheable extension, including `.json`. The app's `URLSession`/`AsyncImage` cached the older `cards.index.json` (where `ABRASIVE` had `portraitPath: null`) and will not refetch because the cached response is marked immutable. The catalog version path is treated as immutable, but during dev iteration the index is regenerated in place without bumping the version, which breaks that assumption.

## Workarounds

- Reinstall the app on the simulator to clear `URLCache`.
- Bump the catalog version directory when regenerating.

Neither is a real fix. The issue will recur every time a JSON file changes inside an existing version.

## Proposed Solutions

### Option A - ETag revalidation

Override `SimpleHTTPRequestHandler.send_head` in `serve-card-catalog.py` to compute an md5 ETag for each file and handle `If-None-Match` with `304 Not Modified`. Replace `immutable` with `no-cache` (or `no-cache` only for `.json`, keep `immutable` for images).

- Pros: smallest change. No edits to the generator or the app.
- Cons: every request pays a revalidation roundtrip, even when nothing changed.

### Option B - Content-hashed URLs via the manifest

Make `create-card-catalog.py` hash `cards.index.json` (and optionally other content) and write the hash into `manifest.json`, for example:

```json
{ "cardsIndex": "cards.index.json?v=a1b2c3" }
```

or with a hashed filename like `cards.index.a1b2c3.json`. Serve `manifest.json` with `no-cache`; everything the manifest points to keeps `immutable`. The app reads the hashed URL from the manifest instead of constructing a fixed path.

- Pros: zero revalidation traffic for unchanged files. Matches the versioned + immutable model already in place. Standard static-asset pattern.
- Cons: requires coordinated changes in three places: catalog generator, serve script, and the app's catalog loader.

## Recommendation

Option B fits the existing manifest-driven design. Option A is acceptable as a stopgap if the app needs to be unblocked before the generator and app changes land.

## Open Questions

- Should images also be hashed, or is the version-scoped path enough since beta art currently lives under a stable filename?
- If we adopt Option B, should the manifest expose a single content hash for the whole catalog, or per-file hashes?
