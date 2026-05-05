# 0006 - Card Parser

> Updated for the current ProjectSpire implementation on 2026-05-05.

This document describes the first-pass card parser in `Lab/parsers/card_parser.py`.

## Purpose

The parser converts decompiled card model classes under `Lab/decompiled/<version>/MegaCrit.Sts2.Core.Models.Cards/` into per-card JSON files for research, iteration, and downstream card renderers.

The parser is intentionally conservative. It prefers explicit source facts over inferred gameplay semantics.

## Versioning

The parser has its own internal semantic version:

- `PARSER_VERSION`

Every generated card JSON includes:

- `schema_version`
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

By default, the parser resolves English card text from:

- `Lab/resources/localization/eng/cards.json`

The resolver can also accept:

- `--language <code>` to load `Lab/resources/localization/<code>/cards.json`
- `--localization <path>` to use a specific card localization file
- `--raw-only` to skip text resolution and leave `resolved` empty

## Current Schema

Each card JSON currently contains:

- `schema_version`
- `id`
- `raw`
- `resolved`

`raw` currently contains:

- `parser_version`
- `class_name`
- `file`
- `cost`
- `type`
- `rarity`
- `target`
- `localization`
- `vars`
- `assets`
- `keywords`
- `tags`
- `upgrades`
- `cost_upgrades`
- `tips`
- `applies_powers`
- `relations`
- `notes`

`resolved` currently contains app-friendly display states:

- `base`
- `upgraded`

Each state includes title, cost, and description text as both `plain` text and styled `runs`.

## Field Semantics

### Source-derived fields

These fields come directly from the decompiled card class:

- `cost`
- `type`
- `rarity`
- `target`
- `vars`
- `assets`
- `keywords`
- `tags`
- `upgrades`
- `cost_upgrades`

`vars` uses canonical localization variable identities only. For example, `PowerVar<DexterityPower>` is emitted as `DexterityPower`, not as both `DexterityPower` and a stripped `Dexterity` alias.

`upgrades` uses the same canonical identities as `vars`. When source calls an accessor such as `base.DynamicVars.Vulnerable.UpgradeValueBy(1m)`, the parser resolves that accessor through `DynamicVarSet` and emits `VulnerablePower` so upgraded descriptions apply the delta.

`assets` records discovered packed card portrait files under `Lab/resources/images/packed/card_portraits/`. The parser derives each card pool from decompiled `CardPool` classes, then checks for regular and beta `.webp` portraits in that pool.

`cost_upgrades` records source-level `base.EnergyCost.UpgradeBy(...)` calls separately from dynamic variable upgrades. Resolved upgraded card states apply those deltas to `cost`, clamped to zero to match `CardEnergyCost.UpgradeBy`.

### Behavior-derived fields

These fields come from recognized action patterns in the card body:

- `applies_powers`
- `relations`
- `tips`

`relations` is deliberately split by kind so the parser does not conflate different concepts.

Examples:

- `creates_card`

This avoids incorrect conclusions such as treating `HoverTipFactory.FromCard<Shiv>()` as proof that a card creates or spawns a `Shiv`.

`tips` is separate from card-creation `relations` and includes currently recognized hover-tip sources:

- `hover_tip_static`
- `hover_tip_card`
- `hover_tip_power`
- `hover_tip_orb`

### Localization-derived fields

The C# card files do not contain card title or description text directly.

Instead, the parser derives expected localization keys:

- `<CARD_ID>.title`
- `<CARD_ID>.description`

If localization data is loaded, it populates the second-pass `resolved` display states:

- `resolved.base.title`
- `resolved.base.description.plain`
- `resolved.base.description.runs`
- `resolved.upgraded.title`
- `resolved.upgraded.description.plain`
- `resolved.upgraded.description.runs`

If required localization keys are missing during resolution, the parser fails instead of emitting partial display data. Use `--raw-only` when localization is intentionally unavailable.

The MVP resolver supports:

- simple variables, such as `{Damage}`
- `diff()` values, including green/red upgraded value runs when an upgrade delta changes the value
- `plural`, `show`, `energyIcons`, and `starIcons` fallback formatting
- simple BBCode-style tags such as `[gold]...[/gold]`

Unknown variables are preserved as placeholder text so unresolved formatter behavior remains visible to downstream tools.

### Localization key derivation

The `<CARD_ID>.title` and `<CARD_ID>.description` convention comes from the decompiled base card model, not from an assumption in the parser.

In `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardModel.cs`, `CardModel` defines:

```csharp
public LocString TitleLocString => new LocString("cards", base.Id.Entry + ".title");

public LocString Description => new LocString("cards", base.Id.Entry + ".description");
```

This means card titles and descriptions are looked up in the `cards` localization table with entry keys derived from `base.Id.Entry`.

`base.Id.Entry` is assigned by `AbstractModel` through `ModelDb.GetId(type)`. `ModelDb.GetEntry(Type type)` returns:

```csharp
return StringHelper.Slugify(type.Name);
```

`StringHelper.Slugify` converts a class name to the uppercase model entry form used by localization keys, for example:

- `Accuracy` -> `ACCURACY`
- `StrikeDefect` -> `STRIKE_DEFECT`

The parser mirrors this with `class_name_to_id()` and then emits:

```python
title_key = f"{card_id}.title"
description_key = f"{card_id}.description"
```

Strictly speaking, `<CARD_ID>` means the model entry ID derived from the card class name, not the displayed card title.

## Known Limitations

This parser is a first-pass heuristic parser, not a full semantic compiler front-end.

Current limitations include:

- only recognized constructor patterns are parsed
- variable extraction is pattern-based and incomplete
- keyword extraction is partial
- tag extraction is text-pattern based
- power application extraction only covers recognized `PowerCmd.Apply<...>` forms
- card creation extraction only covers currently recognized creation patterns
- the text resolver is an MVP subset of the game's localization formatter behavior
- more complex behaviors such as loops, conditionals, runtime-calculated hit counts, and helper-method indirection are only partially represented

## Coverage Audit

`Lab/audits/card_parser_coverage.py` compares decompiled card source against generated card JSON. It is intended to catch parser coverage gaps such as a source `EnergyCost.UpgradeBy(...)` call that has no generated `raw.cost_upgrades` entry.

Run the default hard-mismatch and unsupported-source-pattern audit:

```bash
python3 Lab/audits/card_parser_coverage.py --version v0.103.2
```

The default audit exits non-zero for errors. Warnings identify source APIs that may deserve future parser support.

Use the opt-in noisy checks when investigating dynamic variables or localization formatter coverage:

```bash
python3 Lab/audits/card_parser_coverage.py --version v0.103.2 \
  --include-dynamic-var-warnings \
  --include-localization-placeholder-warnings
```

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

Export raw-only JSON without resolving localization:

```bash
python3 Lab/parsers/card_parser.py --version v0.103.2 --raw-only
```
