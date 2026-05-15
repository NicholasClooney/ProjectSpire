# Plan: Extend Data Pipeline to Relics, Potions, Events, Monsters, and Acts

Written against game version: **v0.103.2**

---

## Background

The card pipeline is fully operational:

1. `decompile-sts2.sh` — decompiles the game DLL into one `.cs` file per class under `Lab/decompiled/v<version>/`
2. `extract-sts2-resources.py` — copies/converts game assets from `Lab/unpacked/` to `Lab/resources/` using the `resources.allowlist.yaml` manifest
3. `Lab/parsers/card_parser.py` — pattern-matches decompiled C# → structured JSON in `Lab/data/v<version>/cards/`
4. `create-catalog.py` — reads card JSONs + portraits → searchable catalog in `Lab/catalog/v<version>/`
5. `serve-catalog.py` — REST API over the catalog

This plan extends the same pattern to **relics, potions, events, monsters, and acts**.

---

## Source material per entity type

| Entity | Decompiled C# namespace | Count (v0.103.2) | Localization file | Image source path |
|---|---|---|---|---|
| Relics | `MegaCrit.Sts2.Core.Models.Relics/` | ~295 | `relics.json` | `Lab/unpacked/images/relics/*.png` (+ `beta/`) |
| Potions | `MegaCrit.Sts2.Core.Models.Potions/` | ~64 | `potions.json` | `Lab/unpacked/images/potions/*.png` |
| Events | `MegaCrit.Sts2.Core.Models.Events/` | ~68 | `events.json` | `Lab/unpacked/images/events/*.png` |
| Monsters | `MegaCrit.Sts2.Core.Models.Monsters/` | ~121 | `monsters.json` | `Lab/unpacked/images/monsters/*.png` (+ `beta/`) |
| Acts | `MegaCrit.Sts2.Core.Models.Acts/` | 5 | `acts.json` | (no portrait — config-only entity) |

Pool membership for relics and potions is NOT on the model class — it is declared separately in pool classes:
- `MegaCrit.Sts2.Core.Models.RelicPools/` — `IroncladRelicPool.cs`, `SilentRelicPool.cs`, `DefectRelicPool.cs`, `RegentRelicPool.cs`, `NecrobinderRelicPool.cs`, `SharedRelicPool.cs`, `EventRelicPool.cs`
- `MegaCrit.Sts2.Core.Models.PotionPools/` — same pattern

Card pool membership, by contrast, is a field on each `CardModel` class directly.

---

## Localization key schemas

### Relics
```
<RELIC_ID>.title
<RELIC_ID>.description          — SmartFormat: {VarName:diff()}, [gold]...[/gold]
<RELIC_ID>.flavor               — flavour text (not always present)
<RELIC_ID>.eventDescription     — used when relic appears as event reward (rare)
```

### Potions
```
<POTION_ID>.title
<POTION_ID>.description
<POTION_ID>.selectionScreenPrompt   — shown when potion requires a card choice (not always present)
```

### Monsters
```
<MONSTER_ID>.name
<MONSTER_ID>.moves.<MOVE_ID>.title  — intent name shown in UI
```
Intent titles come from the `MonsterMoveStateMachine` — each `MoveState` has a string ID (e.g., `"KILLSHOT"`) that maps to `<MONSTER_ID>.moves.KILLSHOT.title` in `monsters.json`.

### Events
Nested structure — events have multiple pages and branching options:
```
<EVENT_ID>.pages.<PAGE_ID>.description
<EVENT_ID>.pages.<PAGE_ID>.options.<OPTION_ID>.title
<EVENT_ID>.pages.<PAGE_ID>.options.<OPTION_ID>.description   (sometimes)
<EVENT_ID>.loss                                               (sometimes)
```
Page and option IDs are derived from the localization key string literals passed to `L10NLookup()` and `new EventOption(this, handler, "<key>")` in the C# source.

### Acts
```
<ACT_ID>.title
```

---

## Image naming convention

All entity images follow the same slug pattern as cards: class name converted to snake_case lowercase.

- `Akabeko` → `akabeko.png`
- `AttackPotion` → `attack_potion.png`
- `AbyssalBaths` → `abyssal_baths.png`
- `BattleFriendV1` → `battle_friend_v1.png`

Relics and monsters also have a `beta/` subdirectory for unreleased or alternative art.

Image paths relative to the source root (`Lab/unpacked/`):
- Relics: `images/relics/<slug>.png` (or `images/relics/beta/<slug>.png`)
- Potions: `images/potions/<slug>.png`
- Events: `images/events/<slug>.png`
- Monsters: `images/monsters/<slug>.png` (or `images/monsters/beta/<slug>.png`)

---

## Steps

### Step 1 — Add image entries to `resources.allowlist.yaml`

Add four new entries (in addition to the existing `card_portraits` entry):

```yaml
  - name: relic_images
    from: images/relics
    to: images/relics
    include:
      - "**/*.png"
    exclude:
      - ".DS_Store"
      - "**/*.import"
    transform: webp-q85

  - name: potion_images
    from: images/potions
    to: images/potions
    include:
      - "**/*.png"
    exclude:
      - ".DS_Store"
      - "**/*.import"
    transform: webp-q85

  - name: event_images
    from: images/events
    to: images/events
    include:
      - "**/*.png"
    exclude:
      - ".DS_Store"
      - "**/*.import"
    transform: webp-q85

  - name: monster_images
    from: images/monsters
    to: images/monsters
    include:
      - "**/*.png"
    exclude:
      - ".DS_Store"
      - "**/*.import"
    transform: webp-q85
```

Re-run `extract-sts2-resources.py` to populate `Lab/resources/images/{relics,potions,events,monsters}/`.

### Step 2 — Write `Lab/parsers/relic_parser.py`

**Input:** All `.cs` files in `MegaCrit.Sts2.Core.Models.Relics/` plus all pool files in `MegaCrit.Sts2.Core.Models.RelicPools/`

**What to extract per relic (raw section):**
- `class_name` — from file name
- `rarity` — from `RelicRarity.<Value>` property override
- `pools` — list of pool names derived by scanning pool classes for `ModelDb.Relic<ClassName>()` references. Pool name is the `EnergyColorName` string (or inferred from class name: `IroncladRelicPool` → `ironclad`, `SharedRelicPool` → `shared`, etc.)
- `vars` — from `CanonicalVars` property, same pattern as cards (`new BlockVar(10m)` → `{ "Block": 10 }`)
- `hover_tips` — from `ExtraHoverTips` property (`HoverTipFactory.Static(...)`, `HoverTipFactory.FromPower<...>()`)
- `localization` — derived key: `{ "table": "relics", "title_key": "<ID>.title", "description_key": "<ID>.description" }`
- `assets` — `[{ "kind": "portrait", "path": "Lab/resources/images/relics/<slug>.webp" }]` (add `beta_portrait` if beta file exists)

**What to resolve (resolved section):**
- `title` — from `relics.json`
- `description.plain` + `description.runs[]` — same SmartFormat resolver as cards; `[gold]...[/gold]` tags, `{Var:diff()}` patterns, `[blue]...[/blue]` for numeric values
- `flavor` — from `relics.json` (plain string, no SmartFormat)

**Schema version:** Start at `0.1.0`

**Output:** `Lab/data/v<version>/relics/<slug>.json`

**Verification:** Check a few known relics manually (Anchor → Block 10, Akabeko → VigorPower 8).

### Step 3 — Write `Lab/parsers/potion_parser.py`

**Input:** All `.cs` files in `MegaCrit.Sts2.Core.Models.Potions/` plus pool files in `MegaCrit.Sts2.Core.Models.PotionPools/`

**What to extract (raw section):**
- `class_name`
- `rarity` — from `PotionRarity.<Value>`
- `usage` — from `PotionUsage.<Value>` (`CombatOnly`, `NonCombatOnly`, `Anytime`)
- `target_type` — from `TargetType.<Value>` (`Self`, `AnyEnemy`, etc.)
- `pools` — same pool-class scanning approach as relics
- `vars` — from `CanonicalVars` if present (many potions have none)
- `localization` — derived key: `{ "table": "potions", "title_key": "<ID>.title", "description_key": "<ID>.description" }`
- `assets` — `[{ "kind": "portrait", "path": "Lab/resources/images/potions/<slug>.webp" }]`

**What to resolve:**
- `title`, `description.plain` + `description.runs[]`
- `selection_screen_prompt` — plain string from `potions.json` if present

**Schema version:** Start at `0.1.0`

**Output:** `Lab/data/v<version>/potions/<slug>.json`

### Step 4 — Write `Lab/parsers/monster_parser.py`

**Input:** All `.cs` files in `MegaCrit.Sts2.Core.Models.Monsters/`

**What to extract (raw section):**
- `class_name`
- `hp` — `{ "min": <MinInitialHp>, "max": <MaxInitialHp> }` (some are fixed, i.e., min == max)
- `moves` — list of move state IDs extracted from `MoveState("<ID>", ...)` constructor calls in `GenerateMoveStateMachine()`. Capture the intent class name (e.g., `AttackIntent`, `HiddenIntent`, `BlockIntent`) from the second or third arg.
- `localization` — `{ "table": "monsters", "name_key": "<ID>.name" }`
- `assets` — `[{ "kind": "portrait", "path": "Lab/resources/images/monsters/<slug>.webp" }]` if file exists

**What to resolve:**
- `name` — from `monsters.json` `<ID>.name`
- `moves[]` — for each move ID: `{ "id": "<ID>", "intent": "<IntentClass>", "title": "<ID>.moves.<ID>.title from monsters.json>" }`

**Notes:**
- Filter rule: skip any class whose derived ID has no `name` key in `monsters.json`. This naturally excludes all test/debug helpers (`MultiAttackMoveMonster`, `SingleAttackMoveMonster`, `OneHpMonster`, `TenHpMonster`, `BigDummy`), `DeprecatedMonster`, and non-combat entities like `Architect` — all of which borrow another monster's localization key instead of owning one. No hardcoded exclusion list needed.
- HP of 9999 typically indicates a non-combat scene entity; this is already handled by the filter above, but worth noting.

**Schema version:** Start at `0.1.0`

**Output:** `Lab/data/v<version>/monsters/<slug>.json`

### Step 5 — Write `Lab/parsers/event_parser.py`

**Input:** All `.cs` files in `MegaCrit.Sts2.Core.Models.Events/`

**What to extract (raw section):**
- `class_name`
- `vars` — from `CanonicalVars` if present
- `pages` — list of localization key bases found in `L10NLookup("...")` calls and `SetEventState(L10NLookup("..."), ...)` calls. Extract the literal string argument.
- `options` — per page: list of option localization keys from `new EventOption(this, <handler>, "<key>")` calls
- `localization` — `{ "table": "events" }`
- `assets` — `[{ "kind": "portrait", "path": "Lab/resources/images/events/<slug>.webp" }]` if file exists

**What to resolve:**
- For each page key found: `description.plain` from `events.json`
- For each option key found: `title`, `description` from `events.json`
- `vars` resolved same as cards/relics

**Notes:**
- Events are the most complex entity. The parser should focus on extracting the localization key structure faithfully rather than trying to model branching logic.
- Some events inherit from `AncientEventModel` — capture this in a `kind` field (`"event"` vs `"ancient"`).

**Schema version:** Start at `0.1.0`

**Output:** `Lab/data/v<version>/events/<slug>.json`

### Step 6 — Write `Lab/parsers/act_parser.py`

**Input:** All `.cs` files in `MegaCrit.Sts2.Core.Models.Acts/`

**What to extract (raw section):**
- `class_name`
- `boss_discovery_order` — list of encounter class names from `BossDiscoveryOrder` property
- `ancients` — list of ancient event class names from `AllAncients`
- `events` — list of event class names from `AllEvents`
- `encounters` — list of encounter class names from `AllEncounters` or `GenerateAllEncounters()` if present
- `base_room_count` — from `BaseNumberOfRooms` if present
- `weak_encounter_count` — from `NumberOfWeakEncounters` if present
- `localization` — `{ "table": "acts", "title_key": "<ID>.title" }`

**What to resolve:**
- `title` — from `acts.json`

**Notes:**
- Filter out `DeprecatedAct.cs`.
- Acts reference other classes by name — no need to inline their data; IDs are sufficient.

**Schema version:** Start at `0.1.0`

**Output:** `Lab/data/v<version>/acts/<slug>.json`

### Step 7 — Add run scripts

Add a top-level runner for each parser, analogous to how `card_parser.py` is invoked. These can be standalone scripts in `Lab/scripts/`:

- `create-relic-data.py` — invokes `relic_parser.py` over the decompiled source directory
- `create-potion-data.py`
- `create-monster-data.py`
- `create-event-data.py`
- `create-act-data.py`

Or consolidate all five into a single `create-entity-data.py` with a `--entity` flag.

### Step 8 — Documentation

Add a Lab Documentation file for each new entity type following the `0001 - Title.md` convention. The next available numbers are 0016+. Each file should document:
- The decompiled source structure and key base class fields
- The localization key schema
- Any parser-specific decisions or patterns
- The output JSON schema with an example

---

## Shared infrastructure to reuse unchanged

- `class_name_to_id()` — works for all entity types (same snake-to-upper-slug logic)
- SmartFormat localization resolver — same `[gold]...[/gold]` tags, `{Var:diff()}` patterns apply to relics, potions, events
- `resources.allowlist.yaml` + `extract-sts2-resources.py` — extend by adding entries (Step 1)
- `manifest.json` generation pattern — reuse per output directory

---

## Order of execution (recommended)

1. **Step 1** (allowlist) — unblocks having images on disk before parsers run
2. **Step 2** (relics) — most similar to cards; validates that shared infrastructure extends cleanly
3. **Step 3** (potions) — simpler than relics, validates pool-scanning approach
4. **Step 4** (monsters) — state machine parsing is new but self-contained
5. **Step 5** (events) — most complex localization; tackle after patterns are proven
6. **Step 6** (acts) — simplest; pure configuration extraction
7. **Steps 7–8** — scripts and documentation in parallel with or after parsers

---

## Open questions

- **Relic images not hardcoded in C#:** Unlike cards (which have `assets` declared in the class body), relic portrait paths are convention-based (`images/relics/<slug>.webp`). The parser should derive the path from class name and check existence, rather than parsing it from source.
- **Monster images:** Same convention-based approach. Not all monster classes have a portrait (e.g., mock/composition helpers). Check existence before adding to assets.
- **Event images:** Existence varies. Check before adding.
- **Potion `selectionScreenPrompt`:** Present only for potions that require a card-choice interaction. Resolver should treat it as optional.
- **`AncientEventModel` subclasses:** These are distinct from regular `EventModel` — they appear in `AllAncients` on act classes. Confirm whether they share the same localization key structure as events.
- **Encounter classes** (`MegaCrit.Sts2.Core.Models.Encounters/`) — these represent combat encounters (groups of monsters). Not planned here but referenced by acts and monster pools. A future `encounter_parser.py` would follow the same pattern.
