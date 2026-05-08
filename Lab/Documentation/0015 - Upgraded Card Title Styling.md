# 0015 - Upgraded Card Title Styling

> Written against v0.103.2

## Summary

Upgraded cards show a `+` suffix on their title and render it in green. Both behaviors are hard-coded in engine C#, not driven by card data.

## Title suffix

`CardModel.Title` (`MegaCrit.Sts2.Core.Models/CardModel.cs`) applies the suffix at the model layer:

```csharp
public string Title
{
    get
    {
        LocString titleLocString = TitleLocString;
        if (!IsUpgraded)
            return titleLocString.GetFormattedText();
        if (MaxUpgradeLevel > 1)
            return $"{titleLocString.GetFormattedText()}+{CurrentUpgradeLevel}";
        return titleLocString.GetFormattedText() + "+";
    }
}
```

- `upgradeLevel == 0` (not upgraded): plain title
- `upgradeLevel > 0` and `MaxUpgradeLevel == 1` (typical card): `"Title+"`
- `upgradeLevel > 0` and `MaxUpgradeLevel > 1` (multi-level card): `"Title+N"` where N is the current level

## Title color

`NCard.UpdateTitleLabel()` (`MegaCrit.Sts2.Core.Nodes.Cards/NCard.cs`) switches the title label color based on upgrade state:

```csharp
else if (Model.CurrentUpgradeLevel == 0)
{
    textAutoSize = Model.Title;
    color = StsColors.cream;
    color2 = GetTitleLabelOutlineColor();   // rarity-based outline
}
else
{
    textAutoSize = Model.Title;
    color = StsColors.green;                // #7FFF00
    color2 = StsColors.cardTitleOutlineSpecial; // #1B6131FF
}
```

Colors from `StsColors.cs`:

| Purpose | Hex |
|---|---|
| Upgraded title fill | `#7FFF00` |
| Upgraded title outline | `#1B6131` |
| Default title fill (cream) | driven by rarity/pool — approximately `#F5F5F0` |
| Default title outline | rarity-based (common `#4D4B40`, uncommon `#005C75`, rare `#6B4B00`, …) |
