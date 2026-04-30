import SwiftUI

private enum AppTab {
    case cards
    case deck
    case filter
}

public struct ContentView: View {
    public init() {}

    @State private var searchText = ""
    @State private var selected: AppTab = .cards
    @State private var selectedDisplayedCardPool: Card.DisplayedCardPool = .all
    @State private var selectedDisplayedCardType: Card.DisplayedCardType = .all
    @State private var selectedDisplayedRarity: Card.DisplayedRarity = .all

    public var body: some View {
        TabView(selection: $selected) {
            Tab("Cards", systemImage: "rectangle.grid.2x2", value: .cards) {
                NavigationStack {
                    cards
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

    private var filteredCards: [Card] {
        return Self.previewCards.filter { card in
            matchesSearch(card) &&
            matchesDisplayedCardPool(card) &&
            matchesDisplayedCardType(card) &&
            matchesDisplayedRarity(card)
        }
    }

    private var cards: some View {
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

private extension ContentView {
    static let previewCards = [
        Card(
            id: "BALL_LIGHTNING",
            title: "Ball Lightning",
            description: """
            Deal 7 damage.
            Channel 1 Lightning.
            """,
            energyCost: 1,
            rarity: .common,
            cardType: .attack,
            cardPool: .defect
        ),
        Card(
            id: "ANGER",
            title: "Anger",
            description: """
            Deal 6 damage.
            Add a copy into your Discard Pile.
            """,
            energyCost: 0,
            rarity: .common,
            cardType: .attack,
            cardPool: .ironclad
        ),
        Card(
            id: "CORRUPTION",
            title: "Corruption",
            description: """
            Skills cost 0.
            Whenever you play a Skill, Exhaust it.
            """,
            energyCost: 3,
            rarity: .ancient,
            cardType: .power,
            cardPool: .ironclad
        ),
        Card(
            id: "ADRENALINE",
            title: "Adrenaline",
            description: """
            Gain 1 Energy.
            Draw 2 cards.
            """,
            energyCost: 0,
            rarity: .rare,
            cardType: .skill,
            cardPool: .silent
        ),
        Card(
            id: "MEMENTO_MORI",
            title: "Memento Mori",
            description: """
            Deal damage.
            Deals additional damage for each card discarded this turn.
            """,
            energyCost: 1,
            rarity: .uncommon,
            cardType: .attack,
            cardPool: .silent
        ),
        Card(
            id: "DEFEND_REGENT",
            title: "Defend",
            description: "Gain 5 Block.",
            energyCost: 1,
            rarity: .basic,
            cardType: .skill,
            cardPool: .regent
        ),
        Card(
            id: "DEATHBRINGER",
            title: "Deathbringer",
            description: """
            Apply 21 Doom and 1 Weak to ALL enemies.
            """,
            energyCost: 2,
            rarity: .uncommon,
            cardType: .skill,
            cardPool: .necrobinder
        ),
        Card(
            id: "MASTER_OF_STRATEGY",
            title: "Master of Strategy",
            description: "Draw 3 cards.",
            energyCost: 0,
            rarity: .rare,
            cardType: .skill,
            cardPool: .colorless
        ),
        Card(
            id: "DOUBT",
            title: "Doubt",
            description: """
            At the end of your turn, if this is in your Hand, gain 1 Weak.
            """,
            energyCost: -1,
            rarity: .curse,
            cardType: .curse,
            cardPool: .curse
        ),
        Card(
            id: "WOUND",
            title: "Wound",
            description: "",
            energyCost: -1,
            rarity: .status,
            cardType: .status,
            cardPool: .status
        ),
        Card(
            id: "LANTERN_KEY",
            title: "Lantern Key",
            description: "Unlocks a special event in the next Act.",
            energyCost: -1,
            rarity: .quest,
            cardType: .quest,
            cardPool: .quest
        ),
        Card(
            id: "HELLO_WORLD",
            title: "Hello World",
            description: """
            At the start of your turn, add a random Common card into your Hand.
            """,
            energyCost: 1,
            rarity: .event,
            cardType: .power,
            cardPool: .event
        )
    ]
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
