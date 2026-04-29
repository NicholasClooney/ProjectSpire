# 0008 - Card View Assets

> Initial notes from decompiled `v0.103.2` sources.

This document records how the game assembles visible card views and how individual visual components can be extracted from atlas resources.

## Card View Composition

Cards are not rendered from one complete card image.

The visible card is a reusable Godot scene:

```text
res://scenes/cards/card.tscn
```

The scene is controlled by:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Nodes.Cards/NCard.cs
```

`NCard` looks up scene nodes such as:

- `%Portrait`
- `%Frame`
- `%PortraitBorder`
- `%TitleBanner`
- `%TypePlaque`
- `%TitleLabel`
- `%DescriptionLabel`
- `%EnergyIcon`
- `%EnergyLabel`

Relevant code path:

```csharp
_titleLabel = GetNode<MegaLabel>("%TitleLabel");
_descriptionLabel = GetNode<MegaRichTextLabel>("%DescriptionLabel");
_frame = GetNode<TextureRect>("%Frame");
_portrait = GetNode<TextureRect>("%Portrait");
_portraitBorder = GetNode<TextureRect>("%PortraitBorder");
_energyLabel = GetNode<MegaLabel>("%EnergyLabel");
_energyIcon = GetNode<TextureRect>("%EnergyIcon");
_banner = GetNode<TextureRect>("%TitleBanner");
_typePlaque = GetNode<NinePatchRect>("%TypePlaque");
```

`NCard.Reload()` then fills those nodes from the `CardModel`:

```csharp
_portrait.Texture = portrait;
_portraitBorder.Texture = Model.PortraitBorder;
_portraitBorder.Material = Model.BannerMaterial;
_frame.Texture = Model.Frame;
_banner.Material = Model.BannerMaterial;
_banner.Texture = Model.BannerTexture;
_frame.Material = Model.FrameMaterial;
```

So the card is assembled from:

- per-card portrait art
- shared frame textures
- shared portrait-border textures
- shared banner textures
- frame materials selected by card pool / character
- banner materials selected by rarity
- runtime labels for cost, title, type, and description

## Asset Paths

`CardModel` supplies the texture and material paths.

Per-card portrait:

```csharp
public virtual string PortraitPath =>
    ImageHelper.GetImagePath($"atlases/card_atlas.sprites/{Pool.Title.ToLowerInvariant()}/{base.Id.Entry.ToLowerInvariant()}.tres");
```

`ImageHelper.GetImagePath(...)` prefixes the path with `res://images/`, so the final Godot resource path is:

```text
res://images/atlases/card_atlas.sprites/<pool-title>/<card-id-lowercase>.tres
```

For extracted assets, drop the `res://images/` prefix:

```text
images/atlases/card_atlas.sprites/<pool-title>/<card-id-lowercase>.tres
```

The `<card-id-lowercase>` part comes from `base.Id.Entry.ToLowerInvariant()`. The id entry is generated from the card model class name through `ModelDb.GetEntry(type)`, which calls `StringHelper.Slugify(type.Name)`.

For example:

| Card class | Model id entry | Pool title | Portrait resource |
| --- | --- | --- | --- |
| `BallLightning` | `BALL_LIGHTNING` | `defect` | `atlases/card_atlas.sprites/defect/ball_lightning.tres` |

The `<pool-title>` part comes from `CardModel.Pool.Title`. A card does not usually store that directly. `CardModel.Pool` searches `ModelDb.AllCardPools` and picks the first `CardPoolModel` whose `AllCardIds` contains the card id. For `BallLightning`, `DefectCardPool.GenerateAllCards()` includes `ModelDb.Card<BallLightning>()`, and `DefectCardPool.Title` is `defect`.

Some cards override `PortraitPath`, so do not assume the default path formula is universal. `MadScience` is one example:

```csharp
public override string PortraitPath => GetPortraitPath(TinkerTimeType);

private string GetPortraitPath(CardType cardType)
{
    return ImageHelper.GetImagePath("atlases/card_atlas.sprites/event/" + GetPortraitFilename(cardType) + ".tres");
}
```

It can resolve to:

```text
atlases/card_atlas.sprites/event/mad_science_attack.tres
atlases/card_atlas.sprites/event/mad_science_skill.tres
atlases/card_atlas.sprites/event/mad_science_power.tres
```

So the safe rule is: use `CardModel.PortraitPath` as the source of truth. The default implementation maps to `<pool-title>/<card-id-lowercase>.tres`, but overrides can choose specific portrait assets.

Card frame shape by card type:

```csharp
return ImageHelper.GetImagePath(
    "atlases/ui_atlas.sprites/card/card_frame_" +
    cardType.ToString().ToLowerInvariant() +
    "_s.tres");
```

Portrait border shape by card type:

```csharp
return ImageHelper.GetImagePath(
    "atlases/ui_atlas.sprites/card/card_portrait_border_" +
    cardType.ToString().ToLowerInvariant() +
    "_s.tres");
```

Shared title banner:

```csharp
return ImageHelper.GetImagePath("atlases/ui_atlas.sprites/card/card_banner.tres");
```

Relevant source:

```text
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardModel.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/ModelDb.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Helpers/StringHelper.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.CardPools/DefectCardPool.cs
Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/MadScience.cs
```

## Color And Character Differences

The visible character color is mostly controlled by the card pool's frame material. The frame texture itself is shared; the game recolors it with a shader material.

Examples:

```csharp
public sealed class SilentCardPool : CardPoolModel
{
    public override string Title => "silent";
    public override string EnergyColorName => "silent";
    public override string CardFrameMaterialPath => "card_frame_green";
}
```

```csharp
public sealed class IroncladCardPool : CardPoolModel
{
    public override string Title => "ironclad";
    public override string EnergyColorName => "ironclad";
    public override string CardFrameMaterialPath => "card_frame_red";
}
```

```csharp
public sealed class DefectCardPool : CardPoolModel
{
    public override string Title => "defect";
    public override string EnergyColorName => "defect";
    public override string CardFrameMaterialPath => "card_frame_blue";
}
```

`CardPoolModel` converts `CardFrameMaterialPath` to a material path:

```csharp
public string FrameMaterialPath =>
    "res://materials/cards/frames/" + CardFrameMaterialPath + "_mat.tres";

public Material FrameMaterial =>
    PreloadManager.Cache.GetMaterial(FrameMaterialPath);
```

This is why cards from different characters can share the same frame shape while appearing green, red, blue, etc.

The extracted material files live under:

```text
materials/cards/frames/
```

Each frame material is a `ShaderMaterial` that uses:

```text
res://shaders/hsv.gdshader
```

For example, `card_frame_green_mat.tres` contains:

```ini
[gd_resource type="ShaderMaterial" load_steps=2 format=3 uid="uid://056w1pq8p1j"]

[ext_resource type="Shader" path="res://shaders/hsv.gdshader" id="1_6tpt8"]

[resource]
resource_local_to_scene = true
shader = ExtResource("1_6tpt8")
shader_parameter/h = 0.32
shader_parameter/s = 0.45
shader_parameter/v = 1.2
```

`NCard.Reload()` applies both the shared texture and the per-pool material:

```csharp
_frame.Texture = Model.Frame;
_frame.Material = Model.FrameMaterial;
```

So the class color pipeline is:

```text
shared frame atlas sprite + frame HSV material = character-colored card frame
```

Banner colors work the same way, but use rarity-based materials from:

```text
materials/cards/banners/
```

`NCard.Reload()` applies the shared banner texture and the rarity material:

```csharp
_banner.Material = Model.BannerMaterial;
_banner.Texture = Model.BannerTexture;
```

`CardModel.BannerMaterialPath` selects the material by rarity:

```csharp
private string BannerMaterialPath => Rarity switch
{
    CardRarity.Uncommon => "res://materials/cards/banners/card_banner_uncommon_mat.tres",
    CardRarity.Rare => "res://materials/cards/banners/card_banner_rare_mat.tres",
    CardRarity.Curse => "res://materials/cards/banners/card_banner_curse_mat.tres",
    CardRarity.Status => "res://materials/cards/banners/card_banner_status_mat.tres",
    CardRarity.Event => "res://materials/cards/banners/card_banner_event_mat.tres",
    CardRarity.Quest => "res://materials/cards/banners/card_banner_quest_mat.tres",
    CardRarity.Ancient => "res://materials/cards/banners/card_banner_ancient_mat.tres",
    _ => "res://materials/cards/banners/card_banner_common_mat.tres",
};
```

The extracted HSV material values have been recorded in:

```text
material_hsv_variants.json
card_hsv_semantic_variants.json
```

`material_hsv_variants.json` is the raw material scrape. `card_hsv_semantic_variants.json` is the more useful rendering map: it groups the frame materials, banner materials, card pools, and rarity-to-banner rules without depending on local extraction paths.

Current frame material values:

| Material | h | s | v | Used by |
| --- | ---: | ---: | ---: | --- |
| `card_frame_blue` | 0.55 | 0.9 | 1.0 | Defect |
| `card_frame_colorless` | 1.0 | 0.0 | 1.2 | Colorless, Status, Event, Token, Test |
| `card_frame_curse` | 0.85 | 0.05 | 0.55 | Curse |
| `card_frame_green` | 0.32 | 0.45 | 1.2 | Silent |
| `card_frame_orange` | 0.12 | 1.5 | 1.2 | Regent |
| `card_frame_pink` | 0.965 | 0.55 | 1.2 | Necrobinder |
| `card_frame_quest` | 1.0 | 1.0 | 1.0 | Quest |
| `card_frame_red` | 0.025 | 0.85 | 1.0 | Ironclad |

Current banner material values:

| Material | h | s | v | Used by |
| --- | ---: | ---: | ---: | --- |
| `card_banner_ancient` | 0.0 | 0.2 | 0.9 | Ancient |
| `card_banner_common` | 1.0 | 0.0 | 0.85 | None, Basic, Common, Token, Special |
| `card_banner_curse` | 0.27 | 1.1 | 0.9 | Curse |
| `card_banner_event` | 0.875 | 0.85 | 0.9 | Event |
| `card_banner_quest` | 0.515 | 1.727 | 0.9 | Quest |
| `card_banner_rare` | 0.563 | 1.198 | 1.14 | Rare |
| `card_banner_status` | 0.634 | 0.35 | 0.8 | Status |
| `card_banner_uncommon` | 1.0 | 1.0 | 1.0 | Uncommon |

The shader used by both frame and banner materials is:

```text
res://shaders/hsv.gdshader
```

It converts the sampled texture color from RGB to YIQ, rotates the IQ plane by `(1.0 - h) * 2π`, scales saturation by `s`, scales value by `v`, converts back to RGB, then multiplies by the node's modulate color. Reimplementations should use that YIQ hue rotation if the goal is matching the game rather than applying a generic HSB adjustment.

Relevant sources:

- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardPoolModel.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.CardPools/SilentCardPool.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.CardPools/IroncladCardPool.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.CardPools/DefectCardPool.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Nodes.Cards/NCard.cs`
- `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardModel.cs`

## Card Type Shape Differences

Frame and portrait-border shape are selected from `CardType`.

Examples:

- `Attack` uses `card_frame_attack_s.tres` and `card_portrait_border_attack_s.tres`
- `Skill` uses `card_frame_skill_s.tres` and `card_portrait_border_skill_s.tres`
- `Power` uses `card_frame_power_s.tres` and `card_portrait_border_power_s.tres`

For `Status`, `Curse`, and some fallback cases, the code maps the card type to the skill-shaped assets.

This explains why cards can have similar construction but visibly different top/portrait shapes.

## Layout Constraints From `card.tscn`

`NCard` exposes the base card size in code:

```csharp
public static readonly Vector2 defaultSize = new Vector2(300f, 422f);
```

The `card.tscn` scene places most normal-card children around the card center. Treat the center as `(0, 0)` in Godot and `(150, 211)` in a top-left coordinate system.

To convert a node rectangle from Godot offsets to a Swift-style frame:

```text
x = 150 + offset_left
y = 211 + offset_top
width = offset_right - offset_left
height = offset_bottom - offset_top
```

These converted values are top-left frames. In SwiftUI, `.position(x:y:)` uses the view center, so do not pass these `x` and `y` values directly to `.position`. Use a `.topLeading` container with `.offset(x:y:)`, or convert to center coordinates:

```text
center_x = x + width / 2
center_y = y + height / 2
```

Normal card layout:

| Node | Godot offsets | Swift-style frame |
| --- | --- | --- |
| `Frame` | `-150, -211, 150, 211` | `x: 0, y: 0, w: 300, h: 422` |
| `Portrait` | `-125, -168, 125, 22` | `x: 25, y: 43, w: 250, h: 190` |
| `PortraitBorder` | `-137.5, -164, 137.5, 46` | `x: 12.5, y: 47, w: 275, h: 210` |
| `TitleBanner` | `-163, -207, 164, -124` | `x: -13, y: 4, w: 327, h: 83` |
| `TitleLabel` | `-105, -204, 105, -150` | `x: 45, y: 7, w: 210, h: 54` |
| `TypePlaque` | `-30.5, 1, 30.5, 38` | `x: 119.5, y: 212, w: 61, h: 37` |
| `DescriptionLabel` | `-122, 37, 121, 173` | `x: 28, y: 248, w: 243, h: 136` |
| `EnergyIcon` | `-166, -227, -102, -163` | `x: -16, y: -16, w: 64, h: 64` |
| `EnergyLabel` inside icon | `-23, -26, 23, 30` | local `x: 9, y: 6, w: 46, h: 56` |
| `StarIcon` | `-186, -189, -128, -131` | `x: -36, y: 22, w: 58, h: 58` |
| `StarLabel` inside icon | `-14, -20, 14, 20` | local `x: 15, y: 9, w: 28, h: 40` |
| `Enchantment` | `-166, -116, -94, -62` | `x: -16, y: 95, w: 72, h: 54` |

Ancient card layout differs from normal cards. `NCard.Reload()` hides `Portrait`, `PortraitBorder`, `Frame`, and `TitleBanner`, then shows `AncientPortrait`, `AncientBorder`, `AncientTextBg`, and `AncientBanner`.

Ancient card layout:

| Node | Godot offsets / scale | Swift-style frame |
| --- | --- | --- |
| `AncientPortrait` | `-153, -215, 445, 627`, scale `0.5` | `x: -3, y: -4, w: 299, h: 421` |
| `AncientHighlight` | `-156, -220, 154, 217` | `x: -6, y: -9, w: 310, h: 437` |
| `AncientBorder` | `-154, -223, 152, 217` | `x: -4, y: -12, w: 306, h: 440` |
| `AncientTextBg` | `-132, -20, 132, 183` | `x: 18, y: 191, w: 264, h: 203` |
| `AncientBanner` | `-163, -207, 164, -124` | `x: -13, y: 4, w: 327, h: 83` |

`AncientTextBg` uses a type-specific texture: `ancient_card_text_bg_attack`, `ancient_card_text_bg_skill`, or `ancient_card_text_bg_power`. Quest, Curse, and Status can use the skill background as the closest shape fallback.

Runtime layout rules from `NCard`:

- `TypePlaque` is dynamically widened to `max(typeLabel.width + 17, 61)` and then recentered on its original midpoint.
- The enchantment tab uses its scene position when the card has a star cost. If there is no star cost, it moves up by `45`.
- The title, cost, star cost, type, enchantment amount, and description labels use `MegaLabel` / `MegaRichTextLabel` auto-sizing rather than fixed font sizes only.
- `DescriptionLabel` is written as centered BBCode: `"[center]" + description + "[/center]"`.
- Normal cards show `Portrait`, `PortraitBorder`, `Frame`, and `TitleBanner`; Ancient cards hide those normal pieces and show `AncientPortrait`, `AncientBorder`, `AncientTextBg`, and `AncientBanner` instead.

Important font settings from the scene:

| Label | Font | Max size | Min size | Notes |
| --- | --- | ---: | ---: | --- |
| `TitleLabel` | `kreon_regular_shared` variation | 26 | auto label default | centered, outline size 12, shadow offset 2 |
| `DescriptionLabel` | `kreon_regular_shared` | 21 | 12 | BBCode, centered, line separation `-3` |
| `TypeLabel` | `kreon_bold_shared` | 16 | 10 | centered |
| `EnergyLabel` | `kreon_bold_shared` | 32 | 22 | outline size 16 |
| `StarLabel` | `kreon_bold_shared` | 22 | 16 | outline size 12 |

The extracted atlas PNGs are larger than the logical card size. For example, a frame crop can be roughly `598x844`, while the scene draws it into `300x422`. For Swift, either mark the extracted assets with an appropriate image scale or draw them into the logical frames above.

## Recreating The Card View In Swift

A close SwiftUI recreation should follow the same layering model as `NCard`:

1. Draw the portrait art in the `Portrait` rectangle.
2. Draw the full `Frame` texture over the card and apply the selected frame HSV material.
3. Draw the `PortraitBorder` texture over the portrait and apply the selected banner HSV material.
4. Draw the `TitleBanner` texture and apply the selected banner HSV material.
5. Draw the type plaque and text.
6. Draw cost icons and cost labels.
7. Draw title and description labels with autosizing and outlines.

Use a fixed top-leading card canvas and place converted `card.tscn` frames with `.offset(x:y:)`:

```swift
struct CardView: View {
    var body: some View {
        ZStack(alignment: .topLeading) {
            Image(.ballLightning)
                .resizable()
                .frame(width: 250, height: 190)
                .offset(x: 25, y: 43)

            Image(.cardFrameAttackS)
                .resizable()
                .frame(width: 300, height: 422)
                .offset(x: 0, y: 0)

            Image(.cardPortraitBorderAttackS)
                .resizable()
                .frame(width: 275, height: 210)
                .offset(x: 12.5, y: 47)

            Image(.cardBanner)
                .resizable()
                .frame(width: 327, height: 83)
                .offset(x: -13, y: 4)
        }
        .frame(width: 300, height: 422, alignment: .topLeading)
    }
}
```

If using `.position`, convert each top-left frame to a center first. For example, the portrait frame `x: 25, y: 43, w: 250, h: 190` becomes `.position(x: 150, y: 138)`.

The frame color comes from the card pool:

```text
card pool -> CardFrameMaterialPath -> materials/cards/frames/<name>_mat.tres -> h/s/v
```

The banner color comes from card rarity:

```text
card rarity -> materials/cards/banners/card_banner_<rarity>_mat.tres -> h/s/v
```

For 1:1 color behavior, use a Core Image or Metal shader that mirrors `hsv.gdshader`'s YIQ transform. A generic SwiftUI `.hueRotation()` plus `.saturation()` is easier, but it will not exactly match because Godot's shader rotates in YIQ and applies value before converting back to RGB.

The extracted asset folder should contain the card component PNGs and both HSV JSON files. The repo docs intentionally refer to those files by name only, not by a local absolute path.

## Extracting Individual Components From An Atlas

If the extracted game assets include the `.tres` resource files and source atlas image, the easiest way to extract a component is to read the `.tres` file.

Godot atlas texture resources usually encode:

- the source atlas image
- the rectangle inside that atlas

A typical text `.tres` shape is:

```ini
[gd_resource type="AtlasTexture"]

[ext_resource type="Texture2D" path="res://images/packed/ui_atlas.png" id="1"]

[resource]
atlas = ExtResource("1")
region = Rect2(123, 456, 300, 422)
```

That means the component is the rectangle:

```text
x = 123
y = 456
w = 300
h = 422
```

cropped from:

```text
res://images/packed/ui_atlas.png
```

### ImageMagick extraction

Once the atlas image and rectangle are known, crop with ImageMagick:

```bash
magick ui_atlas.png -crop 300x422+123+456 card_frame_attack_s.png
```

### Godot extraction

Godot can load the `AtlasTexture` directly, which avoids manually parsing the `.tres` file:

```gdscript
var tex := load("res://atlases/ui_atlas.sprites/card/card_frame_attack_s.tres") as AtlasTexture
var image := tex.atlas.get_image()
var crop := image.get_region(tex.region)
crop.save_png("res://exports/card_frame_attack_s.png")
```

For batch extraction, iterate every `.tres` under:

```text
res://atlases/ui_atlas.sprites/card/
```

Load each as `AtlasTexture`, crop `tex.region` from `tex.atlas`, and save a PNG named after the `.tres` file.

## Practical Notes

The decompiled C# references the asset paths, but this repository may not contain the original Godot `.tres` atlas resources or atlas PNG files.

If only decompiled C# is present, the code tells us which assets the game expects, but not the pixel rectangles. To extract the actual component images, we need the extracted Godot resources from the game package, including both:

- the `AtlasTexture` `.tres` resources
- the source atlas PNG or imported texture resource they reference
