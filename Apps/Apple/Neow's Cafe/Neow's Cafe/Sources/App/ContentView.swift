import SwiftUI

private enum AppTab {
    case cards
    case relics
    case potions
    case events
    case monsters
    case deck
}

public struct ContentView: View {
    private let dependencies: Dependencies

    init(dependencies: Dependencies) {
        self.dependencies = dependencies
    }

    @State private var searchText = ""
    @State private var relicSearchText = ""
    @State private var selected: AppTab = .cards

    public var body: some View {
        TabView(selection: $selected) {
            Tab("Cards", systemImage: "rectangle.grid.2x2", value: .cards) {
                tabContent(title: "Cards") {
                    cardCatalogContent
                        .searchable(text: $searchText, prompt: "Search cards, i.e. Ball Lightning, etc.")
                }
            }

            Tab("Relics", systemImage: "shield.lefthalf.filled", value: .relics) {
                tabContent(title: "Relics") {
                    RelicsView(relics: MockRelics.relics, searchText: $relicSearchText)
                        .searchable(text: $relicSearchText, prompt: "Search relics...")
                }
            }

            Tab("Potions", systemImage: "flask", value: .potions) {
                tabContent(title: "Potions") {
                    PotionsView(potions: MockPotions.potions)
                }
            }

            Tab("Events", systemImage: "scroll", value: .events) {
                tabContent(title: "Events") {
                    EventsView(events: MockEvents.events)
                }
            }

            Tab("Monsters", systemImage: "person.fill.questionmark", value: .monsters) {
                tabContent(title: "Monsters") {
                    MonstersView(monsters: MockMonsters.monsters)
                }
            }

            Tab("Deck",  systemImage: "square.stack.3d.up", value: .deck) {
                tabContent(title: "Deck") {
                    ContentUnavailableView(
                        "Deck",
                        systemImage: "square.stack.3d.up",
                        description: Text("Deck building will live here.")
                    )
                }
            }
        }
        .neowCafeAppTheme()
        .task {
            await dependencies.cardCatalogStore.load()
        }
    }

    @ViewBuilder
    private var cardCatalogContent: some View {
        switch cardCatalogState {
        case .loading:
            ProgressView()
                .tint(NeowSCafeTheme.accent)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(NeowSCafeTheme.background)
        case .error(let message):
            ContentUnavailableView(
                "Cards Unavailable",
                systemImage: "exclamationmark.triangle",
                description: Text(message)
            )
            .foregroundStyle(NeowSCafeTheme.text)
            .background(NeowSCafeTheme.background)
        case .empty:
            ContentUnavailableView(
                "No Cards",
                systemImage: "rectangle.grid.2x2",
                description: Text("The card catalog did not return any cards.")
            )
            .foregroundStyle(NeowSCafeTheme.text)
            .background(NeowSCafeTheme.background)
        case .loaded:
            CardsView(
                dependencies: dependencies.cardsView,
                searchText: $searchText
            )
        }
    }

    private func tabContent<Content: View>(
        title: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        NavigationStack {
            content()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(NeowSCafeTheme.background)
                .navigationTitle(title)
                .navigationBarTitleDisplayMode(.inline)
                .toolbarBackground(NeowSCafeTheme.surface, for: .navigationBar)
                .toolbarBackground(.visible, for: .navigationBar)
                .toolbarBackground(NeowSCafeTheme.surface, for: .tabBar)
                .toolbarBackground(.visible, for: .tabBar)
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
            .preferredColorScheme(.light)

        ContentView(dependencies: .live())
            .preferredColorScheme(.dark)
    }
}
