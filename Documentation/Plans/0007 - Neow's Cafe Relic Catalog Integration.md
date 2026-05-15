# Neow's Cafe Relic Catalog Integration

Date: 2026-05-15

Project areas: `Lab/`, `Apps/Apple/Neow's Cafe`, relic catalog generation

## Summary

Integrate `Lab/data/v0.103.2/relics` into `Apps/Apple/Neow's Cafe` using the same catalog pattern established for cards (Plan 0002). Extend the existing catalog layout, manifest, and static server to cover relics. Replace `MockRelics` in the app with a live `RelicCatalogStore`.

## Catalog layout

Extend the existing `Lab/catalog/v0.103.2/` structure:

```text
Lab/catalog/v0.103.2/
  manifest.json          ← add relicsIndexPath, relicCount
  cards.index.json       ← unchanged
  relics.index.json      ← new
  relics -> ../../data/v0.103.2/relics   ← new symlink
  images/relic_portraits -> ../../../resources/images/relics   ← new symlink
```

Extend `Lab/scripts/create-catalog.py` (or extract a shared `create-catalog.py`) to also generate `relics.index.json`. Each entry in the flat index contains:

- `id` — from `id`
- `title` — from `resolved.title`
- `description` — from `resolved.description.plain`
- `descriptionRuns` — from `resolved.description.runs` (text, style per run)
- `flavor` — from `resolved.flavor.plain` (optional)
- `flavorRuns` — from `resolved.flavor.runs` (optional)
- `rarity` — from `raw.rarity` (lowercased)
- `pools` — from `raw.pools` (array of strings)
- `portraitPath` — catalog-relative path resolved from `raw.assets` where `kind == "portrait"` (optional)

`vars` and `tips` from the raw JSON are not included in the index — they are detail-view concerns. Add `detailPath` pointing to the per-relic JSON if those fields are needed later.

Update `manifest.json`:

```json
{
  "relicsIndexPath": "relics.index.json",
  "relicCount": 94
}
```

## App integration

### New files

**`RelicCatalogModels.swift`** — decodable structs that mirror the index schema and map to `Relic`:

```
RelicCatalogIndex     { relics: [RelicCatalogRelic] }
RelicCatalogRelic     → Relic
```

`DescriptionRun` is now a shared top-level type (`Models/DescriptionRun.swift`) used by both `Card` and `Relic`. Its `Style` already conforms to `Decodable`. No separate `CatalogRelicDescriptionRun` type is needed — reuse `CatalogDescriptionRun` from `CardCatalogModels.swift`, which already maps to the shared `DescriptionRun`.

**`RelicCatalogService.swift`** — follows `CardCatalogService` exactly:

```swift
struct RelicCatalogService {
    var baseURL: URL
    func fetchRelics() async throws -> [Relic]
}
```

Fetches manifest → validates `relicsIndexPath` present → fetches `relics.index.json` → decodes via `RelicCatalogDecoder`.

**`RelicCatalogStore.swift`** — follows `CardCatalogStore` exactly:

```swift
@MainActor @Observable
final class RelicCatalogStore: ObservableObject {
    private(set) var relics: [Relic]
    private(set) var errorMessage: String?
    private(set) var isLoading: Bool
    func load() async
}
```

### Files to update

**`Dependencies.swift`** — add `relicCatalogStore: RelicCatalogStore` and a `relicsView` accessor that returns `RelicsView`-compatible data (just the store's `relics` array for now — no filter function needed since filtering is all in-view).

**`ContentView.swift`** — add `.task { await dependencies.relicCatalogStore.load() }` alongside the cards load. Add a `relicCatalogState` computed property mirroring `cardCatalogState`. Replace the mock `RelicsView(relics: MockRelics.relics, ...)` with a `@ViewBuilder relicCatalogContent` switch on loading/error/empty/loaded states, passing `dependencies.relicCatalogStore.relics` when loaded. The `relicSearchText` state and `.searchable` already in place — no change needed there.

**`RelicsView`** — no interface change needed. Already takes `relics: [Relic]` and `searchText: Binding<String>`.

## Serving

Same static server as cards (`Lab/catalog/` at `http://127.0.0.1:8765`). No new server infrastructure needed.

New HTTP paths:

```text
/v0.103.2/relics.index.json
/v0.103.2/relics/burning_blood.json
/v0.103.2/images/relic_portraits/burning_blood.webp
```

## Verification

Run the relic index generator and confirm `relics.index.json` contains all 94 relics with correct `descriptionRuns` for a known relic (e.g. `cracked_core` — should have gold Channel/Lightning runs, blue 1 run).

Manually verify the Relics tab in the app:
- Loads all relics from the live catalog (not mock)
- Rarity filter works
- Search filters by name and description
- Portrait images load from catalog URLs
- Styled description runs render correctly in both the row and detail view
- Dark and light mode both readable

Build:

```sh
xcodebuild -workspace "Neow's Cafe.xcworkspace" -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' build | xcbeautify
```

## Assumptions

- The catalog generator for cards (`create-catalog.py`) is the right place to add relic index generation — one script, one catalog build step.
- `vars` and `tips` from the relic raw JSON are not needed in the app index yet.
- Portrait images for relics already exist at `Lab/resources/images/relics/` as WebP files. Relics without a portrait asset render the placeholder.
- `DescriptionRun` is already a shared top-level type with `Decodable` style conformance. No per-type description run work needed.
- No pagination needed — 94 relics is small enough to load as one index.
