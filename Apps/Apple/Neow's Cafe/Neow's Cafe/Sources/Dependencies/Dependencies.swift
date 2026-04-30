struct Dependencies {
    let cards: [Card]
    let filterCards: CardsView.Dependencies.FilterCards

    static let live = Dependencies(
        cards: MockCards.cards,
        filterCards: { cards, filters in
            CardFilter.apply(filters: filters.asCriteria, to: cards)
        }
    )

    var cardsView: CardsView.Dependencies {
        CardsView.Dependencies(
            cards: cards,
            filterCards: filterCards
        )
    }
}

private extension CardsView.CardFilters {
    var asCriteria: CardFilter.Criteria {
        CardFilter.Criteria(
            searchText: text,
            displayedCardPool: pool,
            displayedCardType: type,
            displayedRarity: rarity
        )
    }
}
