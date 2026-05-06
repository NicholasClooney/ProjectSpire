import Combine
import Observation

@MainActor
@Observable
final class CardCatalogStore: ObservableObject {
    private(set) var cards: [Card]
    private(set) var errorMessage: String?
    private(set) var isLoading: Bool

    private let service: CardCatalogService

    init(service: CardCatalogService = .live) {
        self.service = service
        self.cards = []
        self.isLoading = false
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            cards = try await service.fetchCards()
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
