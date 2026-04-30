enum CardFilter {
    struct Criteria {
        let searchText: String
        let displayedCardPool: Card.DisplayedCardPool
        let displayedCardType: Card.DisplayedCardType
        let displayedRarity: Card.DisplayedRarity
    }

    static func apply(filters: Criteria, to cards: [Card]) -> [Card] {
        cards.filter { card in
            match(card: card, against: filters.searchText) &&
            match(card: card, against: filters.displayedCardPool) &&
            match(card: card, against: filters.displayedCardType) &&
            match(card: card, against: filters.displayedRarity)
        }
    }

    private static func match(card: Card, against searchText: String) -> Bool {
        guard !searchText.isEmpty else {
            return true
        }

        return card.title.localizedCaseInsensitiveContains(searchText) ||
        card.description.localizedCaseInsensitiveContains(searchText)
    }

    private static func match(card: Card, against displayedCardPool: Card.DisplayedCardPool) -> Bool {
        switch displayedCardPool {
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

    private static func match(card: Card, against displayedCardType: Card.DisplayedCardType) -> Bool {
        switch displayedCardType {
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

    private static func match(card: Card, against displayedRarity: Card.DisplayedRarity) -> Bool {
        switch displayedRarity {
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
