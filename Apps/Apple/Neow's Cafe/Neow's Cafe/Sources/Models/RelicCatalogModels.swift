import Foundation

struct RelicCatalogIndex: Decodable {
    let relics: [RelicCatalogRelic]
}

struct RelicCatalogRelic: Decodable {
    let id: String
    let title: String
    let description: String
    let descriptionRuns: [CatalogDescriptionRun]?
    let flavor: String?
    let flavorRuns: [CatalogDescriptionRun]?
    let rarity: Relic.Rarity
    let pools: [String]
    let portraitPath: String?

    func relic(baseURL: URL) -> Relic {
        let portrait = portraitPath.map { baseURL.appendingPathComponent($0) }
        return Relic(
            id: id,
            name: title,
            description: description,
            descriptionRuns: descriptionRuns?.map(\.descriptionRun) ?? [],
            flavor: flavor,
            flavorRuns: flavorRuns?.map(\.descriptionRun) ?? [],
            rarity: rarity,
            pools: pools,
            portraitURL: portrait
        )
    }
}
