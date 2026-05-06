# 0003 — Neow's Cafe: Drop `.all` filter case, use allCases

Date: 2026-05-06

Project areas: `Apps/Apple/Neow's Cafe`

Status: Implemented

## Context

`Card.DisplayedCardPool`, `DisplayedCardType`, and `DisplayedRarity` each carry a synthetic `.all` case that exists only to represent "no filter." This forces every `switch` in `CardFilter` to handle `.all`, and the picker UI surfaces "All" as the selected label by default.

Goals:

1. Drop the `.all` case from each enum. The full case list comes from `allCases` directly.
2. The pickers in `CardsView` should show their title ("Character", "Type", "Rarity") as the placeholder when no value is selected. A `nil` UI selection means no filtering is applied.
3. `CardFilter.Criteria` fields stay non-optional. Instead of representing "no filter" with optionals or a synthetic case, the view passes the list of accepted values via `allCases` when nothing is selected, or `[selected]` when a value is picked. `CardFilter` then matches if the card maps to any value in that list.

## Files to change

- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Models/DisplayedDataTypes.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Components/EnumPicker.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Logic/CardFilter.swift`
- `Apps/Apple/Neow's Cafe/Neow's Cafe/Sources/Views/CardsView.swift`

## Changes

### 1. `DisplayedDataTypes.swift`

Remove the `.all` case from each of the three enums. Keep `String, CaseIterable, Hashable` conformances. The remaining cases are unchanged.

### 2. `EnumPicker.swift`

Bind to an optional `Value?`. Render a `nil` row whose label is the picker's title text, so when nothing is selected the picker label shows the title (e.g. "Character").

```swift
struct EnumPicker<Value>: View
where Value: CaseIterable & Hashable & RawRepresentable,
      Value.RawValue == String
{
    let text: String
    @Binding var selection: Value?

    init(_ text: String, selection: Binding<Value?>) {
        self.text = text
        self._selection = selection
    }

    var body: some View {
        Picker(text, selection: $selection) {
            // TODO: i18n
            Text(text).tag(Value?.none)
            ForEach(Array(Value.allCases), id: \.self) { value in
                Text(value.rawValue).tag(Value?.some(value))
            }
        }
    }
}
```

### 3. `CardFilter.swift`

`Criteria` fields become arrays of accepted values (non-optional):

```swift
struct Criteria {
    let searchText: String
    let displayedCardPools: [Card.DisplayedCardPool]
    let displayedCardTypes: [Card.DisplayedCardType]
    let displayedRarities: [Card.DisplayedRarity]
}
```

Each `match` overload becomes "matches if any element in the list matches". The single-value match logic moves into a per-element helper, and the existing `case .all` arms are deleted (since `.all` no longer exists).

```swift
private static func match(card: Card, against pools: [Card.DisplayedCardPool]) -> Bool {
    pools.contains { match(card: card, against: $0) }
}

private static func match(card: Card, against pool: Card.DisplayedCardPool) -> Bool {
    switch pool {
    case .ironclad: return card.cardPool == .ironclad
    // ... existing arms minus `.all`
    }
}
```

Same shape for `DisplayedCardType` and `DisplayedRarity`. Calling site in `apply(filters:to:)` updates field names accordingly.

### 4. `CardsView.swift`

State holds optional selections with `nil` defaults; the view translates each into a list when building `Criteria`.

```swift
@State private var selectedDisplayedCardPool: Card.DisplayedCardPool?
@State private var selectedDisplayedCardType: Card.DisplayedCardType?
@State private var selectedDisplayedRarity: Card.DisplayedRarity?

private var cardFilters: CardFilter.Criteria {
    CardFilter.Criteria(
        searchText: searchText,
        displayedCardPools: selectedDisplayedCardPool.map { [$0] } ?? Card.DisplayedCardPool.allCases,
        displayedCardTypes: selectedDisplayedCardType.map { [$0] } ?? Card.DisplayedCardType.allCases,
        displayedRarities: selectedDisplayedRarity.map { [$0] } ?? Card.DisplayedRarity.allCases
    )
}
```

Note: `CardsView` currently goes through its own `CardFilters` shim and a `Dependencies.filterCards` closure. Update `CardFilters` (or fold it into `CardFilter.Criteria`) so the same list-of-accepted-values shape flows from view to filter.

Reset button assigns `nil` to all three. `areFiltersReset` checks `== nil` for each.

## Verification

From `Apps/Apple/Neow's Cafe`:

```sh
tuist generate
xcodebuild \
  -workspace "Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' \
  build | xcbeautify
```

Then in the simulator:
- Launch the app, open the Cards tab. Each picker label should read "Character", "Type", "Rarity" by default. The card grid shows all cards.
- Pick a character (e.g. Ironclad). The picker label updates and the grid filters. Open the picker and select the title row to clear back to no filter.
- Combine filters across all three pickers. The reset button enables when any filter is non-nil and disables when all are cleared.
