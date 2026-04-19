# 0006 - Card Parser

> Updated for the current ProjectSpire implementation on 2026-04-19.

This document describes the first-pass card parser in [Lab/parsers/card_parser.py](/Users/nicholasclooney/Source/Projects/ProjectSpire/Lab/parsers/card_parser.py:1).

## Purpose

The parser converts decompiled card model classes under `Lab/decompiled/<version>/MegaCrit.Sts2.Core.Models.Cards/` into per-card JSON files for research and iteration.

The parser is intentionally conservative. It prefers explicit source facts over inferred gameplay semantics.

## Versioning

The parser has its own internal semantic version:

- `PARSER_VERSION`

Every generated card JSON includes:

- `parser_version`

This version should be bumped whenever the output schema changes, a parsing bug is fixed, or a parser feature is added that changes output meaningfully.

## Input And Output Layout

Discovered decompiled inputs live under:

- `Lab/decompiled/<version>/`

Generated card JSON is written to:

- `Lab/data/<version>/cards/`

Examples:

- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/Accuracy.cs`
- `Lab/data/v0.103.2/cards/accuracy.json`

## CLI Behavior

If no explicit path or version is supplied:

- the parser discovers available versions under `Lab/decompiled/`
- in an interactive terminal, it prompts for a version and defaults to the latest
- in a non-interactive environment, it defaults to the latest version automatically

The parser can also accept:

- a specific version via `--version`
- a specific card file path
- a specific cards directory path

Bulk export reports elapsed time for the parse and write pass.

## Current Schema

Each card JSON currently contains:

- `parser_version`
- `id`
- `class_name`
- `name`
- `file`
- `cost`
- `type`
- `rarity`
- `target`
- `localization`
- `vars`
- `keywords`
- `tags`
- `upgrades`
- `applies_powers`
- `relations`
- `notes`

## Field Semantics

### Source-derived fields

These fields come directly from the decompiled card class:

- `cost`
- `type`
- `rarity`
- `target`
- `vars`
- `keywords`
- `tags`
- `upgrades`

### Behavior-derived fields

These fields come from recognized action patterns in the card body:

- `applies_powers`
- `relations`

`relations` is deliberately split by kind so the parser does not conflate different concepts.

Examples:

- `hover_tip_card`
- `hover_tip_power`
- `hover_tip_orb`
- `creates_card`

This avoids incorrect conclusions such as treating `HoverTipFactory.FromCard<Shiv>()` as proof that a card creates or spawns a `Shiv`.

### Localization-derived fields

The C# card files do not contain card title or description text directly.

Instead, the parser derives expected localization keys:

- `<CARD_ID>.title`
- `<CARD_ID>.description`

If localization data is supplied separately, those values can populate:

- `localization.title`
- `localization.description_raw`

If no localization data is supplied, the parser records the keys and adds a note explaining that description text is not present in the source file itself.

## Known Limitations

This parser is a first-pass heuristic parser, not a full semantic compiler front-end.

Current limitations include:

- only recognized constructor patterns are parsed
- variable extraction is pattern-based and incomplete
- keyword extraction is partial
- tag extraction is text-pattern based
- power application extraction only covers recognized `PowerCmd.Apply<...>` forms
- card creation extraction only covers currently recognized creation patterns
- descriptions are not rendered unless external localization data is supplied
- more complex behaviors such as loops, conditionals, runtime-calculated hit counts, and helper-method indirection are only partially represented

## Example Commands

Export the latest discovered version to versioned output:

```bash
python3 Lab/parsers/card_parser.py
```

Export a specific version:

```bash
python3 Lab/parsers/card_parser.py --version v0.103.2
```

Export one card:

```bash
python3 Lab/parsers/card_parser.py Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/Accuracy.cs
```

Print JSON to stdout instead of writing files:

```bash
python3 Lab/parsers/card_parser.py --version v0.103.2 --stdout
```
