import SwiftUI

private enum AppTab {
    case cards
    case deck
    case filter
}

public struct ContentView: View {
    private let dependencies: Dependencies

    init(dependencies: Dependencies) {
        self.dependencies = dependencies
    }

    @State private var searchText = ""
    @State private var selected: AppTab = .cards

    public var body: some View {
        TabView(selection: $selected) {
            Tab("Cards", systemImage: "rectangle.grid.2x2", value: .cards) {
                NavigationStack {
                    cardCatalogContent
                    .navigationTitle("Cards")
                    .searchable(text: $searchText, prompt: "Search cards, i.e. Ball Lightning, etc.")
                }
            }

            Tab("Deck",  systemImage: "square.stack.3d.up", value: .deck) {
                NavigationStack {
                    Text("Deck")
                        .navigationTitle("Deck")
                }
            }
        }
        .task {
            await dependencies.cardCatalogStore.load()
        }
    }

    @ViewBuilder
    private var cardCatalogContent: some View {
        switch cardCatalogState {
        case .loading:
            ProgressView()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        case .error(let message):
            ContentUnavailableView(
                "Cards Unavailable",
                systemImage: "exclamationmark.triangle",
                description: Text(message)
            )
        case .empty:
            ContentUnavailableView(
                "No Cards",
                systemImage: "rectangle.grid.2x2",
                description: Text("The card catalog did not return any cards.")
            )
        case .loaded:
            CardsView(
                dependencies: dependencies.cardsView,
                searchText: $searchText
            )
        }
    }

    private var cardCatalogState: CardCatalogState {
        if let errorMessage = dependencies.cardCatalogStore.errorMessage {
            return .error(errorMessage)
        }

        if dependencies.cardCatalogStore.isLoading && dependencies.cardCatalogStore.cards.isEmpty {
            return .loading
        }

        if dependencies.cardCatalogStore.cards.isEmpty {
            return .empty
        }

        return .loaded
    }

    private enum CardCatalogState: Equatable {
        case loading
        case error(String)
        case empty
        case loaded
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView(dependencies: .live())
    }
}
