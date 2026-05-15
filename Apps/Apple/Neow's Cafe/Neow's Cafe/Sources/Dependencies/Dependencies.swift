@MainActor
struct Dependencies {
    let cardCatalogStore: CardCatalogStore
    let relicCatalogStore: RelicCatalogStore
    let filterCards: CardsView.Dependencies.FilterCards

    static func live() -> Dependencies {
        live(cardCatalogStore: CardCatalogStore(), relicCatalogStore: RelicCatalogStore())
    }

    static func live(cardCatalogStore: CardCatalogStore, relicCatalogStore: RelicCatalogStore) -> Dependencies {
        Dependencies(
            cardCatalogStore: cardCatalogStore,
            relicCatalogStore: relicCatalogStore,
            filterCards: { cards, filters in
                CardFilter.apply(filters: filters.asCriteria, to: cards)
            }
        )
    }

    var cardsView: CardsView.Dependencies {
        CardsView.Dependencies(
            cards: cardCatalogStore.cards,
            filterCards: filterCards
        ) {
            await cardCatalogStore.load()
        }
    }

    var relicsView: RelicsView.Dependencies {
        RelicsView.Dependencies(
            relics: relicCatalogStore.relics,
            filterRelics: { relics, filters in RelicFilter.apply(relics: relics, filters: filters) }
        ) {
            await relicCatalogStore.load()
        }
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
