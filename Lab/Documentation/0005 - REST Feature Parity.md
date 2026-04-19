# 0005 - REST Feature Parity

> Updated for the current ProjectSpire implementation on 2026-04-18.

This document tracks which game interactions the current REST layer can read, detect, and complete.

## Status Key

- `Supported` means there is a working endpoint path for the interaction
- `Partial` means part of the flow is implemented but follow-up or edge cases are missing
- `Detectable Only` means the current UI/game state can be identified but not acted on yet
- `Unsupported` means there is no current API support

## Feature Matrix

| Interaction | Status | Endpoint(s) | Notes |
|------------|--------|-------------|-------|
| Read combat state | Supported | `GET /combat/state` | Exposes hand, enemies, energy, round, and `combatCardIndex` for hand cards |
| Play straightforward hand card | Supported | `POST /combat/play-card` | Works for `None`, `Self`, `AnyEnemy`, `AllEnemies`, `AnyAlly`, `AllAllies` |
| Detect active screen/UI | Supported | `GET /ui/state` | Reports current screen class, screen type, and supported selection details |
| Hand upgrade selection | Supported | `GET /ui/state`, `POST /combat/select-hand-card` | Covers in-combat `NPlayerHand.Mode.UpgradeSelect`, such as unupgraded `Armaments` |
| Overlay choose-a-card selection | Supported | `GET /ui/state`, `POST /ui/select-card` | Covers `NChooseACardSelectionScreen`, such as `Discovery` |
| Post-combat card reward selection | Supported | `GET /ui/state`, `POST /ui/select-card` | Covers `NCardRewardSelectionScreen` |
| End turn | Unsupported | None yet | Game path is understood from decompiled code but not exposed in ProjectSpire yet |
| Use potion | Unsupported | None yet | Game path is understood from decompiled code but not exposed in ProjectSpire yet |
| Random/special target card play | Unsupported | None yet | Includes `RandomEnemy`, `AnyPlayer`, `TargetedNoCreature`, `Osty` |
| Generic follow-up player-choice flows | Partial | Current UI endpoints | Some families are supported, but not every choice screen or multi-step flow |
| Console command execution | Unsupported | None yet | Planned next candidate: direct dev-console hook plus history/replay |

## Notes by Interaction

### Straightforward hand card play

Current support is intentionally narrow. The endpoint uses the game's normal manual-play path and dispatches to the Godot main thread before calling `TryManualPlay`.

Supported target families:

- `None`
- `Self`
- `AnyEnemy`
- `AllEnemies`
- `AnyAlly`
- `AllAllies`

Unsupported target families:

- `RandomEnemy`
- `AnyPlayer`
- `TargetedNoCreature`
- `Osty`

### Hand upgrade selection

This currently supports the in-combat hand selector used by flows like unupgraded `Armaments`.

`GET /ui/state` reports:

- `interactionKind: "hand_card_selection"`
- `prompt`
- `handSelectionMode`
- `selectableCards[]`

Selection is then submitted with `POST /combat/select-hand-card`.

### Overlay choose-a-card selection

This covers `NChooseACardSelectionScreen`, which is used by effects like `Discovery`.

`GET /ui/state` reports:

- `interactionKind: "overlay_card_selection"`
- `currentScreenClass: "NChooseACardSelectionScreen"`
- `selectableCards[]` with `choiceIndex`

`choiceIndex` is only valid for the currently active overlay screen. It is not a persistent card identifier and should be read fresh from `GET /ui/state` before selection.

Selection is submitted with `POST /ui/select-card`.

### Post-combat card reward selection

This covers `NCardRewardSelectionScreen`, which is the card reward screen shown after combat.

`GET /ui/state` reports:

- `interactionKind: "reward_card_selection"`
- `currentScreenClass: "NCardRewardSelectionScreen"`
- `selectableCards[]` with `choiceIndex`

`choiceIndex` is only valid for the currently active reward screen. It is not stable across screens or screen refreshes.

Selection is submitted with `POST /ui/select-card`.

## Example Commands

Inspect combat state:

```bash
curl -s http://127.0.0.1:7777/combat/state | jq
```

Inspect current UI state:

```bash
curl -s http://127.0.0.1:7777/ui/state | jq
```

Play a straightforward targeted card:

```bash
curl -s -X POST http://127.0.0.1:7777/combat/play-card \
  -H 'Content-Type: application/json' \
  -d '{"combatCardIndex":1,"targetCombatId":1}' | jq
```

Resolve a hand upgrade selection:

```bash
curl -s -X POST http://127.0.0.1:7777/combat/select-hand-card \
  -H 'Content-Type: application/json' \
  -d '{"combatCardIndex":2}' | jq
```

Resolve an overlay or reward card selection:

```bash
curl -s -X POST http://127.0.0.1:7777/ui/select-card \
  -H 'Content-Type: application/json' \
  -d '{"choiceIndex":0}' | jq
```

## Logging

The interaction flow is logged with a shared request id, for example:

```text
[INFO] [SpireRestAPI] [play-card req=12] request: POST /ui/select-card
[INFO] [SpireAPI] [play-card req=12] selecting overlay card choiceIndex=0 card=SOME_CARD
[INFO] [SpireRestAPI] [play-card req=12] ui/select-card result success=True message="Selected UI card"
```

The current request label text is still `play-card req=N` even for non-play endpoints like `GET /ui/state` and `POST /ui/select-card`. The correlation id is the important part; the label wording is just not generalized yet.

Tail the game log during testing:

```bash
tail -f ~/Library/Application\ Support/SlayTheSpire2/logs/godot.log
```
