# Ancient Card Only Determined by Rarity

An STS2 card is "ancient" only when its `Rarity` is `CardRarity.Ancient`.

`Ancient` is not a `CardType` value. The card type enum contains `Attack`, `Skill`, `Power`, `Status`, `Curse`, `Quest`, and `None`.

Example constructor pattern from decompiled card classes:

```csharp
: base(1, CardType.Skill, CardRarity.Ancient, TargetType.Self)
```

This means:

- Check `Rarity == CardRarity.Ancient` to detect an ancient card.
- Do not check `Type` for `Ancient`; no such card type exists.

Related docs:

- `Lab/Documentation/0009 - Card Rarity.md`
- `Lab/Documentation/0011 - Card Type.md`
