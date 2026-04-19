# CLAUDE.md

This file provides guidance to Claude Code when working in the SpireRestAPI mod directory.

## Purpose

SpireRestAPI owns the HTTP server and REST API routing. It depends on SpireAPI for all game-state access and has no direct game state logic of its own.

## Local paths

- **MegaDot executable**: `~/Applications/MegaDot.app/Contents/MacOS/Godot`
- **Slay the Spire 2**: `~/Library/Application Support/Steam/steamapps/common/Slay the Spire 2`

These are already set in `Directory.Build.props`.

## Building

```bash
dotnet build     # builds SpireAPI first, then SpireRestAPI; deploys both to the game's mods folder
dotnet publish   # also exports Godot assets to .pck via MegaDot headless
```

## Architecture

Entry point is `SpireRestAPICode/MainFile.cs`. On `Initialize()` it starts an `HttpListener` on a background thread and routes incoming requests.

### HTTP server

- Listens on `http://localhost:7777/` and `http://127.0.0.1:7777/` (both needed — macOS resolves `localhost` to IPv6 `::1`, so the explicit IPv4 address is required for browser access via `127.0.0.1`)
- Runs on a background thread; all routing lives in `MainFile.cs`
- Game state is read by calling into SpireAPI (`CombatApi`, etc.) — no direct game access in this project

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | HTML index listing all endpoints |
| `GET` | `/combat/state` | Current combat state: hand (with card ids, names, and `combatCardIndex`), enemies, energy, round. Returns `isInProgress: false` with a `message` when not in combat. |
| `POST` | `/combat/play-card` | Queue a straightforward hand card play using `combatCardIndex` and optional `targetCombatId`. |
| `GET` | `/ui/state` | Describe the current active screen and supported selection details. |
| `POST` | `/combat/select-hand-card` | Answer a supported hand card selection by `combatCardIndex`. |
| `POST` | `/ui/select-card` | Answer a supported overlay or reward card selection by `choiceIndex`. |

### Play-card contract

- `combatCardIndex` is the stable per-combat hand-card identifier exposed by `/combat/state`
- `targetCombatId` is optional and should use the `combatId` from `/combat/state`
- The endpoint currently supports straightforward target types only: `None`, `Self`, `AnyEnemy`, `AllEnemies`, `AnyAlly`, `AllAllies`
- The endpoint dispatches onto the Godot main thread before calling into SpireAPI

Example commands:

```bash
curl -s http://127.0.0.1:7777/combat/state | jq
```

```bash
curl -s -X POST http://127.0.0.1:7777/combat/play-card \
  -H 'Content-Type: application/json' \
  -d '{"combatCardIndex":1,"targetCombatId":1}' | jq
```

```bash
curl -s -X POST http://127.0.0.1:7777/combat/play-card \
  -H 'Content-Type: application/json' \
  -d '{"combatCardIndex":0}' | jq
```

### UI selection contract

- `GET /ui/state` is the discovery endpoint for current interactive UI
- supported `interactionKind` values currently include:
  - `hand_card_selection`
  - `overlay_card_selection`
  - `reward_card_selection`
- hand card selection exposes `combatCardIndex` values and is answered with `POST /combat/select-hand-card`
- overlay and reward card selection expose `choiceIndex` values and are answered with `POST /ui/select-card`
- `combatCardIndex` is only meaningful for the current combat hand
- `choiceIndex` is only meaningful for the currently active overlay or reward screen and should be treated as ephemeral screen-local state

Example `GET /ui/state` shapes:

```json
{
  "interactionKind": "hand_card_selection",
  "prompt": "Choose a Card to Upgrade",
  "handSelectionMode": "UpgradeSelect",
  "selectableCards": [
    {
      "choiceIndex": 0,
      "combatCardIndex": 2,
      "id": "STRIKE_IRONCLAD",
      "name": "Strike",
      "isUpgraded": false
    }
  ]
}
```

```json
{
  "interactionKind": "overlay_card_selection",
  "currentScreenClass": "NChooseACardSelectionScreen",
  "selectableCards": [
    {
      "choiceIndex": 0,
      "combatCardIndex": null,
      "id": "DISCOVERY_OPTION_A",
      "name": "Option A",
      "isUpgraded": false
    }
  ]
}
```

```json
{
  "interactionKind": "reward_card_selection",
  "currentScreenClass": "NCardRewardSelectionScreen",
  "selectableCards": [
    {
      "choiceIndex": 0,
      "combatCardIndex": null,
      "id": "REWARD_CARD_A",
      "name": "Reward Card A",
      "isUpgraded": false
    }
  ]
}
```

Example commands:

```bash
curl -s http://127.0.0.1:7777/ui/state | jq
```

```bash
curl -s -X POST http://127.0.0.1:7777/combat/select-hand-card \
  -H 'Content-Type: application/json' \
  -d '{"combatCardIndex":2}' | jq
```

```bash
curl -s -X POST http://127.0.0.1:7777/ui/select-card \
  -H 'Content-Type: application/json' \
  -d '{"choiceIndex":0}' | jq
```

### Logging

- The logger already prefixes entries with `[SpireRestAPI]` or `[SpireAPI]`; do not duplicate the mod name in the message body
- `POST /combat/play-card` logs use a shared request id like `[play-card req=7]` across both mods so one attempt can be traced end-to-end in `godot.log`
- That same request label is currently reused for non-play endpoints too; the correlation id is authoritative, the `play-card` text is just the current label format

### Dependency on SpireAPI

Referenced via `<ProjectReference>` with `ExcludeAssets="runtime" Private="false"` so SpireAPI.dll is available at compile time but not copied into this mod's output. The game loads each mod independently from its own folder.
