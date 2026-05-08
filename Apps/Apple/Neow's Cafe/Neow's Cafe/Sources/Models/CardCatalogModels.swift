import Foundation

struct CardCatalogManifest: Decodable {
    let cardsIndexPath: String
}

struct CardCatalogIndex: Decodable {
    let cards: [CardCatalogCard]
}

struct CardCatalogCard: Decodable {
    let id: String
    let title: String
    let description: String
    let keywords: [CatalogCardKeyword]?
    let keywordPeriod: String?
    let energyCost: CatalogEnergyCost
    let type: Card.CardType
    let rarity: Card.Rarity
    let pool: Card.CardPool
    let portraitPath: String?

    func card(baseURL: URL) -> Card {
        Card(
            id: id,
            title: title,
            description: description,
            keywords: keywords?.map(\.cardKeyword) ?? [],
            keywordPeriod: keywordPeriod ?? ".",
            energyCost: energyCost.cardEnergyCost,
            rarity: rarity,
            cardType: type,
            cardPool: pool,
            portraitURL: portraitPath.map { baseURL.appendingPathComponent($0) }
        )
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
