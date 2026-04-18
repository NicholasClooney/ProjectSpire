# 0002 - Map Drawing

> **Note:** This document was written against a previous game version. Logic may have changed.

## Core Classes

- **`NMapDrawings`** - the main controller, manages per-player `DrawingState` objects
- **`NMapDrawingInput`** (abstract) with two implementations:
  - `NMouseModeMapDrawingInput` - continuous drawing, line follows mouse movement
  - `NMouseHeldMapDrawingInput` - drawing only while button is held
- **`DrawingMode`** enum: `None`, `Drawing`, `Erasing`

## Input Capture

Left-click starts a line via `BeginLineLocal()`, mouse motion adds points, release calls `StopLineLocal()`. Right/middle click exits drawing mode. A factory method `NMapDrawingInput.Create()` picks mouse vs. controller input handler based on `NControllerManager.IsUsingController`. Input handlers are ephemeral - they emit a `Finished` signal and delete themselves when done.

## Rendering

Each player gets a dedicated **SubViewport** for their drawings. Lines are Godot `Line2D` nodes added as children of that viewport, which renders to a `TextureRect` overlaid on the map. Points are filtered to a minimum 2px distance apart to avoid redundant data. Lines use player-specific colors from `player.Character.MapDrawingColor`.

Erasing isn't a true erase - it creates another `Line2D` with a special `_eraserMaterial` that blends as transparent, painting over existing lines.

## Toggling Drawing Mode

`SetDrawingModeLocal(DrawingMode)` updates the local state and broadcasts a `MapDrawingModeChangedMessage` to other players. The cursor swaps to `cursor_quill.png` when drawing and `cursor_eraser.png` when erasing.

There's no undo - only clear all (`ClearAllLines()` / `ClearAllLinesForPlayer()`), which frees all `Line2D` children from the viewport and syncs via `ClearMapDrawingsMessage`.

## Persistence & Multiplayer

Drawings are fully saved with the run via `GetSerializableMapDrawings()` / `LoadDrawings()`. Each line serializes its points into a normalized "net position" format (relative to map bounds) for compactness.

Network sync uses `MapDrawingMessage` batches of up to 15 events (`BeginLine`, `ContinueLine`, `EndLine`) sent over unreliable UDP, rate-limited to one message per 50ms. Clear operations use reliable transfer.
