import Foundation

extension Card {
    enum DisplayedCardPool: String, CaseIterable, Hashable {
        case all
        case ironclad
        case silent
        case defect
        case regent
        case necrobinder
        case colorless
        // Ancient is surfaced as a top-level displayed pool because the game treats it that way.
        case ancient
        case other
    }
}

extension Card {
    enum DisplayedCardType: String, CaseIterable, Hashable {
        case all
        case attack
        case skill
        case power
        case other
    }
}

extension Card {
    enum DisplayedRarity: String, CaseIterable, Hashable {
        case all
        case common
        case uncommon
        case rare
        case other
    }
}
