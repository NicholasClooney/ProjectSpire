# 0009 - Event Parser with Pages and Ancient Events

Date: 2026-05-11

## Context

Extended the data pipeline to cover events. Events fall into two distinct categories: regular events (subclass `EventModel`, localized in `events.json`) and ancient events (subclass `AncientEventModel`, localized in `ancients.json`). The parser handles both, with different resolution paths.

## Changes

`Lab/parsers/event_parser.py` is a new parser producing the same `raw`/`resolved` structure.

**Raw fields extracted from C#:**
- Kind: `event` or `ancient`
- DynamicVar values (via shared `common.py` `extract_vars`)
- Image asset reference if a WebP exists under `Lab/resources/images/events/`

The C# state machine for regular events is not parsed — it is too dynamic (conditional branches, multi-step transitions) to yield a reliable static page sequence. Page and option structure is derived entirely from localization keys.

**Resolved structure for regular events:**
- Title (from `{id}.title`)
- Loss text (from `{id}.loss`, if present)
- Pages (dict keyed by page ID: `INITIAL`, `DONE`, etc.)
  - Each page has a `description` and an `options` dict keyed by option ID
  - Pages and options are derived by scanning all keys under `{id}.pages.*`
  - Omitted if both description and options are empty

`INITIAL` is the universal page (present in all 59 regular events). Additional pages (`DONE`, `GOBLIN`, etc.) are event-specific.

**Ancient events** use a different dialogue system with no standard `events.json` keys. Their localization lives in `ancients.json` under `{id}.epithet` (used as the title), `{id}.talk.*` (character-specific dialogue, skipped), and sometimes `{id}.pages.*`. The parser emits `kind: ancient` and resolves whatever localization is present in `ancients.json`.

**Images** were extracted from `Lab/unpacked/images/events/` and converted to WebP at q85. 55 of 68 events have a portrait asset. The remaining 13 are ancient events or events with no standalone image (they use composite or UI-only assets).

**Resources allowlist** gained an `event_images` entry.

## Results

68 event files written to `Lab/data/v0.103.2/events/` (59 regular, 9 ancient). 58 regular events have page data. Orobas and The Architect (ancient events) also resolve pages from `ancients.json`. Events with deprecated or unreleased localization keys emit a note in `raw.notes`.

## Verification

```sh
python3 Lab/parsers/event_parser.py --version v0.103.2
# Wrote 68 event files to Lab/data/v0.103.2/events in ~0.1s
```
