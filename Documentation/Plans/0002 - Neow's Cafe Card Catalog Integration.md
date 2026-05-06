# Neow's Cafe Card Catalog Integration

Date: 2026-05-06

Project areas: `Lab/`, `Apps/Apple/Neow's Cafe`, card catalog generation

## Summary

Integrate `Lab/data/v0.103.2/cards`, `Lab/resources/images/packed`, and card localization data into `Apps/Apple/Neow's Cafe` through a generated, static, versioned catalog serving view.

Use one compact card index for app-side search and filters, lazy-load portrait images, and avoid a REST API until there is a concrete need for server-side querying or sync.

## Catalog layout

Generate a static catalog serving view under a versioned root:

```text
Lab/catalog/v0.103.2/
manifest.json
cards.index.json
cards -> ../../data/v0.103.2/cards
images/card_portraits -> ../../../resources/images/packed/card_portraits
```

`Lab/data/v0.103.2/cards` and `Lab/resources/images/packed/card_portraits` remain the source of truth. The catalog generator should create real app-facing files for `manifest.json` and `cards.index.json`, then use symlinks for existing raw card JSON and portrait assets to avoid duplicating data during local development.

`manifest.json` is the app's first fetch target. It records:

- `schemaVersion`
- `gameVersion`
- `generatedAt`
- `cardsIndexPath`
- `cardCount`
- supported locales
- asset base path
- checksums

`cards.index.json` is the grid, search, and filter payload. It contains all card summaries needed by the app:

- id
- slug
- title
- description
- energy cost
- type
- rarity
- pool
- portrait path
- optional detail path

Keep individual card JSON files for detail and debug views, not for the main grid. In local development, these files are reached through the `cards` symlink in `Lab/catalog/v0.103.2/`.

## App integration

Replace mock card injection with a `CardCatalogService` that fetches `manifest.json`, validates whether cached data is still current, then loads `cards.index.json`.

Keep existing filters in Swift over an in-memory `[Card]`. The current catalog has 577 cards, so server-side pagination would add complexity without improving the filter UI.

Update `Card` decoding to support generated catalog values, including `energyCost.kind == "x"` and integer costs.

Update portrait rendering so card art can come from catalog URLs or local cache paths instead of only `ImageResource`.

Keep existing frame, banner, plaque, energy icon, rarity, and pool derivation in the app unless generated data exposes a mismatch that requires a narrow model update.

## Serving

Serve `Lab/catalog/` with a static local HTTP server during development. Do not introduce a custom REST API for v1.

The app should see stable HTTP paths and should not depend on whether the backing catalog uses symlinks:

```text
/v0.103.2/manifest.json
/v0.103.2/cards.index.json
/v0.103.2/cards/anger.json
/v0.103.2/images/card_portraits/ironclad/anger.webp
```

Treat a downloadable packed catalog zip as a later extension using the same file layout. Any zip, archive, or export step must materialize symlinks into real files so the packaged catalog is self-contained. The app can eventually download the zip once, extract it, and then read the catalog from local storage.

## Verification

Add unit coverage for:

- manifest decoding and version/checksum comparison
- card index decoding for integer and X-cost cards
- existing search, pool, type, and rarity filters against generated catalog card fixtures
- missing portrait behavior using known cards without portrait assets
- catalog symlink resolution for card JSON and portrait assets

Run the Neow's Cafe test target.

Build the app with compact output:

```sh
xcodebuild ... | xcbeautify
```

Manually verify the Cards tab loads all cards, filters still work, search still works, and portraits load lazily without blocking the grid.

Verify the static server can fetch a sample card JSON and portrait through the catalog URL layout.

## Assumptions

- `v0.103.2` is the first catalog version to expose to the app.
- The card metadata payload is small enough to download as one index.
- Images are the only payload that needs lazy loading.
- English resolved card text from the existing card JSON is sufficient for v1.
- A static catalog is preferred over REST until server-side search, sync, remote hosting policy, or multi-version browsing requires it.
- `Lab/catalog/` is generated, rebuildable, and tracked.
- Symlinks are for local development and repo hygiene; packaged/offline catalogs should contain real files.
