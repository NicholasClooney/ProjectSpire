# 2026-05-06 - Neow's Cafe Card Catalog Integration

## Context

This session connected the tracked Slay the Spire 2 card data and recovered portrait resources to `Apps/Apple/Neow's Cafe`.

The starting point was a SwiftUI app with mock cards and a small set of bootstrap card portrait assets. The repository already had generated card JSON under `Lab/data/v0.103.2/cards` and recovered WebP portraits under `Lab/resources/images/packed/card_portraits`. The goal was to let the app browse the real card catalog without building a REST API.

The implementation followed the plan in:

- `Documentation/Plans/0002 - Neow's Cafe Card Catalog Integration.md`

## Catalog Serving Direction

The chosen catalog shape is a static, versioned serving view under:

- `Lab/catalog/v0.103.2/`

The catalog keeps real generated app-facing files for:

- `manifest.json`
- `cards.index.json`

It uses symlinks for existing source material so local development does not duplicate card JSON or image assets:

- `Lab/catalog/v0.103.2/cards`
- `Lab/catalog/v0.103.2/images/card_portraits`

The catalog tooling landed across these commits:

- `dde7842` - `feat(Lab): add card catalog dev tooling`
- `ab8baeb` - `feat(Lab): add generated v0.103.2 card catalog`
- `ba5b216` - `feat(Lab): serve catalog with Python cache headers`
- `5360bc4` - `fix(Lab): use beta card portraits in catalog`

`Lab/scripts/serve-card-catalog.py` replaced the original shell wrapper so the development server can remain a dumb static server while adding long-lived cache headers for catalog JSON and image assets.

## Beta Portrait Follow-Up

Reviewing `ABRASIVE` showed that some card JSON entries only expose `beta_portrait` assets. The first catalog generator pass only accepted `portrait`, which left those cards with `portraitPath: null` even though usable beta art existed.

The generator now resolves portraits in this order:

- `portrait`
- `beta_portrait`
- `null`

After regeneration, `ABRASIVE` points to:

- `images/card_portraits/silent/beta/abrasive.webp`

At the time of this devlog, only `DEPRECATED_CARD` and `MAD_SCIENCE` still have no portrait path in the catalog.

## App Integration

The app-side work landed in:

- `a0ddc5f` - `feat(NeowsCafe): load cards from catalog`
- `f5cef68` - `chore(NeowsCafe): remove bundled card portraits`

The app now fetches `manifest.json`, loads `cards.index.json`, decodes all cards, and renders portraits from catalog URLs. The catalog loading work is split into:

- `CardCatalogService` for fetching.
- `CardCatalogDecoder` and catalog DTOs for decoding.
- `CardCatalogStore` for observable loading/error/card state.

`ContentView` owns the UI state mapping for the catalog:

- loading
- error
- empty
- loaded

This keeps the app shell thin and keeps card-grid behavior dependent on the catalog store rather than on mock-card injection.

The old app-bundled individual card portraits were removed. Shared renderer assets remain in the app bundle, including frames, banners, portrait borders, masks, plaques, and energy icons.

## Verification

The catalog generator and server were verified with:

```sh
python3 -m py_compile Lab/scripts/create-card-catalog.py Lab/scripts/serve-card-catalog.py
Lab/scripts/create-card-catalog.py --clean
```

The Python dev server was checked with localhost HEAD requests and confirmed to return:

```text
Cache-Control: public, max-age=31536000, immutable
```

The app was verified with:

```sh
xcodebuild -workspace "Apps/Apple/Neow's Cafe/Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'platform=iOS Simulator,name=iPhone 17' \
  test | xcbeautify
```

The test run succeeded after catalog decoding tests were added.

## Notes For Future Work

The current app uses catalog URLs and `AsyncImage`; it does not yet implement a custom app-side image cache. The server provides cache headers, and the versioned catalog path is treated as immutable for development.

Future work should decide whether the app needs an explicit disk-backed image cache or whether `URLSession`/`AsyncImage` behavior is enough for the next milestone.

The catalog remains static by design. A REST API should only be introduced if the app needs server-side search, user-specific state, sync, generated assets, or multi-version negotiation beyond the manifest.
