# ProjectSpire

## Repo structure

- `Documentation/` — project-wide records, plans, and decisions that span multiple repo areas.
- `Lab/` — research workspace for decompiling and studying STS2 game source. See `Lab/CLAUDE.md`.
- `Mods/` — Godot/C# mod projects. See `Mods/README.md`.
- `Mods/SpireAPI/` — game-state API layer mod. See `Mods/SpireAPI/CLAUDE.md`.
- `Mods/SpireRestAPI/` — REST HTTP server mod, depends on SpireAPI. See `Mods/SpireRestAPI/CLAUDE.md`.

## Ideas

- SpireAPI -- an unofficial programmable easy to use API for mods
- SpireRESTAPI -- this will be built upon the SpireAPI project to provide
  RESTful API
- SpireVoiceCommand -- this will be built upon the SpireAPI project to provide
  voice command / accessibilities. ideally with a whisper built-in, start with
  english, expand to other languages with community support or using AI. MVP
  would be just controlling the game, v2 would add in voice over ish feature
  too, i.e. reading things out loud based on commands. i.e. "available actions"
  / "enemies" / "relics" / "potions" / "players" / "player 1 xyz..."
