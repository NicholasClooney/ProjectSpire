import SwiftUI

struct CardsView: View {
    struct CardFilters {
        let text: String
        let pool: Card.DisplayedCardPool
        let type: Card.DisplayedCardType
        let rarity: Card.DisplayedRarity
    }

    struct Dependencies {
        typealias FilterCards = ([Card], CardFilters) -> [Card]

        let cards: [Card]
        let filterCards: FilterCards
    }

    let dependencies: Dependencies
    @Binding var searchText: String

    @State private var selectedDisplayedCardPool: Card.DisplayedCardPool = .all
    @State private var selectedDisplayedCardType: Card.DisplayedCardType = .all
    @State private var selectedDisplayedRarity: Card.DisplayedRarity = .all

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                filterPickers

                LazyVGrid(
                    columns: [GridItem(.adaptive(minimum: 190), spacing: 24)],
                    spacing: 32
                ) {
                    ForEach(filteredCards, id: \.id) { card in
                        CardView(card: card)
                            .scaledToFit()
                    }
                }
            }
            .padding(24)
        }
    }

    private var filteredCards: [Card] {
        dependencies.filterCards(dependencies.cards, cardFilters)
    }

    private var cardFilters: CardFilters {
        CardFilters(
            text: searchText,
            pool: selectedDisplayedCardPool,
            type: selectedDisplayedCardType,
            rarity: selectedDisplayedRarity
        )
    }

    private var filterPickers: some View {
        HStack(alignment: .center, spacing: 12) {
            EnumPicker("Character", selection: $selectedDisplayedCardPool)
            EnumPicker("Type", selection: $selectedDisplayedCardType)
            EnumPicker("Rarity", selection: $selectedDisplayedRarity)

            Button {
                selectedDisplayedCardPool = .all
                selectedDisplayedCardType = .all
                selectedDisplayedRarity = .all
            } label: {
                Image(systemName: "arrow.counterclockwise")
            }
            .disabled(areFiltersReset)
        }
    }

    private var areFiltersReset: Bool {
        selectedDisplayedCardPool == .all &&
        selectedDisplayedCardType == .all &&
        selectedDisplayedRarity == .all
    }
}
