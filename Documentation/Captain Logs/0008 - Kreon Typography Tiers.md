# 0008 - Kreon Typography Tiers

This conversation records the work to register and centralize Neow's Cafe font usage around bundled Kreon fonts.

Entries are newest first. This is not a transcript and it is not a replacement for full devlogs in `Documentation/Devlogs/`. Each entry preserves the interaction shape: user direction, agent response, user steering, outcome, and what future agents should carry forward.

## 2026-05-07 - Document Typography Work And Picker Limitation

**Context:** After researching whether native SwiftUI `Picker` or `Menu` rows can use custom fonts, the user wanted the completed typography work preserved in a devlog and the picker/menu limitation recorded as an issue.

**User Direction:** The user asked to create a devlog for the work done and leave an issue note for the unresolved picker/menu font styling problem.

**Agent Response:** The agent added a numbered devlog for the Neow's Cafe Kreon typography tier work and a numbered issue explaining why native iOS picker/menu rows still render with system fonts.

**User Feedback:** No correction or follow-up yet.

**Outcome:** `Documentation/Devlogs/0003 - Neow's Cafe Kreon Typography Tiers.md` now records the typography implementation, verification, and future guidance. `Documentation/Issues/0002 - SwiftUI Picker Menu Font Styling.md` tracks the native picker/menu font limitation and custom selector tradeoff.

**Carry Forward:** When platform controls block app-specific styling, document the system limitation separately from the implemented work so future agents can preserve the stable abstraction while evaluating whether a custom control is worth the behavior cost.

## 2026-05-07 - Apply Font Tier To EnumPicker

**Context:** After seeing the app in the simulator, the user asked whether `EnumPicker.swift` had been updated to use the new font system.

**User Direction:** The user pointed specifically at the filter picker component and asked whether its fonts were covered.

**Agent Response:** The agent clarified that the picker could inherit the app root font, but SwiftUI picker controls can route through system-backed UI, so the component should apply the typography tier explicitly.

**User Feedback:** The screenshot implied the filter controls still looked like system text and needed attention.

**Outcome:** `EnumPicker` now applies `.font(.neow(.body))` to the picker and its option labels, and the app still builds successfully.

**Carry Forward:** Do not rely only on root font inheritance for controls backed by platform UI. Apply shared typography tiers at reusable component boundaries when visual consistency matters.

## 2026-05-07 - Add Shared Kreon Font Tiers

**Context:** `TODOs.md` included an App UI task to register approved app fonts with SwiftUI so standard `.font(...)` usage can pick up the app theme without repeating custom font names.

**User Direction:** The user asked to take the TODO, register Koreon/Kreon as the app fonts, use them across the app, and create the remaining sizing tiers from existing values.

**Agent Response:** The agent added a shared `NeowSCafeTypography` layer with regular and bold Kreon weights, named font tiers, SwiftUI `Font.neow(...)`, UIKit `UIFont.neow(...)`, app startup registration, and card call sites that use semantic card tiers.

**User Feedback:** No correction or follow-up yet.

**Outcome:** Neow's Cafe now registers bundled Kreon fonts on launch, applies the Kreon body font at the app root, uses named tiers for card title/type/energy/description text, and marks the related TODO complete.

**Carry Forward:** Keep app typography behind shared tiers and semantic aliases so future screens choose intent, such as body or card title, instead of scattering font filenames and point sizes through individual views.
