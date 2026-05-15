import SwiftUI

struct Potion {
    let id: String
    let name: String
    let description: String
    let rarity: Rarity
    let usage: Usage
    let targetType: TargetType
    let pools: [String]
    let portraitURL: URL?
}

extension Potion {
    enum Rarity: String, CaseIterable {
        case common
        case uncommon
        case rare
        case event
        case token
        case none

        var displayName: String {
            switch self {
            case .common:   return "Common"
            case .uncommon: return "Uncommon"
            case .rare:     return "Rare"
            case .event:    return "Event"
            case .token:    return "Token"
            case .none:     return "None"
            }
        }

        var color: Color {
            switch self {
            case .common:   return Color(StsColors.cream)
            case .uncommon: return Color(StsColors.aqua)
            case .rare:     return Color(StsColors.gold)
            case .event:    return Color(StsColors.green)
            case .token:    return Color(StsColors.orange)
            case .none:     return Color(StsColors.gray)
            }
        }
    }

    enum Usage: String {
        case anyTime      = "AnyTime"
        case combatOnly   = "CombatOnly"
        case automatic    = "Automatic"

        var displayName: String {
            switch self {
            case .anyTime:    return "Any time"
            case .combatOnly: return "Combat only"
            case .automatic:  return "Automatic"
            }
        }
    }

    enum TargetType: String {
        case `self`              = "Self"
        case allEnemies          = "AllEnemies"
        case anyEnemy            = "AnyEnemy"
        case anyPlayer           = "AnyPlayer"
        case targetedNoCreature  = "TargetedNoCreature"

        var displayName: String {
            switch self {
            case .self:             return "Self"
            case .allEnemies:       return "All enemies"
            case .anyEnemy:         return "Target enemy"
            case .anyPlayer:        return "Any player"
            case .targetedNoCreature: return "No target"
            }
        }
    }
}
