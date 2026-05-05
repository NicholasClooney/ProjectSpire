# ProjectSpire Mods

## Mod architecture overview

Two mods have a deliberate separation of concerns:

- **SpireAPI** — pure game-state access layer. Exposes C# classes (`CombatApi`, etc.) for reading and eventually mutating game state. No HTTP, no transport concerns. Intended to be a foundation other mods can also depend on.
- **SpireRestAPI** — owns the HTTP server and REST routing. References SpireAPI as a project dependency and calls into it to serve game state over HTTP. Compiled with `ExcludeAssets="runtime"` so SpireAPI.dll is not bundled into its output; the game loads each mod independently.

Building SpireRestAPI builds SpireAPI first and deploys both to the game's mods folder automatically.
