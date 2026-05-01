# 0001 - Card Data And Text Resolution

> Written on 2026-05-01. Concerns `Lab/parsers/card_parser.py`, generated card JSON, and downstream card renderers such as Neow's Cafe.

## Context

ProjectSpire currently has two related but separate pieces:

- a Python card parser that reads decompiled STS2 card classes and writes JSON under `Lab/data/<version>/cards/`
- a Swift `Card` model in Neow's Cafe that intentionally starts simple for MVP card display

The current parser output is useful for research, but it mixes source-derived facts with convenience values in a few places. The current Swift model renders card descriptions as plain strings, so it cannot yet represent formatted localization output such as colored keywords.

Example target display for Ball Lightning:

```text
Deal 7 damage
Channel 1 Lightning
```

In that rendered text, words such as `Channel` and `Lightning` may need styling such as the game's `[gold]...[/gold]` markup.

## Parser Alias Issue

For `Abrasive`, the decompiled source defines canonical dynamic variables as power variables:

- `ThornsPower`
- `DexterityPower`

The current parser also emits stripped aliases:

- `Thorns`
- `Dexterity`

This happens because `extract_vars()` records both the exact `PowerVar<T>` type name and a suffix-stripped convenience name. That was useful for quick inspection and for aligning with some behavior fields that strip `Power` from applied power names, but it is not source-faithful enough for localization.

Localization formatters such as `diff()` resolve against the canonical dynamic variable names in the localization string. For example:

```json
"ABRASIVE.description": "Gain {DexterityPower:diff()} [gold]Dexterity[/gold].\nGain {ThornsPower:diff()} [gold]Thorns[/gold]."
```

That means the canonical data layer should preserve `DexterityPower` and `ThornsPower` as the dynamic variable identities. Aliases should either move to a clearly separate convenience section or be omitted from first-pass canonical output.

## Proposed Two-Pass Model

Use a two-pass process:

1. First pass: parse raw canonical card data from decompiled source.
2. Second pass: enrich and resolve localization into app-friendly data.

The first pass should stay close to source truth. The second pass can add derived or convenience data for renderers.

## JSON Shape Sketch

The generated JSON should eventually separate raw and resolved sections:

```json
{
  "schema_version": "0.2.0",
  "id": "BALL_LIGHTNING",
  "raw": {
    "class_name": "BallLightning",
    "file": "Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models.Cards/BallLightning.cs",
    "cost": 1,
    "type": "Attack",
    "rarity": "Common",
    "target": "AnyEnemy",
    "localization": {
      "table": "cards",
      "title_key": "BALL_LIGHTNING.title",
      "description_key": "BALL_LIGHTNING.description"
    },
    "vars": {
      "Damage": 7
    },
    "upgrades": [
      {
        "var": "Damage",
        "delta": 3
      }
    ],
    "tips": [
      {
        "kind": "hover_tip_static",
        "target": "Channeling",
        "source": "HoverTipFactory.Static"
      },
      {
        "kind": "hover_tip_orb",
        "target": "LightningOrb",
        "source": "HoverTipFactory.FromOrb"
      }
    ]
  },
  "resolved": {
  }
}
```

The first pass creates the overall shape and fills `raw`. It leaves `resolved` empty.

For now, `raw.vars` stays intentionally simple: canonical variable names mapped to base values. For Ball Lightning, the source constructs a `DamageVar`, but the canonical localization variable name is `Damage`, so first-pass output uses `"Damage": 7`. If ProjectSpire later needs to preserve variable source types, it can add that without reintroducing aliases.

The second pass requires localization data and fills `resolved`. If required localization data is missing, the second pass should fail instead of silently emitting partial display data.

Example second-pass output:

```json
{
  "resolved": {
    "base": {
      "title": "Ball Lightning",
      "cost": 1,
      "description": {
        "plain": "Deal 7 damage\nChannel 1 Lightning",
        "runs": [
          {
            "text": "Deal "
          },
          {
            "text": "7",
            "source_var": "Damage"
          },
          {
            "text": " damage\n"
          },
          {
            "text": "Channel",
            "style": "gold"
          },
          {
            "text": " 1 "
          },
          {
            "text": "Lightning",
            "style": "gold"
          }
        ]
      }
    },
    "upgraded": {
      "title": "Ball Lightning",
      "cost": 1,
      "changed": [
        "description"
      ],
      "description": {
        "plain": "Deal 10 damage\nChannel 1 Lightning",
        "runs": [
          {
            "text": "Deal "
          },
          {
            "text": "10",
            "source_var": "Damage",
            "style": "green"
          },
          {
            "text": " damage\n"
          },
          {
            "text": "Channel",
            "style": "gold"
          },
          {
            "text": " 1 "
          },
          {
            "text": "Lightning",
            "style": "gold"
          }
        ]
      }
    }
  }
}
```

`runs` means contiguous text spans that share the same display attributes. Downstream apps can render these as SwiftUI `Text` fragments, attributed strings, HTML spans, canvas draw calls, or another native representation.

This keeps the card JSON useful for multiple consumers:

- SwiftUI can render `resolved.base.description.runs` as styled text.
- A web app can use the same runs to produce HTML or canvas text.
- Tools can still inspect `raw` when they need source-faithful card facts.

## Tips

Hover tips should be represented separately from text resolution until the game behavior is better understood.

For Ball Lightning, the decompiled card source currently shows two tips:

```json
{
  "raw": {
    "tips": [
      {
        "kind": "hover_tip_static",
        "target": "Channeling",
        "source": "HoverTipFactory.Static"
      },
      {
        "kind": "hover_tip_orb",
        "target": "LightningOrb",
        "source": "HoverTipFactory.FromOrb"
      }
    ]
  }
}
```

These correspond to the in-game Channel and Lightning hover popups, but ProjectSpire should not yet attach those tips to specific text runs. That mapping needs a separate investigation into how the game connects hover tips, localization markup, and rendered text.

## Resolved Upgrades

Upgrades belong in `resolved` as display states, because upgrades can affect more than just dynamic variable values. Description text and energy cost may both change.

For the MVP schema, `resolved.base` and `resolved.upgraded` are enough. Future work can investigate whether more upgrade variants or card states require a more general structure.

```json
"resolved": {
  "base": {
    "title": "Ball Lightning",
    "cost": 1,
    "description": {
      "plain": "Deal 7 damage\nChannel 1 Lightning",
      "runs": [
        { "text": "Deal " },
        { "text": "7", "source_var": "Damage" },
        { "text": " damage\n" },
        { "text": "Channel", "style": "gold" },
        { "text": " 1 " },
        { "text": "Lightning", "style": "gold" }
      ]
    }
  },
  "upgraded": {
    "title": "Ball Lightning",
    "cost": 1,
    "changed": ["description"],
    "description": {
      "plain": "Deal 10 damage\nChannel 1 Lightning",
      "runs": [
        { "text": "Deal " },
        { "text": "10", "source_var": "Damage", "style": "green" },
        { "text": " damage\n" },
        { "text": "Channel", "style": "gold" },
        { "text": " 1 " },
        { "text": "Lightning", "style": "gold" }
      ]
    }
  }
}
```

## Formatter Scope

The resolver does not need to implement the full game localization engine immediately.

An MVP resolver can support the card-description subset first:

- replacement of simple dynamic variables such as `{Damage}` or `{Damage:diff()}`
- line breaks
- simple color tags such as `[gold]...[/gold]`, `[green]...[/green]`, and `[red]...[/red]`
- plain text fallback when a formatter is unknown

Later resolver work can add more of the game's SmartFormat behavior, including conditional and plural formatters.

## Open Questions

- How does the game associate hover tips with rendered text spans?
- Which upgrade behaviors beyond dynamic variable changes and energy cost changes need explicit resolved output?
- Should resolved text expose only source markup styles such as `gold`, `green`, and `red`, or eventually add semantic labels when they can be derived confidently?
