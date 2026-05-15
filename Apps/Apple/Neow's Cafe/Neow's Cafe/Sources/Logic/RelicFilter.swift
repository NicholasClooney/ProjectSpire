enum RelicFilter {
    static func apply(relics: [Relic], filters: RelicsView.RelicFilters) -> [Relic] {
        relics.filter { relic in
            matchesSearch(relic, filters.searchText) && matchesRarity(relic, filters.rarity)
        }
    }

    private static func matchesSearch(_ relic: Relic, _ searchText: String) -> Bool {
        guard !searchText.isEmpty else { return true }
        return relic.name.localizedCaseInsensitiveContains(searchText)
            || relic.description.localizedCaseInsensitiveContains(searchText)
            || relic.rarity.rawValue.localizedCaseInsensitiveContains(searchText)
            || relic.pools.contains { $0.localizedCaseInsensitiveContains(searchText) }
    }

    private static func matchesRarity(_ relic: Relic, _ rarity: Relic.Rarity?) -> Bool {
        guard let rarity else { return true }
        return relic.rarity == rarity
    }
}
