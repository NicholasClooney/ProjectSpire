# 0005 - Card Keyword Pipeline And Neow's Cafe Rendering

Date: 2026-05-08

## Context

This devlog records the card keyword work that followed the initial card parser and Neow's Cafe catalog integration.

The issue surfaced from visual comparison against in-game card renders: cards such as `Ascender's Bane`, `Dazed`, and `Bombardment` showed keyword lines that were not visible in Neow's Cafe because the app only consumed `description` text. The generated parser data already knew about some keyword membership, but it did not yet expose localized keyword display text, before/after placement, or upgrade-time keyword changes in a way the app could use.

## Source Findings

The game does not infer keyword text placement from localization text or keyword meaning. It uses explicit keyword ordering source:

- `CardKeyword.cs`
- `CardKeywordOrder.cs`
- `card_keywords.json`

The source-defined placement split is:

- Before description: `Ethereal`, `Sly`, `Retain`, `Innate`, `Unplayable`
- After description: `Exhaust`, `Eternal`

At the time of the investigation there was no placement overlap and no displayed enum missing from the before/after arrays.

Detailed findings are documented in:

- `Lab/Documentation/0014 - Card Keywords.md`
- `Lab/Documentation/0006 - Card Parser.md`
- `Documentation/Plans/0004 - Card Keyword Parser Schema.md`

## Parser And Data Shape

The parser schema moved to `0.2.4` and now keeps keyword data structured instead of concatenating it into card description text.

Important generated fields:

- `raw.keywords` records base source keyword membership.
- `raw.keyword_upgrades` records direct keyword add/remove mutations found in `OnUpgrade()`.
- `resolved.keyword_period` carries the localized period used after keyword titles.
- `resolved.base.keywords` and `resolved.upgraded.keywords` carry localized keyword objects with `id`, `placement`, `title`, and resolved description data.

The coverage audit was expanded to compare generated keyword membership and upgrade keyword deltas against decompiled source.

Relevant commit:

- `3a6d3dd` - `feat(parser): resolve card keyword metadata`

## Catalog And App Integration

Neow's Cafe reads a compact app-facing catalog index rather than full card JSON for the main card grid. That meant the keyword data had to be carried into `Lab/catalog/v0.103.2/cards.index.json` before Swift could render it.

The catalog summary generator now emits:

- `keywords`
- `keywordPeriod`

The Swift model now includes:

- `Card.Keyword`
- `Card.Keyword.Placement`
- `Card.keywords`
- `Card.keywordPeriod`

The catalog decoder maps keyword summaries into the Swift model, and the card view renders keyword title lines around the rules description according to placement.

Relevant commits:

- `f05b318` - `feat(catalog): expose card keyword summaries`
- `a0a5a20` - `feat(app/cafe): render card keyword text`

## Text Fitting And Search

After keyword rendering landed, `Bombardment` exposed a layout issue: long descriptions plus keyword lines could truncate in the fixed in-game card text box.

`CardView` now composes rules text as one styled `AttributedString` and renders it with a minimum scale factor, so keyword and description text shrink together while preserving keyword color. This replaced the earlier independent text views, which made truncation difficult to control.

`CardFilter` now searches keyword `id` and `title`, so filtering for terms such as `exhaust` finds cards where the visible match comes from keyword text rather than the base description.

Relevant paths:

- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Views/CardView.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Logic/CardFilter.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Tests/NeowSCafeTests.swift`

## Verification

Parser and audit verification during the keyword parser pass:

```sh
python3 -m py_compile Lab/parsers/card_parser.py Lab/audits/card_parser_coverage.py
python3 Lab/audits/card_parser_coverage.py --version v0.103.2
```

Targeted spot checks confirmed:

- `ascenders_bane`: `Unplayable`, `Ethereal`, `Eternal`
- `dazed`: `Unplayable`, `Ethereal`
- `know_thy_place`: base `Exhaust`, upgraded none
- `aggression`: upgraded `Innate`

Catalog/app verification:

```sh
python3 -m py_compile Lab/scripts/create-card-catalog.py
xcodebuild -workspace "Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' \
  build | xcbeautify
xcodebuild -workspace "Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  test | xcbeautify
```

The latest test pass included:

- `decodesCatalogCards()`
- `filtersCatalogCardsByKeywordText()`

## Notes For Future Work

The current app renders localized keyword titles, not full keyword tooltip descriptions. The parser already resolves keyword descriptions, but the compact catalog summary intentionally carries only the fields needed for card-face rendering.

If Neow's Cafe adds card detail screens, hover sheets, or keyword glossary UI, the next step should be to either fetch each card's `detailPath` JSON or expand the catalog summary deliberately. Avoid folding keyword text into `description`; placement and identity are source data and should stay structured.

Long text now scales to fit better, but card text layout is still approximate. If exact in-game fidelity becomes a goal, future work should compare rendered screenshots against representative cards with multiple before/after keywords, long descriptions, no descriptions, and ancient frames.
