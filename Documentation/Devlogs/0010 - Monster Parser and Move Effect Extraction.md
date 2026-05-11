# 0010 - Monster Parser and Move Effect Extraction

Date: 2026-05-11

## Context

Extended the data pipeline to cover monsters. This was the most technically involved parser: monsters have HP values that may be ascension-scaled, move state machines driven by C# code, and handler methods that encode block, power, status card, and heal effects. The goal was to extract all of that into structured JSON without resorting to a runtime simulation.

## Changes

`Lab/parsers/monster_parser.py` was built in two stages.

**Stage 1 (v0.1.0):** HP extraction and localization-derived moves.

- HP extracted as `{min, max, min_ascension, max_ascension}`. Three patterns handled: simple integer (`=> 75;`), ascension-scaled (`AscensionHelper.GetValueIfAscension(level, asc, base)`), and cross-reference (`MaxInitialHp => MinInitialHp`).
- Monsters with no `{id}.name` key in localization are skipped (test helpers, deprecated entries, non-combat entities).
- Move IDs and titles derived from localization keys (`{id}.moves.{move_id}.title`), not from the C# state machine (whose internal IDs often differ from localization IDs).
- Image assets referenced if WebP exists under `Lab/resources/images/monsters/`.

**Stage 2 (v0.2.0):** Full move effect extraction.

The C# state machine is now parsed to extract per-move effect data. The approach:

1. **Symbol table**: parse all `const int`, `=> N`, and `=> AscensionHelper.GetValueIfAscension(level, asc, base)` property declarations. Used to resolve named expressions like `HammerUppercutDamage` to `(base=8, ascension=10)`.

2. **State machine parsing**: extract `new MoveState("ID", HandlerName, intents...)` from `GenerateMoveStateMachine()`. The handler name is used to find the method body. Intent constructors are parsed with paren-balanced extraction to handle lambda args like `() => CurrentPressureGunDamage`.

3. **Handler body extraction**: brace-counted extraction of async handler method bodies.

4. **Effect extraction** from handler bodies:
   - `CreatureCmd.GainBlock(_, amount, ...)` → block value
   - `PowerCmd.Apply<PowerName>(_, amount, ...)` → power name (suffix-stripped) and amount
   - `CardPileCmd.AddToCombatAndPreview<Card>(_, PileType.X, count, ...)` → card type, pile, count
   - `CreatureCmd.Heal(_, amount)` → heal value

5. **Expression resolution**: resolves simple integers, named properties from the symbol table, `Prop * expr` (extracts the LHS), and falls back to first numeric token. Handles decimal suffix `m`.

6. **ID matching**: maps localization move IDs to C# handler names via four fallbacks in order: exact C# ID match (for monsters where loc keeps `_MOVE` suffix), `_MOVE`-stripped match (the common case), case-insensitive match (for mixed-case loc IDs like `Crash`), and dotted-to-underscore conversion (for nested loc IDs like `TACKLE.WEAKENING_SPORES`).

**Intent kinds recognized:** `SingleAttack`, `MultiAttack`, `Defend`, `Buff`, `Debuff`, `Status`, `Heal`, `Hidden`, `Stun`, `Escape`, `Summon`, `Sleep`, `CardDebuff`, `DeathBlow`.

**Why intents and powers are separate fields.** Intents come from the `MoveState` constructor — they are the UI indicators the game shows above the monster to telegraph what it will do. Powers (block, applied powers, status cards, heal) come from parsing the handler method body — they are the actual mechanical effects. These are structurally distinct sources and have different semantics: intents are the display layer, handler effects are the mechanics layer. Merging them would require inferring which intent corresponds to which effect by position, which can be wrong. For example, a move with `[SingleAttack, Debuff, Buff]` intents and `[WeakPower(1), SteamEruptionPower(3)]` powers has no structural guarantee that `Debuff` maps to `Weak` and `Buff` maps to `SteamEruption` — it's true for that monster, but the C# enforces nothing. Keeping them separate preserves fidelity to the source.

**Images** are sparse. Most monster visuals are Spine animations stored as atlas PNGs, not standalone images. Only 4 monsters have portrait WebP files; 18 have beta portrait files. Extracting usable static images for the remaining monsters would require parsing the Spine `.atlas` text files to locate idle-frame sprite coordinates and cropping from the corresponding atlas PNG using something like Pillow. This work is not yet started; the atlas files live under `Lab/unpacked/animations/monsters/<slug>/`.

**Resources allowlist** gained a `monster_images` entry.

## Results

113 monster files written to `Lab/data/v0.103.2/monsters/`. 97 of 113 monsters have fully enriched move effects. The remaining 16 without enrichment break down as:
- 4 allies/NPCs with only a `NOTHING` placeholder move
- 12 with genuine naming mismatches between localization and C# state machine IDs (e.g. `BOWLBUG_SILK`'s localization calls moves `SPIN_WEB`/`THRASH`, while C# uses `TOXIC_SPIT_MOVE`/`TRASH_MOVE`)

51 monsters have ascension-scaled HP. 1 monster (`TEST_SUBJECT`) has an HP property that references another named property (`FirstFormHp`) and cannot be statically resolved; a note is emitted.

## Verification

```sh
python3 Lab/parsers/monster_parser.py --version v0.103.2
# Wrote 113 monster files to Lab/data/v0.103.2/monsters in 0.056s
```

Sample enriched move (Axebot's Hammer Uppercut):

```json
{
  "id": "HAMMER_UPPERCUT",
  "title": "Hammer Uppercut",
  "effects": {
    "intents": [
      { "kind": "SingleAttack", "damage": 8, "damage_ascension": 10 },
      { "kind": "Debuff" }
    ],
    "powers": [
      { "name": "Weak", "amount": 1 },
      { "name": "Frail", "amount": 1 }
    ]
  }
}
```
