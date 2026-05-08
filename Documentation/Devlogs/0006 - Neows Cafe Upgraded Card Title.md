# 0006 - Neow's Cafe Upgraded Card Title

Date: 2026-05-08

## Context

Cards in STS2 display differently when upgraded: the title gains a `+` suffix and renders in green rather than the default cream. Neow's Cafe had no model field for upgrade state, so all cards rendered with the same cream title regardless of upgrade level.

## Source Findings

Both behaviors are hard-coded in engine C#, not driven by card data:

- The `+` suffix is appended by `CardModel.Title` in `MegaCrit.Sts2.Core.Models/CardModel.cs`. Single-level upgrades get `"Title+"`, multi-level upgrades get `"Title+N"` where N is the current upgrade level.
- The green color is applied by `NCard.UpdateTitleLabel()` in `MegaCrit.Sts2.Core.Nodes.Cards/NCard.cs`. When `CurrentUpgradeLevel > 0` the fill switches to `StsColors.green` (`#7FFF00`) and the outline to `StsColors.cardTitleOutlineSpecial` (`#1B6131`). Unupgraded cards use a cream fill and a rarity-based outline.

Findings are documented in `Lab/Documentation/0015 - Upgraded Card Title Styling.md`.

## App Changes

`Card` gained two new fields with defaults so no existing call site breaks:

- `upgradeLevel: Int = 0`
- `maxUpgradeLevel: Int = 1`

`BannerText` gained `textColor` and `outlineColor` parameters (defaulting to the previous cream/dark-gray values) so the title view can pass upgrade-state colors without duplicating the label rendering logic.

`CardView` now computes three properties from the card model at the call site:

- `displayTitle` applies the `+`/`+N` suffix rule.
- `titleTextColor` returns chartreuse green when upgraded, cream otherwise.
- `titleOutlineColor` returns the special green outline when upgraded, or the rarity-based outline otherwise (uncommon/rare/curse/quest/status/event each have distinct values matching `StsColors`).

Relevant paths:

- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Models/Card.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Components/BannerText.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Views/CardView.swift`

## Verification

```sh
xcodebuild -workspace "Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' \
  build | xcbeautify
```

Build succeeded with no warnings.

## Notes For Future Work

The catalog index does not currently carry `upgradeLevel` or `maxUpgradeLevel`, so no live card in Neow's Cafe will render as upgraded yet. The fields are in the model and the view is wired up; the remaining step is to expose upgrade state from the parser and catalog generator, and pass it through the decoder.

Multi-level upgrade cards (`MaxUpgradeLevel > 1`) are rare in the current card pool, but the suffix logic handles them correctly when the data is present.
