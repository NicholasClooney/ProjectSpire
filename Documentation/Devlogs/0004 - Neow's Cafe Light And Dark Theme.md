# 0004 - Neow's Cafe Light And Dark Theme

Date: 2026-05-07

## Context

`TODOs.md` included an App UI task to explore visual theme work so Neow's Cafe feels closer to Slay the Spire. The previous typography work had already centralized bundled Kreon font usage, so this pass focused on app-level color, chrome, and reusable theme structure.

The goal was to add both light and dark appearances without changing card rendering assets or the existing card metadata tinting pipeline.

## What Changed

The new theme entry point is:

- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/App/NeowSCafeTheme.swift`

It defines dynamic semantic colors for:

- app background
- surfaces
- elevated surfaces
- primary and secondary text
- accent color
- separators

`NeowSCafeApp` now applies the theme at the root alongside the shared typography layer. `ContentView` applies the background, foreground, tint, and explicit navigation/tab bar backgrounds so app chrome participates in the theme. Loading, empty, and error states also use the themed background and text colors.

`CardsView` now gives the cards screen a themed background and wraps the filter controls in a compact elevated surface with a separator stroke. `EnumPicker` keeps using the shared typography tier and now adopts the theme text color while retaining the native menu picker behavior.

The card art, frame, banner, portrait, rarity, and pool color logic remains in `CardView` and its existing `CardAssetColor` metadata path. This keeps the recovered Slay the Spire-inspired card rendering visually faithful while making the app chrome themeable independently.

## TODO Outcome

The original open App UI task:

- `Explore visual theme work so the app feels closer to Slay the Spire, including using the game's font where appropriate.`

was moved to DONE as:

- `Add light and dark app themes inspired by Slay the Spire, with shared semantic colors for app chrome and filter controls.`

The separate font research task remains open because this work used the already-approved bundled Kreon files and did not investigate additional game fonts or licensing.

## Verification

The app build passed with:

```sh
xcodebuild -workspace "Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' \
  build | xcbeautify
```

## Notes For Future Work

Future screens should consume `NeowSCafeTheme` semantic colors instead of defining local palette values. If the theme needs more visual depth, extend the theme with named tokens first, then apply those tokens through screen and component boundaries.

Keep card-specific visual decisions separate from app chrome theme decisions. Card rendering should continue to be driven by recovered assets and card metadata unless a future task explicitly changes the card art system.
