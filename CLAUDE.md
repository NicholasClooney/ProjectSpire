# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo structure

- `Lab/` — research workspace for decompiling and studying STS2 game source. See `Lab/CLAUDE.md`.
- `Mods/SpireAPI/` — game-state API layer mod. See `Mods/SpireAPI/CLAUDE.md`.
- `Mods/SpireRestAPI/` — REST HTTP server mod, depends on SpireAPI. See `Mods/SpireRestAPI/CLAUDE.md`.

## Mod architecture overview

Two mods with a deliberate separation of concerns:

- **SpireAPI** — pure game-state access layer. Exposes C# classes (`CombatApi`, etc.) for reading and eventually mutating game state. No HTTP, no transport concerns. Intended to be a foundation other mods can also depend on.
- **SpireRestAPI** — owns the HTTP server and REST routing. References SpireAPI as a project dependency and calls into it to serve game state over HTTP. Compiled with `ExcludeAssets="runtime"` so SpireAPI.dll is not bundled into its output; the game loads each mod independently.

Building SpireRestAPI builds SpireAPI first and deploys both to the game's mods folder automatically.

## Game logs

```
~/Library/Application Support/SlayTheSpire2/logs/godot.log
```

`godot.log` is the current session. Tail it live with `tail -f`.

## Commits

Conventional commits with a scope are required, e.g. `feat(SpireAPI):`, `feat(SpireRestAPI):`, `docs(Lab):`, `chore:`.
