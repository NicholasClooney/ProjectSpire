# 0006 - App UI TODO Capture

This conversation records lightweight TODO capture for ProjectSpire app UI ideas.

Entries are newest first. This is not a transcript and it is not a replacement for full devlogs in `Documentation/Devlogs/`. Each entry preserves the interaction shape: user direction, agent response, user steering, outcome, and what future agents should carry forward.

## 2026-05-07 - Add Character Icon Dropdown TODO

**Context:** The user had another future UI task to capture alongside the existing app UI TODOs.

**User Direction:** The user asked to add a task to replace character names in the dropdown with icons from the game's card library screen.

**Agent Response:** The agent added the task to the `App UI` section of `TODOs.md`.

**User Feedback:** No correction or follow-up yet.

**Outcome:** The character dropdown icon replacement is now recorded as a future UI task.

**Carry Forward:** When implementing this, source the icons from the game's card library screen assets so the dropdown matches in-game visual language.

## 2026-05-07 - Record App UI Ideas In TODOs

**Context:** The user wanted several app-facing ideas saved quickly as TODOs rather than implemented immediately.

**User Direction:** The user asked to record ideas for a card details view with a `View Upgrades` button, keyword rendering in card UI such as Ascender's Bane, a relics tab, and theme/font work that may use Slay the Spire's font after checking the game code and font licensing.

**Agent Response:** The agent inspected the existing TODO and Captain Log formats, then added the ideas under a new `App UI` section in `TODOs.md` with rough difficulty tags.

**User Feedback:** No correction or follow-up yet.

**Outcome:** `TODOs.md` now contains the requested app UI TODOs, split into implementation, investigation, and SwiftUI font registration tasks.

**Carry Forward:** Before implementing theme work, verify the actual game font usage and license status rather than assuming Koreon is the only font or that it is usable in the app.
