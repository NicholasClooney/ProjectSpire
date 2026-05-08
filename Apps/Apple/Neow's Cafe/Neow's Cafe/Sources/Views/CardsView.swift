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
        typealias RefreshCards = () async -> Void

        let cards: [Card]
        let filterCards: FilterCards
        let refreshCards: RefreshCards
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
                        NavigationLink {
                            CardDetailView(card: card)
                        } label: {
                            GeometryReader { geo in
                                CardView(card: card)
                                    .scaleEffect(geo.size.width / CardView.Constraints.width, anchor: .topLeading)
                            }
                            .aspectRatio(CardView.Constraints.width / CardView.Constraints.height, contentMode: .fit)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .padding(24)
        }
        .background(NeowSCafeTheme.background)
        .refreshable {
            await dependencies.refreshCards()
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
                .buttonStyle(.bordered)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(NeowSCafeTheme.surfaceElevated)
            }
            .overlay {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .stroke(NeowSCafeTheme.separator.opacity(0.55), lineWidth: 1)
            }
        }
        .scrollIndicators(.hidden)
    }

    private var areFiltersReset: Bool {
        selectedDisplayedCardPool == nil &&
        selectedDisplayedCardType == nil &&
        selectedDisplayedRarity == nil
    }
}
