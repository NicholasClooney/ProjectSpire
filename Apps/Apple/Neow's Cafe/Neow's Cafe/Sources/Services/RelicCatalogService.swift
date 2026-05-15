import Foundation

struct RelicCatalogService {
    var baseURL: URL
    var session: URLSession = .shared

    static let live = RelicCatalogService(
        baseURL: URL(string: "http://127.0.0.1:8765/v0.103.2/")!
    )

    func fetchRelics() async throws -> [Relic] {
        let manifestURL = baseURL.appendingPathComponent("manifest.json")
        let (manifestData, _) = try await session.data(from: manifestURL)
        let manifest = try JSONDecoder().decode(CardCatalogManifest.self, from: manifestData)
        guard let relicsIndexPath = manifest.relicsIndexPath else {
            throw RelicCatalogError.missingRelicsIndex
        }
        let indexURL = baseURL.appendingPathComponent(relicsIndexPath)
        let (indexData, _) = try await session.data(from: indexURL)
        return try RelicCatalogDecoder.decodeRelics(from: indexData, baseURL: baseURL)
    }
}

enum RelicCatalogDecoder {
    static func decodeRelics(from data: Data, baseURL: URL) throws -> [Relic] {
        let index = try JSONDecoder().decode(RelicCatalogIndex.self, from: data)
        return index.relics.map { $0.relic(baseURL: baseURL) }
    }
}

enum RelicCatalogError: Error {
    case missingRelicsIndex
}
