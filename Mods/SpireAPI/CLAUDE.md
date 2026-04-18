# CLAUDE.md

This file provides guidance to Claude Code when working in the SpireAPI mod directory.

## Purpose

SpireAPI is the game-state access layer. It exposes a clean C# API for reading (and eventually mutating) STS2 game state. It has no HTTP or transport concerns — those live in SpireRestAPI.

Other mods can depend on SpireAPI to interact with the game without reimplementing state access.

## Local paths

- **MegaDot executable**: `~/Applications/MegaDot.app/Contents/MacOS/Godot`
- **Slay the Spire 2**: `~/Library/Application Support/Steam/steamapps/common/Slay the Spire 2`

These are already set in `Directory.Build.props`.

## Building

```bash
dotnet build     # compile DLL + auto-copy DLL and manifest to game's mods folder
dotnet publish   # also exports Godot assets to .pck via MegaDot headless
```

`dotnet build` is sufficient during development (no Godot assets yet). `dotnet publish` is required when Godot scenes or assets change.

The build auto-copies output to the game's mods folder via `CopyToModsFolderOnBuild` in `SpireAPI.csproj`. Path resolution is handled by `Sts2PathDiscovery.props` (cross-platform Steam auto-detect) with local overrides in `Directory.Build.props`.

## Architecture

Entry point is `SpireAPICode/MainFile.cs`. The `[ModInitializer(nameof(Initialize))]` attribute on the `Node` subclass tells `ModManager` to call `Initialize()` once at game startup. Harmony is available for patching game methods.

### Game API access

Key game singletons:
- `CombatManager.Instance` — `IsInProgress`, `IsPlayPhase`, `DebugOnlyGetState()` returns `CombatState?`
- `RunManager.Instance` — action queue via `ActionQueueSynchronizer.RequestEnqueue(action)`

Key types:
- `CombatState` — `Enemies`, `Players`, `RoundNumber`, `HittableEnemies`
- `Player.PlayerCombatState` — `Hand`, `Energy`, `MaxEnergy` (null outside combat)
- `CardEnergyCost.GetResolved()` — current effective energy cost including modifiers

### Thread safety

The HTTP server (in SpireRestAPI) runs on a background thread. Reading game state (e.g. `CombatApi.GetCombatState()`) is safe to call from background threads. Game mutations and state changes must run on the Godot main thread.

### API classes

- `CombatApi` — reads current combat state and returns a serialization-friendly snapshot
