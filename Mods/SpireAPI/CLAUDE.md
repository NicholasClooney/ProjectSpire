# CLAUDE.md

This file provides guidance to Claude Code when working in the SpireAPI mod directory.

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

The mod entry point is `SpireAPICode/MainFile.cs`. The `[ModInitializer(nameof(Initialize))]` attribute on the `Node` subclass tells `ModManager` to call `Initialize()` once at game startup. Harmony is available for patching game methods.

Game API access points (from decompiled source in `Lab/`):
- `RunManager.Instance` — run state, players, action queue
- `CombatManager.Instance` — combat state, enemies, hand
- Actions are enqueued via `RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(action)`
- HTTP handlers run on background threads; game state mutations must use `CallDeferred` to dispatch to the Godot main thread
