# Card Rarity

STS2 defines card rarity in the decompiled core assembly:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardRarity.cs
```

The enum is:

```csharp
public enum CardRarity
{
    None,
    Basic,
    Common,
    Uncommon,
    Rare,
    Ancient,
    Event,
    Token,
    Status,
    Curse,
    Quest
}
```

## Rarity Upgrade Ladder

The upgrade ladder is implemented in:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardRarityExtensions.cs
```

`GetNextHighestRarity()` maps only the normal card-reward rarities upward:

| Input | Next highest rarity |
| --- | --- |
| `None` | `None` |
| `Basic` | `Common` |
| `Common` | `Uncommon` |
| `Uncommon` | `Rare` |
| `Rare` | `None` |
| `Status` | `None` |
| `Curse` | `None` |
| `Event` | `None` |
| `Token` | `None` |
| `Quest` | `None` |
| `Ancient` | `None` |

This means `Basic`, `Common`, `Uncommon`, and `Rare` are the only rarities that participate in the normal upward rarity progression. Special rarities terminate at `None`.

## Localization Keys

`CardRarityExtensions.ToLocString()` maps rarity values to `gameplay_ui` localization keys:

| Rarity | Localization key |
| --- | --- |
| `Basic` | `CARD_RARITY.BASIC` |
| `Common` | `CARD_RARITY.COMMON` |
| `Uncommon` | `CARD_RARITY.UNCOMMON` |
| `Rare` | `CARD_RARITY.RARE` |
| `Status` | `CARD_RARITY.STATUS` |
| `Curse` | `CARD_RARITY.CURSE` |
| `Event` | `CARD_RARITY.EVENT` |
| `Token` | `CARD_RARITY.TOKEN` |
| `Quest` | `CARD_RARITY.QUEST` |
| `Ancient` | `CARD_RARITY.ANCIENT` |

`None` is defined in the enum but is not mapped by `ToLocString()`.

## Parsed Card Data

The parser output in:

```text
Lab/data/v0.103.2/cards/*.json
```

currently contains these rarity values:

| Rarity | Count |
| --- | ---: |
| `Ancient` | 18 |
| `Basic` | 19 |
| `Common` | 100 |
| `Curse` | 18 |
| `Event` | 19 |
| `Quest` | 3 |
| `Rare` | 155 |
| `Status` | 16 |
| `Token` | 10 |
| `Uncommon` | 219 |

`None` exists in the enum, but it does not appear as a parsed rarity in the v0.103.2 card JSON.

## Rendering Notes

Card rarity also drives banner material selection in the card view pipeline. That rendering path is documented in:

```text
Lab/Documentation/0008 - Card View Assets.md
```

The banner-material mapping in `CardModel.BannerMaterialPath` handles special rarity colors for `Uncommon`, `Rare`, `Curse`, `Status`, `Event`, `Quest`, and `Ancient`. All other rarities fall back to the common banner material.
