# 0004 - Card Keyword Parser Schema

Date: 2026-05-08

Project areas: `Lab/parsers`, `Lab/data`, `Lab/Documentation`

Status: Implemented

## Summary

Update `Lab/parsers/card_parser.py` so generated card JSON carries structured keyword display data derived from game source truth:

- Keep `raw.keywords` as the canonical source keyword list for the base card.
- Add source-derived upgrade keyword deltas so upgraded states can differ from base states.
- Add localized, placement-aware keyword objects to `resolved.base` and `resolved.upgraded`.
- Use `placement`, not `type`, with values `beforeDescription` and `afterDescription`.
- Do not add `displayText`; resolved keyword objects carry localized `title` and `description`, plus a shared localized `keyword_period` so consumers can render `Title + period`.

## Key Changes

- Add parser helpers that read `CardKeywordOrder.cs` for the selected decompiled version:
  - `beforeDescription`: `Ethereal`, `Sly`, `Retain`, `Innate`, `Unplayable`
  - `afterDescription`: `Exhaust`, `Eternal`
  - Fail fast if a real `CardKeyword` enum value except `None` has no placement or appears in both placement arrays.

- Keep `raw.keywords: list[str]` as existing canonical membership, and add `raw.keyword_upgrades` for `OnUpgrade()` keyword mutations:
  - shape: `{ "operation": "add" | "remove", "keyword": "<Keyword>", "source": "OnUpgrade" }`
  - parse direct `AddKeyword(CardKeyword.X)` and `RemoveKeyword(CardKeyword.X)` in card classes.
  - This matters because some upgrades add or remove keywords, e.g. `AddKeyword(CardKeyword.Innate)` and `RemoveKeyword(CardKeyword.Exhaust)`.

- Extend resolved schema:
  - Add `keyword_period` under top-level `resolved`, loaded from `Lab/resources/localization/<language>/card_keywords.json` key `PERIOD`.
  - Add `keywords` to each `ResolvedCardState`.
  - Each resolved keyword object:

```json
{
  "id": "Unplayable",
  "placement": "beforeDescription",
  "title": "Unplayable",
  "description": {
    "plain": "Unplayable cards cannot be played.",
    "runs": []
  }
}
```

- Ordering rules:
  - For `beforeDescription`, emit visible render order, meaning reverse of `CardKeywordOrder.beforeDescription` for present keywords because the game uses `Insert(0, ...)`.
  - For `afterDescription`, emit array order from `CardKeywordOrder.afterDescription`.
  - Combined resolved list order should match final card text order: before keywords, then after keywords. Placement remains explicit so consumers can place normal description between the two groups when needed.

- Localization loading:
  - Continue loading card text from `cards.json`.
  - Also load `card_keywords.json` for the selected language unless `--raw-only` is set.
  - Missing keyword title/description/period keys should fail during resolved generation, matching the current "fail instead of partial resolved display data" rule.

- Versioning and docs:
  - Bump `PARSER_VERSION` and `SCHEMA_VERSION` from `0.2.3` to `0.2.4`.
  - Update `Lab/Documentation/0006 - Card Parser.md` to describe `raw.keyword_upgrades`, `resolved.keyword_period`, and `resolved.*.keywords`.
  - Update `Lab/Documentation/0014 - Card Keywords.md` to replace "current gaps" with the new schema behavior.

## Test Plan

- Run one-card stdout checks:
  - `AscendersBane.cs`: `resolved.base.keywords` should be `Unplayable`, `Ethereal`, `Eternal` with placements `beforeDescription`, `beforeDescription`, `afterDescription`.
  - `Dazed.cs`: `resolved.base.keywords` should be `Unplayable`, `Ethereal`.
  - A card that removes `Exhaust` on upgrade, such as `KnowThyPlace.cs`, should include `Exhaust` in base keywords and omit it from upgraded keywords.
  - A card that adds a keyword on upgrade, such as `Aggression.cs`, should include `Innate` only in upgraded keywords.

- Regenerate parser output for `v0.103.2`:

```bash
python3 Lab/parsers/card_parser.py --version v0.103.2
```

- Run audit:

```bash
python3 Lab/audits/card_parser_coverage.py --version v0.103.2
```

- Add or update audit coverage so source `AddKeyword`/`RemoveKeyword` upgrade mutations are compared against generated `raw.keyword_upgrades`.

## Assumptions

- `placement` is the chosen field name.
- `resolved.*.keywords` is per state because upgrades can add or remove keywords.
- `displayText` is intentionally omitted; renderers can compose keyword line text from `title + resolved.keyword_period`.
- This plan only updates parser output and documentation. Neow's Cafe catalog and Swift rendering support should be a separate follow-up plan.
