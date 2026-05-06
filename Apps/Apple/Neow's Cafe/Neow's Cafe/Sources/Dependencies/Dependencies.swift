@MainActor
struct Dependencies {
    let cardCatalogStore: CardCatalogStore
    let filterCards: CardsView.Dependencies.FilterCards

    static func live() -> Dependencies {
        live(cardCatalogStore: CardCatalogStore())
    }

    static func live(cardCatalogStore: CardCatalogStore) -> Dependencies {
        Dependencies(
            cardCatalogStore: cardCatalogStore,
            filterCards: { cards, filters in
                CardFilter.apply(filters: filters.asCriteria, to: cards)
            }
        )
    }

    var cardsView: CardsView.Dependencies {
        CardsView.Dependencies(
            cards: cardCatalogStore.cards,
            filterCards: filterCards
        )
    }
}

private extension CardsView.CardFilters {
    var asCriteria: CardFilter.Criteria {
        CardFilter.Criteria(
            searchText: text,
            displayedCardPools: pools,
            displayedCardTypes: types,
            displayedRarities: rarities
        )
    }
}
