# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Research workspace for decompiling and studying Slay the Spire 2 game logic. The goal is to read the decompiled C# source to understand mechanics (cards, relics, monsters, runs, etc.) and document findings.

## Decompiling

Use `/decompile-sts2` to run the decompile script. Decompiled source lands in `decompiled/<version>/` (e.g. `decompiled/v0.103.2/`) and is gitignored.

## Decompiled code structure

The DLL decompiles into one `.cs` file per class, organised into namespace-named folders:

- `MegaCrit.Sts2.Core.Models.Cards/` — card definitions
- `MegaCrit.Sts2.Core.Models.Monsters/` — monster definitions
- `MegaCrit.Sts2.Core.Models.Relics/` — relic definitions
- `MegaCrit.Sts2.Core.Models.Powers/` — power (buff/debuff) definitions
- `MegaCrit.Sts2.Core.Runs/` — run management and history
- `MegaCrit.Sts2.Core.Saves/` — save file schemas and migration system
- `MegaCrit.Sts2.Core.Debug/` — `ReleaseInfoManager` (version detection), Sentry integration
- `Properties/AssemblyInfo.cs` — assembly version and git commit hash

## Commits

Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.).

## Documentation

Findings go in `Documentation/` using the naming convention `0001 - Title Words Here.md`. Each document should note the game version it was written against.
