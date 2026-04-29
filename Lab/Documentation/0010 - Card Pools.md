# Card Pools

STS2 defines card pools in the decompiled core assembly:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.CardPools/
```

The base type is:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardPoolModel.cs
```

`CardPoolModel` is the card-pool contract. Each concrete pool provides:

```csharp
public abstract string Title { get; }
public abstract string EnergyColorName { get; }
public abstract string CardFrameMaterialPath { get; }
public abstract Color DeckEntryCardColor { get; }
public abstract bool IsColorless { get; }

protected abstract CardModel[] GenerateAllCards();
```

`AllCards` is generated once from `GenerateAllCards()`, then extended with modded models:

```csharp
_allCards = GenerateAllCards();
_allCards = ModHelper.ConcatModelsFromMods(this, _allCards).ToArray();
```

## Pool Definitions

Current decompiled pool classes:

| Pool class | Title | Energy color | Frame material | Is colorless | Vanilla card count |
| --- | --- | --- | --- | --- | ---: |
| `IroncladCardPool` | `ironclad` | `ironclad` | `card_frame_red` | `false` | 87 |
| `SilentCardPool` | `silent` | `silent` | `card_frame_green` | `false` | 88 |
| `RegentCardPool` | `regent` | `regent` | `card_frame_orange` | `false` | 88 |
| `NecrobinderCardPool` | `necrobinder` | `necrobinder` | `card_frame_pink` | `false` | 88 |
| `DefectCardPool` | `defect` | `defect` | `card_frame_blue` | `false` | 88 |
| `ColorlessCardPool` | `colorless` | `colorless` | `card_frame_colorless` | `true` | 64 |
| `CurseCardPool` | `curse` | `colorless` | `card_frame_curse` | `false` | 18 |
| `DeprecatedCardPool` | `token` | `colorless` | `card_frame_colorless` | `true` | 1 |
| `EventCardPool` | `event` | `colorless` | `card_frame_colorless` | `true` | 27 |
| `QuestCardPool` | `quest` | `colorless` | `card_frame_quest` | `false` | 3 |
| `StatusCardPool` | `status` | `colorless` | `card_frame_colorless` | `false` | 11 |
| `TokenCardPool` | `token` | `colorless` | `card_frame_colorless` | `true` | 14 |
| `MockCardPool` | `test` | `colorless` | `card_frame_colorless` | `false` | 12 |

`MockCardPool` exists in the pool namespace, but it is not listed in `ModelDb.AllSharedCardPools`. It is used by debug/deprecated character flows and as a fallback in `CardModel.Pool`.

## Character And Shared Pools

`ModelDb` builds the complete card-pool list from character pools plus shared pools:

```csharp
public static IEnumerable<CardPoolModel> AllCardPools =>
    AllCharacterCardPools.Concat(AllSharedCardPools).Distinct();
```

Character pools come from the character models:

```csharp
public static IEnumerable<CardPoolModel> AllCharacterCardPools =>
    AllCharacters.Select((CharacterModel c) => c.CardPool);
```

The five character models are:

```csharp
Character<Ironclad>(),
Character<Silent>(),
Character<Regent>(),
Character<Necrobinder>(),
Character<Defect>()
```

Each character points at its card pool. For example, `Ironclad` defines:

```csharp
public override CardPoolModel CardPool => ModelDb.CardPool<IroncladCardPool>();
```

Shared pools are listed explicitly in `ModelDb.AllSharedCardPools`:

```csharp
CardPool<ColorlessCardPool>(),
CardPool<CurseCardPool>(),
CardPool<DeprecatedCardPool>(),
CardPool<EventCardPool>(),
CardPool<QuestCardPool>(),
CardPool<StatusCardPool>(),
CardPool<TokenCardPool>()
```

## Card Membership

Vanilla card membership is defined in each pool's `GenerateAllCards()` method.

For example, `IroncladCardPool.GenerateAllCards()` returns:

```csharp
return new CardModel[87]
{
    ModelDb.Card<Aggression>(),
    ModelDb.Card<Anger>(),
    ModelDb.Card<Armaments>(),
    ...
    ModelDb.Card<StrikeIronclad>(),
    ...
};
```

Cards do not store their pool directly as a simple constructor field. `CardModel.Pool` resolves the pool lazily by scanning all known pools for one whose `AllCardIds` contains the card's `ModelId`:

```csharp
_pool = ModelDb.AllCardPools.FirstOrDefault(
    (CardPoolModel pool) => pool.AllCardIds.Contains(base.Id));
```

If that fails, it checks `MockCardPool`. If the card still is not found, it throws:

```csharp
throw new InvalidProgramException($"Card {this} is not in any card pool!");
```

## Visual Pool

Rendering generally uses `CardModel.VisualCardPool`, which defaults to `Pool`:

```csharp
public virtual CardPoolModel VisualCardPool => Pool;
```

Some cards can override `VisualCardPool` to render as a different pool color from their membership pool. For example, `Rebound` and `HelloWorld` override it to use `DefectCardPool`.

The frame-color rendering path is documented in:

```text
Lab/Documentation/0008 - Card View Assets.md
```

In short:

```text
card pool -> CardFrameMaterialPath -> materials/cards/frames/<name>_mat.tres -> h/s/v
```

## Modded Cards

The mod-loading notes document `ModHelper.AddModelToPool<TPool, TModel>()` as the mod API for registering custom cards, relics, monsters, powers, and similar models.

Because `CardPoolModel.AllCards` appends `ModHelper.ConcatModelsFromMods(this, _allCards)`, modded cards are expected to become pool members through that mod model registry path rather than by editing vanilla `GenerateAllCards()` arrays.
