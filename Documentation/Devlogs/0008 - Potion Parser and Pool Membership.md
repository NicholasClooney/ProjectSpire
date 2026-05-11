# 0008 - Potion Parser and Pool Membership

Date: 2026-05-11

## Context

Extended the STS2 data pipeline to cover potions. Potions are simpler than cards in some ways (no upgrade states, no energy cost modeling), but pool membership is more complex: character-specific pools delegate to epoch files rather than inlining potion lists directly.

## Changes

`Lab/parsers/potion_parser.py` is a new parser following the same `raw`/`resolved` two-part shape used by the card and relic parsers.

**Raw fields extracted from decompiled C#:**
- Rarity (`PotionRarity.X`)
- Usage (`PotionUsage.X`) — `AnyTime`, `Automatic`, `CombatOnly`
- Target type (`TargetType.X`) — last match used to handle conditional property bodies
- Pool membership (from `*PotionPool.cs` and epoch files)
- DynamicVar values and hover tips (via shared `common.py` utilities)
- Image asset path if a WebP exists under `Lab/resources/images/potions/`

**Resolved fields from localization:**
- Title, description (as structured `ResolvedText`)
- `selectionScreenPrompt` if present

**Pool map loading** is the interesting part. Shared and generic pools (`*PotionPool.cs`) contain direct `ModelDb.Potion<ClassName>()` calls. Character-specific pools reference `{CharacterName}Epoch.Potions` instead of inlining the list. The parser reads the referenced epoch file and extracts the `ModelDb.Potion<>()` calls from there. Pool names are derived from the pool class name with the `PotionPool` suffix stripped and lowercased.

The epoch path is `MegaCrit.Sts2.Core.Timeline.Epochs/` within the decompiled version directory.

**Images** were extracted from `Lab/unpacked/images/potions/` and converted to WebP at q85. 64 images produced. One potion (`DEPRECATED_POTION`) has no image, noted in output but not an error.

**Resources allowlist** gained a `potion_images` entry.

## Results

64 potion files written to `Lab/data/v0.103.2/potions/`. All 64 have full pool membership. 5 potions have a `selectionScreenPrompt` (potions that prompt target selection).

## Verification

```sh
python3 Lab/parsers/potion_parser.py --version v0.103.2
# Wrote 64 potion files to Lab/data/v0.103.2/potions in ~0.05s
```
