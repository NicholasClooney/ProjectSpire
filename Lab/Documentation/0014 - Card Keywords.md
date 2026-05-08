# 0014 - Card Keywords

> Written on 2026-05-08. Concerns `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/`, `Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Models/CardModel.cs`, `Lab/parsers/card_parser.py`, generated card JSON, and downstream app catalog/renderers.

## Summary

Slay the Spire 2 represents card keywords as structured `CardKeyword` values on `CardModel`, not as ordinary card description localization text.

The game then composes keyword lines into the visible card rules text at render time:

- some keywords are inserted before the localized description
- some keywords are appended after the localized description
- keyword text is localized from `card_keywords.json`

ProjectSpire's card parser captures base keyword membership in `raw.keywords`, direct upgrade keyword mutations in `raw.keyword_upgrades`, and localized per-state keyword display metadata in `resolved.base.keywords` and `resolved.upgraded.keywords`.

## Source Representation

The decompiled keyword enum is:

```csharp
public enum CardKeyword
{
    None,
    Exhaust,
    Ethereal,
    Innate,
    Unplayable,
    Retain,
    Sly,
    Eternal
}
```

Cards expose their stable source keywords by overriding `CanonicalKeywords`.

Example, `AscendersBane.cs`:

```csharp
public override IEnumerable<CardKeyword> CanonicalKeywords => new global::_003C_003Ez__ReadOnlyArray<CardKeyword>(new CardKeyword[3]
{
    CardKeyword.Eternal,
    CardKeyword.Unplayable,
    CardKeyword.Ethereal
});
```

Example, `Dazed.cs`:

```csharp
public override IEnumerable<CardKeyword> CanonicalKeywords => new global::_003C_003Ez__ReadOnlyArray<CardKeyword>(new CardKeyword[2]
{
    CardKeyword.Ethereal,
    CardKeyword.Unplayable
});
```

`CardModel.Keywords` initializes a mutable keyword set from `CanonicalKeywords`:

```csharp
_keywords = new HashSet<CardKeyword>();
_keywords.UnionWith(CanonicalKeywords);
return _keywords;
```

Runtime card effects can add or remove keywords from this set, so downstream tools should distinguish:

- canonical keywords parsed from source classes
- dynamic keyword state in live combat/deck contexts

## Keyword Localization

Keyword titles and descriptions are localized through `card_keywords.json`.

English examples:

```json
{
  "ETERNAL.description": "Cannot be removed or transformed from your [gold]Deck[/gold].",
  "ETERNAL.title": "Eternal",
  "ETHEREAL.description": "If this card is in your [gold]Hand[/gold] at the end of this turn, it is [gold]Exhausted[/gold].",
  "ETHEREAL.title": "Ethereal",
  "EXHAUST.description": "Removed until the end of combat.",
  "EXHAUST.title": "Exhaust",
  "INNATE.description": "Start each combat with this card in your [gold]Hand[/gold].",
  "INNATE.title": "Innate",
  "PERIOD": ".",
  "RETAIN.description": "Retained cards are not discarded at the end of turn.",
  "RETAIN.title": "Retain",
  "SLY.description": "If this card is discarded from your [gold]Hand[/gold] before the end of your turn, play it for free.",
  "SLY.title": "Sly",
  "UNPLAYABLE.description": "Unplayable cards cannot be played.",
  "UNPLAYABLE.title": "Unplayable"
}
```

`CardKeywordExtensions.GetCardText()` formats keyword lines as:

```csharp
return "[gold]" + keyword.GetTitle().GetFormattedText() + "[/gold]" + _period.GetRawText();
```

For English, this produces lines such as:

```text
Unplayable.
Ethereal.
Eternal.
```

## Display Placement

Keyword placement is explicit source metadata, not a heuristic.

`CardKeywordOrder.cs` defines:

```csharp
public static readonly CardKeyword[] beforeDescription = new CardKeyword[5]
{
    CardKeyword.Ethereal,
    CardKeyword.Sly,
    CardKeyword.Retain,
    CardKeyword.Innate,
    CardKeyword.Unplayable
};

public static readonly CardKeyword[] afterDescription = new CardKeyword[2]
{
    CardKeyword.Exhaust,
    CardKeyword.Eternal
};
```

`CardModel.GetDescriptionForPile()`:

1. resolves the normal localized card description
2. inserts before-description keywords with `list2.Insert(0, cardKeyword.GetCardText())`
3. appends after-description keywords with `list2.Add(item.GetCardText())`
4. joins non-empty lines with `\n`

Because before-description keywords are inserted at index `0`, their visible order is the reverse of the `beforeDescription` array for keywords that are present on the same card.

For example, `Dazed` has `Ethereal` and `Unplayable`. The array order is:

```text
Ethereal
...
Unplayable
```

but the visible order is:

```text
Unplayable.
Ethereal.
```

`Ascender's Bane` has `Ethereal`, `Unplayable`, and `Eternal`, so it displays:

```text
Unplayable.
Ethereal.
Eternal.
```

`Eternal` appears after the description because it belongs to `afterDescription`. On keyword-only cards with an empty localized card description, this still appears after the before-description keyword block.

## Extracted Placement Table

A one-off extraction from `CardKeyword.cs` and `CardKeywordOrder.cs` for `v0.103.2` gives:

| Keyword | Placement |
| --- | --- |
| Exhaust | after description |
| Ethereal | before description |
| Innate | before description |
| Unplayable | before description |
| Retain | before description |
| Sly | before description |
| Eternal | after description |

There is no overlap in `v0.103.2`: no keyword appears in both before-description and after-description arrays.

Every displayed enum value except `None` appears in exactly one of the two arrays.

The extraction script used for the investigation was:

```python
from pathlib import Path
import re
import json

root = Path("Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards")
keyword_cs = (root / "CardKeyword.cs").read_text()
order_cs = (root / "CardKeywordOrder.cs").read_text()
loc = json.loads(Path("Lab/resources/localization/eng/card_keywords.json").read_text())

enum_body = re.search(r"public enum CardKeyword\s*\{(?P<body>.*?)\}", keyword_cs, re.S).group("body")
keywords = [x.strip().rstrip(",") for x in enum_body.splitlines() if x.strip() and not x.strip().startswith("//")]

def extract_array(name):
    match = re.search(rf"{name}\s*=\s*new CardKeyword\[\d+\]\s*\{{(?P<body>.*?)\}};", order_cs, re.S)
    if not match:
        return []
    return re.findall(r"CardKeyword\.([A-Za-z0-9_]+)", match.group("body"))

before = extract_array("beforeDescription")
after = extract_array("afterDescription")

print("beforeDescription order:")
for index, keyword in enumerate(before, 1):
    print(f"{index}. {keyword}: {loc.get(keyword.upper() + '.title', keyword)}")

print("\nafterDescription order:")
for index, keyword in enumerate(after, 1):
    print(f"{index}. {keyword}: {loc.get(keyword.upper() + '.title', keyword)}")

print("\nall enum placements:")
for keyword in keywords:
    if keyword == "None":
        continue
    placement = []
    if keyword in before:
        placement.append("before")
    if keyword in after:
        placement.append("after")
    print(f"- {keyword}: {', '.join(placement) if placement else 'not displayed by order arrays'}")

print("\noverlap:", sorted(set(before) & set(after)) or "none")
print("missing from display arrays:", [keyword for keyword in keywords if keyword != "None" and keyword not in before and keyword not in after] or "none")
```

## ProjectSpire Parser Coverage

`Lab/parsers/card_parser.py` captures base keyword membership into `raw.keywords`.

Examples:

```json
{
  "schema_version": "0.2.4",
  "id": "ASCENDERS_BANE",
  "raw": {
    "keywords": [
      "Eternal",
      "Unplayable",
      "Ethereal"
    ]
  },
  "resolved": {
    "keyword_period": ".",
    "base": {
      "description": {
        "plain": ""
      },
      "keywords": [
        {
          "id": "Unplayable",
          "placement": "beforeDescription",
          "title": "Unplayable"
        },
        {
          "id": "Ethereal",
          "placement": "beforeDescription",
          "title": "Ethereal"
        },
        {
          "id": "Eternal",
          "placement": "afterDescription",
          "title": "Eternal"
        }
      ]
    }
  }
}
```

```json
{
  "schema_version": "0.2.4",
  "id": "DAZED",
  "raw": {
    "keywords": [
      "Ethereal",
      "Unplayable"
    ]
  },
  "resolved": {
    "keyword_period": ".",
    "base": {
      "description": {
        "plain": ""
      },
      "keywords": [
        {
          "id": "Unplayable",
          "placement": "beforeDescription",
          "title": "Unplayable"
        },
        {
          "id": "Ethereal",
          "placement": "beforeDescription",
          "title": "Ethereal"
        }
      ]
    }
  }
}
```

The parser also captures direct keyword mutations in `OnUpgrade()`:

```json
{
  "id": "KNOW_THY_PLACE",
  "raw": {
    "keywords": ["Exhaust"],
    "keyword_upgrades": [
      {
        "operation": "remove",
        "keyword": "Exhaust",
        "source": "OnUpgrade"
      }
    ]
  },
  "resolved": {
    "base": {
      "keywords": [
        {
          "id": "Exhaust",
          "placement": "afterDescription",
          "title": "Exhaust"
        }
      ]
    },
    "upgraded": {
      "changed": ["keywords"]
    }
  }
}
```

Important current downstream gaps:

- `Lab/scripts/create-card-catalog.py` does not include keywords in `cards.index.json`
- Neow's Cafe's Swift `Card` model has `description` but no `keywords`
- `CardView` renders only `Text(card.description)`, so keyword-only cards show a blank text box

## Data Model Direction

Keywords are intentionally not folded into `resolved.description.plain` as unstructured fallback text.

The parser preserves structured keyword identity and source placement so downstream renderers can:

- render keyword titles in game order
- use localized keyword titles and periods
- style keyword titles as gold text
- attach hover-tip definitions from `card_keywords.json`
- distinguish ordinary description runs from keyword lines

Resolved keyword data uses:

```json
{
  "keyword_period": ".",
  "keywords": [
    {
      "id": "Unplayable",
      "placement": "beforeDescription",
      "title": "Unplayable",
      "description": {
        "plain": "Unplayable cards cannot be played.",
        "runs": [
          {
            "text": "Unplayable cards cannot be played."
          }
        ]
      }
    },
    {
      "id": "Ethereal",
      "placement": "beforeDescription",
      "title": "Ethereal",
      "description": {
        "plain": "If this card is in your Hand at the end of this turn, it is Exhausted.",
        "runs": []
      }
    }
  ]
}
```

Renderers can compose the visible keyword line from `title + keyword_period`. `displayText` is intentionally omitted to avoid duplicating localized title and period data.

## Verification Targets

For `v0.103.2`:

- `Dazed` should render `Unplayable.` then `Ethereal.` in the card text area.
- `Ascender's Bane` should render `Unplayable.`, `Ethereal.`, then `Eternal.`.
- No keyword should appear in both before-description and after-description placement.
- Every `CardKeyword` enum value except `None` should have exactly one placement.
