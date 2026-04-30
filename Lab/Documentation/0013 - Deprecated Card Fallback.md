# Deprecated Card Fallback

STS2 has an explicit `DeprecatedCard` class used as a fallback when a saved card ID no longer resolves to a real card model.

The save-loading path uses:

```csharp
SaveUtil.CardOrDeprecated(save.Id)
```

That method returns the real card model when it exists, otherwise it returns `ModelDb.Card<DeprecatedCard>()`.

This means:

- "Deprecated card" is a fallback model, not a flag on normal card classes.
- Normal card classes are not marked with a `Deprecated` card type or rarity.
- A missing or removed card ID in save data can deserialize as `DeprecatedCard`.

`DeprecatedCard` itself is defined as a hidden status card:

```csharp
: base(0, CardType.Status, CardRarity.Status, TargetType.None, shouldShowInCardLibrary: false)
```

Relevant sources:

- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/DeprecatedCard.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Saves/SaveUtil.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardModel.cs`
