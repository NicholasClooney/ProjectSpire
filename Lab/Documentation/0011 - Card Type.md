# Card Type

STS2 defines card type in the decompiled core assembly:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardType.cs
```

The enum is:

```csharp
public enum CardType
{
    None,
    Attack,
    Skill,
    Power,
    Status,
    Curse,
    Quest
}
```

## Where Type Comes From

Most card classes pass their type into the `CardModel` base constructor:

```csharp
protected CardModel(int canonicalEnergyCost, CardType type, CardRarity rarity, TargetType targetType, bool shouldShowInCardLibrary = true)
{
    CanonicalEnergyCost = canonicalEnergyCost;
    Type = type;
    Rarity = rarity;
    TargetType = targetType;
    ShouldShowInCardLibrary = shouldShowInCardLibrary;
}
```

Example:

```csharp
public BallLightning()
    : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy)
{
}
```

Some special cards can override `Type`. `MadScience` is one example: its portrait and type depend on runtime state.

## Localization Keys

`CardTypeExtensions.ToLocString()` maps type values to `gameplay_ui` localization keys:

| Type | Localization key |
| --- | --- |
| `Attack` | `CARD_TYPE.ATTACK` |
| `Skill` | `CARD_TYPE.SKILL` |
| `Power` | `CARD_TYPE.POWER` |
| `Status` | `CARD_TYPE.STATUS` |
| `Curse` | `CARD_TYPE.CURSE` |
| `Quest` | `CARD_TYPE.QUEST` |

`None` is defined in the enum but is not mapped by `ToLocString()`.

## Parsed Card Data

The parser output in:

```text
Lab/data/v0.103.2/cards/*.json
```

currently contains these type values:

| Type | Count |
| --- | ---: |
| `Attack` | 196 |
| `Curse` | 18 |
| `Power` | 112 |
| `Quest` | 3 |
| `Skill` | 232 |
| `Status` | 16 |

`None` exists in the enum, but it does not appear as a parsed card type in the v0.103.2 card JSON.

## Rendering Effects

Card type controls the frame and portrait-border shape.

`CardModel.FramePath` maps type to frame texture:

| Card type | Frame shape |
| --- | --- |
| `Attack` | `card_frame_attack_s.tres` |
| `Skill` | `card_frame_skill_s.tres` |
| `Power` | `card_frame_power_s.tres` |
| `Quest` | `card_frame_quest_s.tres` |
| `Status` | skill frame |
| `Curse` | skill frame |
| `None` | skill frame |

`CardModel.PortraitBorderPath` maps type to portrait-border texture:

| Card type | Portrait border shape |
| --- | --- |
| `Attack` | `card_portrait_border_attack_s.tres` |
| `Skill` | `card_portrait_border_skill_s.tres` |
| `Power` | `card_portrait_border_power_s.tres` |
| `Quest` | skill portrait border |
| `Status` | skill portrait border |
| `Curse` | skill portrait border |
| `None` | skill portrait border |

The general path formulas are:

```text
res://images/atlases/ui_atlas.sprites/card/card_frame_<type>_s.tres
res://images/atlases/ui_atlas.sprites/card/card_portrait_border_<type>_s.tres
```

The type text shown on the card is rendered by `NCard.UpdateTypePlaque()`:

```csharp
_typeLabel.SetTextAutoSize(Model.Type.ToLocString().GetFormattedText());
```

The plaque material uses `Model.BannerMaterial`, so its color follows rarity, not card type.

## Runtime Behavior

Card type is also used outside rendering. One notable branch is power-card play VFX: `CardModel` checks `Type == CardType.Power` and plays the power-card fly animation path for powers.

`TargetType` is separate from `CardType`. For example, an `Attack` can target `AnyEnemy`, while a `Skill` or `Power` can have other target rules. Do not infer targeting only from card type.

## Relevant Sources

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardType.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardTypeExtensions.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardModel.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Nodes.Cards/NCard.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/BallLightning.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/MadScience.cs
```
