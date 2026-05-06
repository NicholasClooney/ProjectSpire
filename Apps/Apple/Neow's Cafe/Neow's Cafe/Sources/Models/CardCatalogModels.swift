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
            energyCost: energyCost.cardEnergyCost,
            rarity: rarity,
            cardType: type,
            cardPool: pool,
            portraitURL: portraitPath.map { baseURL.appendingPathComponent($0) }
        )
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
