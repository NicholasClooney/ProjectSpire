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
                    CardsView(dependencies: dependencies.cardsView, searchText: $searchText)
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
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView(dependencies: .live)
    }
}
