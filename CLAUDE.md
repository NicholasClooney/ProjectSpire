# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo structure

Two independent workspaces:

- `Lab/` — research workspace for decompiling and studying STS2 game source. See `Lab/CLAUDE.md`.
- `Mods/SpireAPI/` — the SpireAPI mod. See `Mods/SpireAPI/CLAUDE.md`.

## Game logs

```
~/Library/Application Support/SlayTheSpire2/logs/godot.log
```

`godot.log` is the current session. Tail it live with `tail -f`.

## Commits

Conventional commits with a scope are required, e.g. `feat(SpireAPI):`, `docs(Lab):`, `chore:`.
