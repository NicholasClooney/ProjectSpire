# 0003 - Neow's Cafe Kreon Typography Tiers

Date: 2026-05-07

## Context

`TODOs.md` included an App UI task to register approved app fonts with SwiftUI so standard `.font(...)` usage can pick up the app theme without each call site naming a custom font. The app already bundled Kreon font files under:

- `Apps/Apple/Neow's Cafe/Neow's Cafe/Resources/Fonts/kreon_regular.ttf`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Resources/Fonts/kreon_bold.ttf`

Tuist also already generated `NeowSCafeFontFamily.Kreon` accessors, and the app `Info.plist` included both font files through `UIAppFonts`. The remaining work was to add an app-owned typography layer and route existing app text through it.

## What Changed

The new typography entry point is:

- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/App/NeowSCafeTypography.swift`

It defines:

- Kreon weights: regular and bold.
- Standard text tiers: `largeTitle`, `title`, `title2`, `title3`, `headline`, `body`, `callout`, `subheadline`, `footnote`, `caption`, and `caption2`.
- Card-specific semantic aliases: `cardTitle`, `cardType`, `cardEnergy`, and `cardDescription`.
- SwiftUI and UIKit helpers: `Font.neow(...)` and `UIFont.neow(...)`.

The tier sizes preserve existing app values where they were already visible:

- `cardEnergy` uses 32 pt.
- `cardTitle` uses 26 pt.
- `cardDescription` uses 21 pt.
- `cardType` uses 16 pt.

The remaining standard tiers were filled in around those existing values so future screens can choose a named text role instead of hard-coding point sizes.

`NeowSCafeApp` now calls `NeowSCafeTypography.registerFonts()` on launch and applies the body tier at the root `ContentView`. `CardView` and `BannerText` now use the semantic card tiers.

## Picker Follow-Up

`EnumPicker` was updated to apply `.font(.neow(.body))` to the picker and its option labels. That improves the closed SwiftUI surface, but testing showed the expanded iOS picker menu still renders system text.

The limitation is tracked separately in:

- `Documentation/Issues/0002 - SwiftUI Picker Menu Font Styling.md`

## Verification

The app build passed with:

```sh
xcodebuild -project "Apps/Apple/Neow's Cafe/Neow's Cafe.xcodeproj" \
  -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' \
  build | xcbeautify
```

## Notes For Future Work

Typography should continue to flow through `NeowSCafeTypography` rather than through direct `NeowSCafeFontFamily.Kreon` calls in views. If the app needs menu rows or filter controls to visually match Kreon, implement a custom SwiftUI selector component instead of relying on native `Picker` or `Menu` row rendering.
