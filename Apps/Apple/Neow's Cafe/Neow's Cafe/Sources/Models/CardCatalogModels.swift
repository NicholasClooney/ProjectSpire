import Foundation

struct CardCatalogManifest: Decodable {
    let cardsIndexPath: String
    let relicsIndexPath: String?
}

struct CardCatalogIndex: Decodable {
    let cards: [CardCatalogCard]
}

struct CardCatalogCard: Decodable {
    let id: String
    let title: String
    let description: String
    let descriptionRuns: [CatalogDescriptionRun]?
    let keywords: [CatalogCardKeyword]?
    let keywordPeriod: String?
    let energyCost: CatalogEnergyCost
    let type: Card.CardType
    let rarity: Card.Rarity
    let pool: Card.CardPool
    let portraitPath: String?
    let upgrade: CatalogCardUpgrade?

    func card(baseURL: URL) -> Card {
        let portrait = portraitPath.map { baseURL.appendingPathComponent($0) }
        let upgradeSummary: Card.UpgradeSummary? = upgrade.map {
            Card.UpgradeSummary(
                title: $0.title,
                description: $0.description,
                descriptionRuns: $0.descriptionRuns?.map(\.descriptionRun) ?? [],
                keywords: $0.keywords?.map(\.cardKeyword) ?? [],
                keywordPeriod: $0.keywordPeriod ?? ".",
                energyCost: $0.energyCost.cardEnergyCost
            )
        }
        return Card(
            id: id,
            title: title,
            description: description,
            descriptionRuns: descriptionRuns?.map(\.descriptionRun) ?? [],
            keywords: keywords?.map(\.cardKeyword) ?? [],
            keywordPeriod: keywordPeriod ?? ".",
            energyCost: energyCost.cardEnergyCost,
            rarity: rarity,
            cardType: type,
            cardPool: pool,
            portraitURL: portrait,
            upgradeSummary: upgradeSummary
        )
    }
}

struct CatalogCardUpgrade: Decodable {
    let title: String
    let description: String
    let descriptionRuns: [CatalogDescriptionRun]?
    let keywords: [CatalogCardKeyword]?
    let keywordPeriod: String?
    let energyCost: CatalogEnergyCost
}

struct CatalogDescriptionRun: Decodable {
    let text: String
    let sourceVar: String?
    let style: DescriptionRun.Style?

    var descriptionRun: DescriptionRun {
        DescriptionRun(text, sourceVar: sourceVar, style: style)
    }
}

struct CatalogCardKeyword: Decodable {
    let id: String
    let placement: Card.Keyword.Placement
    let title: String

    var cardKeyword: Card.Keyword {
        Card.Keyword(id: id, placement: placement, title: title)
    }
}

struct CatalogEnergyCost: Decodable {
    let kind: String
    let value: Int?

    var cardEnergyCost: Card.EnergyCost {
        switch kind {
        case "x":
            return .x
        default:
            return .int(value ?? -1)
        }
    }
}
