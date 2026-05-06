import Foundation

struct CardCatalogService {
    var baseURL: URL
    var session: URLSession = .shared

    static let live = CardCatalogService(
        baseURL: URL(string: "http://127.0.0.1:8765/v0.103.2/")!
    )

    func fetchCards() async throws -> [Card] {
        let manifestURL = baseURL.appendingPathComponent("manifest.json")
        let (manifestData, _) = try await session.data(from: manifestURL)
        let manifest = try JSONDecoder().decode(CardCatalogManifest.self, from: manifestData)
        let indexURL = baseURL.appendingPathComponent(manifest.cardsIndexPath)
        let (indexData, _) = try await session.data(from: indexURL)
        return try CardCatalogDecoder.decodeCards(from: indexData, baseURL: baseURL)
    }
}

enum CardCatalogDecoder {
    static func decodeCards(from data: Data, baseURL: URL) throws -> [Card] {
        let index = try JSONDecoder().decode(CardCatalogIndex.self, from: data)
        return index.cards.map { $0.card(baseURL: baseURL) }
    }
}
