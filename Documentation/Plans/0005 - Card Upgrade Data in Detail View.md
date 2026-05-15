# Card Upgrade Data in Detail View

Date: 2026-05-08

Project areas: `Lab/scripts/`, `Apps/Apple/Neow's Cafe`

## Context

`CardDetailView` has a "View Upgrades" toggle that currently does nothing. The catalog index (`cards.index.json`) contains no upgrade data. Raw card JSONs have a `resolved.upgraded` section with the full upgraded card state. Add a compact upgrade summary to the catalog index so the toggle is instant with no network fetch.

## 1. Catalog generator (`Lab/scripts/create-catalog.py`)

Refactor `card_keywords()` and `energy_cost()` to accept a section dict rather than a whole card, then add `upgrade_summary()`:

```python
def upgrade_summary(card: dict[str, Any]) -> dict[str, Any] | None:
    upgraded = card.get("resolved", {}).get("upgraded")
    if not isinstance(upgraded, dict):
        return None
    description = upgraded.get("description", {})
    plain_description = description.get("plain") if isinstance(description, dict) else None
    return {
        "title": upgraded.get("title", card["id"]),
        "description": plain_description or "",
        "keywords": extract_keywords(upgraded),
        "keywordPeriod": card.get("resolved", {}).get("keyword_period", "."),
        "energyCost": parse_energy_cost(upgraded.get("energy_cost")),
    }
```

Add `"upgrade": upgrade_summary(card)` to `card_summary()`. Cards with no upgrade emit `"upgrade": null`.

Regenerate: `python3 Lab/scripts/create-catalog.py --clean`

## 2. Swift catalog models (`Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Models/CardCatalogModels.swift`)

Add `CatalogCardUpgrade: Decodable` (title, description, keywords, keywordPeriod, energyCost). Add `upgrade: CatalogCardUpgrade?` to `CardCatalogCard`. In `card(baseURL:)` construct the upgraded `Card` from the summary and pass it as `upgradedCard`.

## 3. Card model (`Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Models/Card.swift`)

Add `let upgradedCard: Card?` defaulting to `nil`. Multi-level upgrades are out of scope.

## 4. CardDetailView (`Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Views/CardDetailView.swift`)

- `CardView` receives `showingUpgrade ? (card.upgradedCard ?? card) : card`
- Hide "View Upgrades" button entirely when `card.upgradedCard == nil`

## 5. Mock cards (`Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Mocks/MockCards.swift`)

Add `upgradedCard` to Anger (6→8 damage), Adrenaline (draw 3), and Corruption (ancient). Leave curse/status/quest mocks with `nil`.

## 6. Preview update

Update the "Common Attack" preview in `CardDetailView.swift` to use Anger so the toggle is exercisable in canvas.

## Verification

- Confirm `upgrade` field is present in `cards.index.json` for `anger` and `null` for `wound`
- Build: `xcodebuild ... | xcbeautify` — no errors
- Simulator: tap "View Upgrades" on a card — flips to upgraded; tap again — reverts
- Curse/status/quest cards hide the "View Upgrades" button
