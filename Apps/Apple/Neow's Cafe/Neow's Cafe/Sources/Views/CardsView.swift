import SwiftUI

struct CardsView: View {
    let cards: [Card]
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
        cards.filter { card in
            matchesSearch(card) &&
            matchesDisplayedCardPool(card) &&
            matchesDisplayedCardType(card) &&
            matchesDisplayedRarity(card)
        }
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

    private func matchesSearch(_ card: Card) -> Bool {
        guard !searchText.isEmpty else {
            return true
        }

        return card.title.localizedCaseInsensitiveContains(searchText) ||
        card.description.localizedCaseInsensitiveContains(searchText)
    }

    private func matchesDisplayedCardPool(_ card: Card) -> Bool {
        switch selectedDisplayedCardPool {
        case .all:
            return true
        case .ironclad:
            return card.cardPool == .ironclad
        case .silent:
            return card.cardPool == .silent
        case .defect:
            return card.cardPool == .defect
        case .regent:
            return card.cardPool == .regent
        case .necrobinder:
            return card.cardPool == .necrobinder
        case .colorless:
            return card.cardPool == .colorless
        case .ancient:
            return card.rarity == .ancient
        case .other:
            switch card.cardPool {
            case .curse, .status, .event, .quest, .token:
                return true
            case .ironclad, .silent, .defect, .regent, .necrobinder, .colorless, .deprecated, .mock:
                return false
            }
        }
    }

    private func matchesDisplayedCardType(_ card: Card) -> Bool {
        switch selectedDisplayedCardType {
        case .all:
            return true
        case .attack:
            return card.cardType == .attack
        case .skill:
            return card.cardType == .skill
        case .power:
            return card.cardType == .power
        case .other:
            switch card.cardType {
            case .status, .curse, .quest:
                return true
            case .attack, .skill, .power:
                return false
            }
        }
    }

    private func matchesDisplayedRarity(_ card: Card) -> Bool {
        switch selectedDisplayedRarity {
        case .all:
            return true
        case .common:
            return card.rarity == .common
        case .uncommon:
            return card.rarity == .uncommon
        case .rare:
            return card.rarity == .rare
        case .other:
            switch card.rarity {
            case .basic, .ancient, .event, .token, .status, .curse, .quest:
                return true
            case .common, .uncommon, .rare:
                return false
            }
        }
    }
}
