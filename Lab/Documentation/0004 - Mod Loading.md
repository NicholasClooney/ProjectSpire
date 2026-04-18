# Mod Loading

> Game version: v0.103.2

## Overview

STS2 ships a first-party mod system. No third-party framework (BepInEx, MelonLoader) is required. The entry point is `ModManager.Initialize()`, called from `OneTimeInitialization` during early startup.

## Mods Directory

The game scans `<executable_dir>/mods/` recursively for mod manifests. On macOS inside Steam:

```
~/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/
  SlayTheSpire2.app/
    Contents/
      MacOS/
        SlayTheSpire2        ← executable
        mods/                ← place mods here
          MyMod/
            manifest.json
            MyMod.dll
            MyMod.pck
```

Mods are also loaded from Steam Workshop subscriptions via `SteamUGC`. Pass `--nomods` on the command line to skip mod loading entirely.

## Mod Structure

Each mod lives in its own subdirectory under `mods/`. At minimum it needs a `manifest.json`. A DLL, a Godot PCK resource pack, or both can accompany it.

```
mods/
  MyMod/
    manifest.json    ← required
    MyMod.dll        ← optional: C# assembly
    MyMod.pck        ← optional: Godot asset pack
```

## manifest.json

| Field | Required | Description |
|---|---|---|
| `id` | yes | Unique string identifier |
| `name` | no | Display name |
| `author` | no | Author name |
| `description` | no | Short description |
| `version` | no | Version string |
| `has_dll` | no | `true` if mod ships a `.dll` |
| `has_pck` | no | `true` if mod ships a `.pck` |
| `dependencies` | no | Array of mod IDs that must load first |
| `affects_gameplay` | no | Defaults to `true` |

Example:

```json
{
  "id": "my-mod",
  "name": "My Mod",
  "author": "Nick",
  "version": "1.0.0",
  "has_dll": true,
  "dependencies": []
}
```

## Initialization

Once an assembly is loaded, the game tries two initialization paths in order:

1. **Custom initializer** -- if any class in the assembly is decorated with `[ModInitializerAttribute("MethodName")]`, that static method is called.
2. **Harmony fallback** -- if no attribute is found, the game calls `Harmony.PatchAll(assembly)`, auto-registering all Harmony patches in the assembly.

## Mod API

`ModHelper` (in `MegaCrit.Sts2.Core.Modding`) exposes:

- `AddModelToPool<TPool, TModel>()` -- register custom cards, relics, monsters, powers, etc.
- `SubscribeForRunStateHooks(delegate)` -- hook into run state events.
- `SubscribeForCombatStateHooks(delegate)` -- hook into combat state events.

## Dependency Management

`ModManager` performs a topological sort of all discovered mods before loading. If a mod lists dependencies in its manifest, those mods are guaranteed to load first. Circular dependencies and missing dependencies are detected and reported with localized error keys (`MOD_ERROR.CIRCULAR_DEPENDENCY`, `MOD_ERROR.MISSING_DEPENDENCY`).

## Mod States

| State | Meaning |
|---|---|
| `None` | Initial, not yet processed |
| `Loaded` | Successfully initialized |
| `Failed` | Load failed (see error key) |
| `Disabled` | User disabled or consent not granted |
| `AddedAtRuntime` | Steam Workshop mod installed during an active session |

## User Consent

The game requires the player to explicitly agree to mod loading (`ModSettings.PlayerAgreedToModLoading`) before any mods are initialized. This is surfaced via `NConfirmModLoadingPopup` in the modding screen UI.

## Key Source Files

| File | Purpose |
|---|---|
| `MegaCrit.Sts2.Core.Modding/ModManager.cs` | Discovery, dependency sort, loading orchestration |
| `MegaCrit.Sts2.Core.Modding/Mod.cs` | Per-mod data (path, state, manifest, assembly) |
| `MegaCrit.Sts2.Core.Modding/ModManifest.cs` | Manifest schema |
| `MegaCrit.Sts2.Core.Modding/ModHelper.cs` | Public mod API |
| `MegaCrit.Sts2.Core.Modding/ModInitializerAttribute.cs` | Attribute for custom init method |
| `MegaCrit.Sts2.Core.Helpers/OneTimeInitialization.cs` | Game startup, calls `ModManager.Initialize()` |
