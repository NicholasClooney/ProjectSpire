import SwiftUI

struct CardsView: View {
    struct CardFilters {
        let text: String
        let pools: [Card.DisplayedCardPool]
        let types: [Card.DisplayedCardType]
        let rarities: [Card.DisplayedRarity]
    }

    struct Dependencies {
        typealias FilterCards = ([Card], CardFilters) -> [Card]

        let cards: [Card]
        let filterCards: FilterCards
    }

    let dependencies: Dependencies

    @Binding var searchText: String

    @State private var selectedDisplayedCardPool: Card.DisplayedCardPool?
    @State private var selectedDisplayedCardType: Card.DisplayedCardType?
    @State private var selectedDisplayedRarity: Card.DisplayedRarity?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                filterPickers

                LazyVGrid(
                    columns: [GridItem(.flexible(), spacing: 24), GridItem(.flexible(), spacing: 24)],
                    spacing: 32
                ) {
                    ForEach(filteredCards, id: \.id) { card in
                        GeometryReader { geo in
                            CardView(card: card)
                                .scaleEffect(geo.size.width / 300, anchor: .topLeading)
                        }
                        .aspectRatio(300 / 422, contentMode: .fit)
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
            pools: selectedDisplayedCardPool.map { [$0] } ?? Card.DisplayedCardPool.allCases,
            types: selectedDisplayedCardType.map { [$0] } ?? Card.DisplayedCardType.allCases,
            rarities: selectedDisplayedRarity.map { [$0] } ?? Card.DisplayedRarity.allCases
        )
    }

    private var filterPickers: some View {
        ScrollView(.horizontal) {
            HStack(alignment: .center, spacing: 12) {
                EnumPicker("Character", selection: $selectedDisplayedCardPool)
                EnumPicker("Type", selection: $selectedDisplayedCardType)
                EnumPicker("Rarity", selection: $selectedDisplayedRarity)

                Button {
                    selectedDisplayedCardPool = nil
                    selectedDisplayedCardType = nil
                    selectedDisplayedRarity = nil
                } label: {
                    Image(systemName: "arrow.counterclockwise")
                }
                .disabled(areFiltersReset)
            }
        }
    }

    private var areFiltersReset: Bool {
        selectedDisplayedCardPool == nil &&
        selectedDisplayedCardType == nil &&
        selectedDisplayedRarity == nil
    }
}
