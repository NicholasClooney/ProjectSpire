# 2026-05-05 - Card Data Resolution Parser Work

## Context

This devlog records the implementation work around `Documentation/0001 - Card Data And Text Resolution.md`, mainly in `Lab/parsers/card_parser.py`, generated card JSON under `Lab/data/v0.103.2/`, and parser coverage tooling under `Lab/audits/`.

The work started as a card data and localization resolver, but quickly became a broader source-fidelity pass. The important development pattern was human-led: the generated JSON was repeatedly inspected against real card examples, issues were pointed out from concrete cards, and those observations were turned into parser behavior, audit scripts, or unresolved-placeholder logs so the same class of issue can be found again.

## What Changed

The parser now emits a clearer two-part card shape:

- `raw` for source-derived facts from decompiled C#.
- `resolved` for localization-resolved display states.

The generated data now includes localized titles and descriptions, structured description runs, upgrade display states, image asset references, structured energy cost, card pool, source relations, hover tips, dynamic variables, value upgrades, and cost upgrades.

The generated cards live under:

- `Lab/data/v0.103.2/cards/`

The unresolved localization audit outputs live at the version root:

- `Lab/data/v0.103.2/unresolved_placeholders.csv`
- `Lab/data/v0.103.2/unresolved_placeholder_catalog.json`

## Issues Found During Review

Several important issues were caught by human review of real generated cards rather than by the first parser implementation.

First, dynamic variable names were too easy to get wrong. The initial approach depended too much on hard-coded type assumptions and convenience aliases. Cards such as `Abrasive` showed why canonical localization variable names matter: localization placeholders use names such as `DexterityPower` and `ThornsPower`, not arbitrary stripped aliases. The parser and audit script now read dynamic variable names from the decompiled dynamic-var source files. If those `.cs` files are missing, the tools fail instead of silently guessing.

Second, cost upgrades are not always increases. The user pointed out cards such as Zap and Dualcast, where upgrading decreases energy cost. That forced the parser to preserve signed `EnergyCost.UpgradeBy(...)` deltas and resolve upgraded cost by applying the delta directly, rather than assuming upgrades are positive improvements to a numeric field.

Third, regular dynamic variable upgrades were not being applied robustly. `Lab/data/v0.103.2/cards/bash.json` exposed that the Vulnerable delta was not appearing in upgraded resolved text. That led to canonicalizing upgrade variable names through `DynamicVarSet.cs` accessors so code like `base.DynamicVars.Vulnerable.UpgradeValueBy(...)` maps back to the source variable key used in `raw.vars` and localization resolution.

Fourth, X-cost cards needed their own shape. Cards such as Tempest, Multi-Cast, Whirlwind, Skewer, and Malaise showed that `-1` cannot be treated as just another integer cost by downstream consumers. The parser now emits structured energy cost data with a `kind`, allowing X-cost cards to be represented explicitly.

Fifth, card pool data was a separate source of truth. The user asked whether card pool was resolved and whether the Swift card model covered all JSON fields. That led to reading card pools from decompiled `*CardPool.cs` files and emitting `raw.card_pool`. Missing pool source now fails fast.

Finally, localization resolution still has unresolved formatter cases. `Lab/data/v0.103.2/cards/unleash.json` surfaced text such as `{CalculatedDamage:diff()}` remaining in resolved output. Instead of treating this as a one-off bug, the parser now writes a CSV with one unresolved placeholder occurrence per row, including the card id, state, placeholder, and resolved text that contains it. It also writes a JSON catalog grouped by placeholder so unresolved formatter work can be prioritized.

## Audit Direction

The most important process improvement was turning human discoveries into repeatable checks.

`Lab/audits/card_parser_coverage.py` exists separately from the exporter. It compares generated JSON against decompiled card source and warns about suspicious source patterns. This keeps the parser honest: the exporter should generate data, while the audit script should ask whether the generated data missed anything obvious in source.

The unresolved placeholder CSV/catalog is the same idea applied to localization. It does not solve every formatter, but it makes unresolved formatter cases visible. That is better than silently emitting strings that look mostly resolved while still containing machine placeholders.

## Human-Led Development Notes

The human/user repeatedly improved the implementation by inspecting concrete outputs and asking source-fidelity questions:

- Noticing cost upgrade direction on cards where upgrades reduce cost.
- Asking for a script to catch missed source patterns after the cost issue appeared.
- Spotting that Bash's upgraded Vulnerable value was not being applied.
- Pushing the parser away from hard-coded dynamic variable assumptions and toward reading decompiled `.cs` source.
- Requiring missing source files to be hard failures.
- Asking whether card pool and downstream model coverage were represented.
- Identifying X-cost cards as a distinct data modeling issue.
- Catching unresolved placeholders in resolved text and steering the response toward CSV logging plus a grouped catalog.
- Moving audit outputs from the `cards/` folder to the version root so generated data is easier to scan.

That review loop is now part of the expected workflow: inspect representative generated JSON, convert findings into parser changes or audit checks, regenerate, and keep unresolved categories visible until they are intentionally resolved.

## Current Verification Snapshot

Recent verification commands used during this pass:

```sh
python3 -m py_compile Lab/parsers/card_parser.py
python3 Lab/parsers/card_parser.py --version v0.103.2
```

The latest unresolved placeholder generation reported:

- `577` card files written.
- `81` unresolved placeholder CSV records.
- `21` unique unresolved placeholder catalog entries.

## Follow-Up Work

The next parser work should use the unresolved catalog to choose formatter support deliberately. Likely areas include calculated damage placeholders, conditional localization behavior, and additional SmartFormat-style functions.

Downstream app work should also compare the generated JSON shape with `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Models/Card.swift` and decide whether the Swift model should represent all raw fields, only display fields, or separate source-fidelity data from app-facing display data.
