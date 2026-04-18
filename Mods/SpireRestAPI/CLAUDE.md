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
| `GET` | `/combat/state` | Current combat state: hand, enemies, energy, round. Returns `isInProgress: false` with a `message` when not in combat. |

### Dependency on SpireAPI

Referenced via `<ProjectReference>` with `ExcludeAssets="runtime" Private="false"` so SpireAPI.dll is available at compile time but not copied into this mod's output. The game loads each mod independently from its own folder.
