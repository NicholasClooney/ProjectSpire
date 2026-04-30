//
//  Card.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 29/04/2026.
//

import DeveloperToolsSupport

struct Card {

    let id: String // e.g. "BALL_LIGHTNING" derives the localization (as is) & images (lowercased)

    let title: String
    let description: String
    let energyCost: Int

    // TODO
    enum EnergyCost {
        case x
        case int(Int)
    }

    let rarity: Rarity // derives banner color, and portrait border & plaque color
    let cardType: CardType // derives portrait boder image
    let cardPool: CardPool // derives frame color
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

    enum CardType: String {
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
    enum CardPool {
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
    enum Rarity {

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
