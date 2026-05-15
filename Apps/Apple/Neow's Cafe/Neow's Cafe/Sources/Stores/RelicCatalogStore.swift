import Combine
import Observation

@MainActor
@Observable
final class RelicCatalogStore: ObservableObject {
    private(set) var relics: [Relic]
    private(set) var errorMessage: String?
    private(set) var isLoading: Bool

    private let service: RelicCatalogService

    init(service: RelicCatalogService = .live) {
        self.service = service
        self.relics = []
        self.isLoading = false
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            relics = try await service.fetchRelics()
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
