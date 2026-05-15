import SwiftUI

struct Relic {
    let id: String
    let name: String
    let description: String
    let descriptionRuns: [DescriptionRun]
    let flavor: String?
    let flavorRuns: [DescriptionRun]
    let rarity: Rarity
    let pools: [String]
    let portraitURL: URL?

    init(
        id: String,
        name: String,
        description: String,
        descriptionRuns: [DescriptionRun] = [],
        flavor: String? = nil,
        flavorRuns: [DescriptionRun] = [],
        rarity: Rarity,
        pools: [String],
        portraitURL: URL? = nil
    ) {
        self.id = id
        self.name = name
        self.description = description
        self.descriptionRuns = descriptionRuns
        self.flavor = flavor
        self.flavorRuns = flavorRuns
        self.rarity = rarity
        self.pools = pools
        self.portraitURL = portraitURL
    }
}

extension Relic {
    enum Rarity: String, CaseIterable {
        case common
        case uncommon
        case rare
        case starter
        case shop
        case event
        case ancient
        case none

        var displayName: String {
            switch self {
            case .common:   return "Common"
            case .uncommon: return "Uncommon"
            case .rare:     return "Rare"
            case .starter:  return "Starter"
            case .shop:     return "Shop"
            case .event:    return "Event"
            case .ancient:  return "Ancient"
            case .none:     return "None"
            }
        }

        var color: Color {
            switch self {
            case .common:   return Color(StsColors.cream)
            case .uncommon: return Color(StsColors.aqua)
            case .rare:     return Color(StsColors.gold)
            case .starter:  return Color(StsColors.orange)
            case .shop:     return Color(StsColors.merchantBlue)
            case .event:    return Color(StsColors.green)
            case .ancient:  return Color(StsColors.red)
            case .none:     return Color(StsColors.gray)
            }
        }
    }
}
