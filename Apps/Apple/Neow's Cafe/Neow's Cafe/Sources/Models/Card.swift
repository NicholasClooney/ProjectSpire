//
//  Card.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 29/04/2026.
//

import DeveloperToolsSupport
import Foundation

struct Card {

    let id: String // e.g. "BALL_LIGHTNING" derives the localization (as is) & images (lowercased)

    let title: String
    let description: String
    let descriptionRuns: [DescriptionRun]
    let keywords: [Keyword]
    let keywordPeriod: String
    let energyCost: EnergyCost

    enum EnergyCost: Equatable {
        case x
        case int(Int)
    }

    let upgradeLevel: Int       // 0 = not upgraded
    let maxUpgradeLevel: Int    // most cards: 1; some multi-level cards: >1
    let energyCostReduced: Bool // true when the upgraded cost is lower than the base cost

    let rarity: Rarity // derives banner color, and portrait border & plaque color
    let cardType: CardType // derives portrait boder image
    let cardPool: CardPool // derives frame color
    let portraitURL: URL?
    let upgradeSummary: UpgradeSummary?

    init(
        id: String,
        title: String,
        description: String,
        descriptionRuns: [DescriptionRun] = [],
        keywords: [Keyword] = [],
        keywordPeriod: String = ".",
        energyCost: EnergyCost,
        upgradeLevel: Int = 0,
        maxUpgradeLevel: Int = 1,
        energyCostReduced: Bool = false,
        rarity: Rarity,
        cardType: CardType,
        cardPool: CardPool,
        portraitURL: URL?,
        upgradeSummary: UpgradeSummary? = nil
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.descriptionRuns = descriptionRuns
        self.keywords = keywords
        self.keywordPeriod = keywordPeriod
        self.energyCost = energyCost
        self.upgradeLevel = upgradeLevel
        self.maxUpgradeLevel = maxUpgradeLevel
        self.energyCostReduced = energyCostReduced
        self.rarity = rarity
        self.cardType = cardType
        self.cardPool = cardPool
        self.portraitURL = portraitURL
        self.upgradeSummary = upgradeSummary
    }
}

extension Card {
    struct UpgradeSummary {
        let title: String
        let description: String
        let descriptionRuns: [DescriptionRun]
        let keywords: [Keyword]
        let keywordPeriod: String
        let energyCost: EnergyCost
    }
}

extension Card {
    struct DescriptionRun: Equatable {
        let text: String
        let sourceVar: String?
        let style: Style?

        enum Style: Equatable, Decodable {
            case gold
            case green
            case red
            case blue
            case unknown(String)

            init(from decoder: Decoder) throws {
                let container = try decoder.singleValueContainer()
                let rawValue = try container.decode(String.self)
                switch rawValue {
                case "gold":
                    self = .gold
                case "green":
                    self = .green
                case "red":
                    self = .red
                case "blue":
                    self = .blue
                default:
                    self = .unknown(rawValue)
                }
            }
        }
    }
}

extension Card {
    struct Keyword: Equatable {
        let id: String
        let placement: Placement
        let title: String

        enum Placement: String, Decodable {
            case beforeDescription
            case afterDescription
        }
    }
}

extension Card {
    /*
     Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardType.cs

     public enum CardType
     {
     None,
     Attack,
     Skill,
     Power,
     Status,
     Curse,
     Quest
     }
     */

    enum CardType: String, Decodable {
        case attack
        case skill
        case power
        case status
        case curse
        case quest
    }
}

extension Card {
    /*
     The current pool classes are:

     - IroncladCardPool -> card_frame_red
     - SilentCardPool -> card_frame_green
     - DefectCardPool -> card_frame_blue
     - RegentCardPool -> card_frame_orange
     - NecrobinderCardPool -> card_frame_pink
     - ColorlessCardPool -> card_frame_colorless
     - CurseCardPool -> card_frame_curse
     - StatusCardPool -> card_frame_colorless
     - EventCardPool -> card_frame_colorless
     - QuestCardPool -> card_frame_quest
     - TokenCardPool -> card_frame_colorless
     - DeprecatedCardPool -> card_frame_colorless
     - MockCardPool -> card_frame_colorless

     */
    enum CardPool: String, Decodable {
        case ironclad
        case silent
        case defect
        case regent
        case necrobinder
        case colorless
        case curse
        case status
        case event
        case quest
        case token
        case deprecated
        case mock
    }
}

extension Card {
    /*
     Lab/decompiled/v0.103.2/MegaCrit.Sts2.Core.Entities.Cards/CardRarity.cs

     ```cs
     public enum CardRarity
     {
     None,
     Basic,
     Common,
     Uncommon,
     Rare,
     Ancient,
     Event,
     Token,
     Status,
     Curse,
     Quest
     }
     ```
     */
    enum Rarity: String, Decodable {

        case basic
        case common
        case uncommon
        case rare
        case ancient
        case event
        case token
        case status
        case curse
        case quest
    }

}
