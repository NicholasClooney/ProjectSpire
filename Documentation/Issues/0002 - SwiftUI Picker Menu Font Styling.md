# 0002 - SwiftUI Picker Menu Font Styling

Status: Open
Date: 2026-05-07
Areas: `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Components/EnumPicker.swift`, `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/App/NeowSCafeTypography.swift`

## Symptom

The filter controls in Neow's Cafe use `EnumPicker`, and the closed picker label can receive the app's Kreon font tier. When the picker opens on iOS, the presented menu rows still render with the system font.

Applying `.font(.neow(.body))` to the `Picker`, each option `Text`, and the app root does not change the expanded menu row font.

## Cause

Menu-style SwiftUI `Picker` controls on iOS present their expanded options through system menu infrastructure rather than ordinary SwiftUI `Text` rendering. The underlying UIKit menu APIs expose titles, images, state, attributes, and preferred element size, but they do not provide a supported per-row font API.

SwiftUI `Menu` has the same practical limitation for opened rows. Its label can be styled because the label is regular SwiftUI content, but the presented menu items are still system-rendered.

## Current Workaround

Keep `EnumPicker` on the shared typography tier for the closed picker surface:

```swift
.font(.neow(.body))
```

Accept that expanded native menu rows remain system-styled for now.

## Proposed Solution

If the opened filter menu needs to match Kreon, replace the native picker/menu presentation with a custom SwiftUI selector:

- Keep the existing `EnumPicker("Character", selection:)` call-site API if possible.
- Render the closed control as a SwiftUI button.
- Present a custom SwiftUI popover/list overlay for options.
- Use `Font.neow(...)` on every visible row.
- Recreate the selected-state checkmark and dismissal behavior.

## Tradeoffs

Native `Picker` and `Menu` preserve system behavior, accessibility, and platform menu styling with minimal code, but they do not support custom row fonts.

A custom selector gives full visual control and can match the app typography, but it must own more behavior: row layout, selected state, dismissal, positioning, scrolling, VoiceOver labels, and keyboard or pointer affordances.

## Open Questions

- Should the app accept native system font rows for filters until the broader Slay the Spire-inspired visual theme work begins?
- Should the eventual filter control use text labels, recovered character icons, or both?
- If a custom selector is built, should it be popover-based or inline/horizontal to better fit the card catalog screen?
