enum MockPotions {
    static let potions: [Potion] = [
        Potion(
            id: "FIRE_POTION",
            name: "Fire Potion",
            description: "Apply 5 Burn to target enemy.",
            rarity: .common,
            usage: .combatOnly,
            targetType: .anyEnemy,
            pools: ["colorless"],
            portraitURL: nil
        ),
        Potion(
            id: "BLOCK_POTION",
            name: "Block Potion",
            description: "Gain 12 Block.",
            rarity: .common,
            usage: .combatOnly,
            targetType: .self,
            pools: ["colorless"],
            portraitURL: nil
        ),
        Potion(
            id: "STRENGTH_POTION",
            name: "Strength Potion",
            description: "Gain 2 Strength.",
            rarity: .common,
            usage: .combatOnly,
            targetType: .self,
            pools: ["ironclad"],
            portraitURL: nil
        ),
        Potion(
            id: "SWIFT_POTION",
            name: "Swift Potion",
            description: "Draw 3 cards.",
            rarity: .common,
            usage: .combatOnly,
            targetType: .self,
            pools: ["silent"],
            portraitURL: nil
        ),
        Potion(
            id: "FOCUS_POTION",
            name: "Focus Potion",
            description: "Gain 2 Focus.",
            rarity: .common,
            usage: .combatOnly,
            targetType: .self,
            pools: ["defect"],
            portraitURL: nil
        ),
        Potion(
            id: "ELIXIR",
            name: "Elixir",
            description: "Exhaust any number of cards in your hand.",
            rarity: .uncommon,
            usage: .combatOnly,
            targetType: .self,
            pools: ["ironclad"],
            portraitURL: nil
        ),
        Potion(
            id: "POISON_POTION",
            name: "Poison Potion",
            description: "Apply 6 Poison to target enemy.",
            rarity: .uncommon,
            usage: .combatOnly,
            targetType: .anyEnemy,
            pools: ["silent"],
            portraitURL: nil
        ),
        Potion(
            id: "ANCIENT_POTION",
            name: "Ancient Potion",
            description: "Gain 1 Artifact.",
            rarity: .uncommon,
            usage: .combatOnly,
            targetType: .self,
            pools: ["colorless"],
            portraitURL: nil
        ),
        Potion(
            id: "ENERGY_POTION",
            name: "Energy Potion",
            description: "Gain 2 Energy.",
            rarity: .uncommon,
            usage: .combatOnly,
            targetType: .self,
            pools: ["colorless"],
            portraitURL: nil
        ),
        Potion(
            id: "FAIRY_IN_A_BOTTLE",
            name: "Fairy in a Bottle",
            description: "When you would die, heal to 30% of your Max HP instead. Ethereal.",
            rarity: .rare,
            usage: .automatic,
            targetType: .self,
            pools: ["colorless"],
            portraitURL: nil
        ),
        Potion(
            id: "CULTIST_POTION",
            name: "Cultist Potion",
            description: "Gain 1 Ritual.",
            rarity: .rare,
            usage: .combatOnly,
            targetType: .self,
            pools: ["ironclad"],
            portraitURL: nil
        ),
        Potion(
            id: "HEART_OF_IRON",
            name: "Heart of Iron",
            description: "Gain 6 Metallicize.",
            rarity: .rare,
            usage: .combatOnly,
            targetType: .self,
            pools: ["ironclad"],
            portraitURL: nil
        ),
        Potion(
            id: "LIQUID_MEMORY",
            name: "Liquid Memory",
            description: "Choose a card in your Discard Pile. Return it to your hand.",
            rarity: .rare,
            usage: .combatOnly,
            targetType: .self,
            pools: ["colorless"],
            portraitURL: nil
        ),
        Potion(
            id: "ENTROPIC_BREW",
            name: "Entropic Brew",
            description: "Fill all your empty Potion slots with random Potions.",
            rarity: .rare,
            usage: .anyTime,
            targetType: .self,
            pools: ["colorless"],
            portraitURL: nil
        ),
    ]
}
