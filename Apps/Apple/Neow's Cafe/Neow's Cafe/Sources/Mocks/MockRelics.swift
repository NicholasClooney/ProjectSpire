private typealias Run = DescriptionRun

enum MockRelics {
    static let relics: [Relic] = [
        Relic(
            id: "BURNING_BLOOD",
            name: "Burning Blood",
            description: "At the end of combat, heal 6 HP.",
            descriptionRuns: [
                Run("At the end of combat, heal "),
                Run("6", style: .blue),
                Run(" HP."),
            ],
            flavor: "Your rage burns inside you, healing your wounds.",
            flavorRuns: [
                Run("Your rage burns inside you, healing your wounds.", style: .red),
            ],
            rarity: .starter,
            pools: ["ironclad"]
        ),
        Relic(
            id: "RING_OF_THE_SNAKE",
            name: "Ring of the Snake",
            description: "At the start of each combat, draw 2 additional cards.",
            descriptionRuns: [
                Run("At the start of each combat, draw "),
                Run("2", style: .blue),
                Run(" additional cards."),
            ],
            flavor: "Made from a fossilized snake, said to have been a companion of the Silent.",
            flavorRuns: [
                Run("Made from a fossilized snake, said to have been a companion of the Silent.", style: .red),
            ],
            rarity: .starter,
            pools: ["silent"]
        ),
        Relic(
            id: "CRACKED_CORE",
            name: "Cracked Core",
            description: "At the start of each combat, Channel 1 Lightning.",
            descriptionRuns: [
                Run("At the start of each combat, "),
                Run("Channel", style: .gold),
                Run(" "),
                Run("1", style: .blue),
                Run(" "),
                Run("Lightning", style: .gold),
                Run("."),
            ],
            flavor: "Details for this relic will be revealed in the future...",
            flavorRuns: [
                Run("Details for this relic will be revealed in the future...", style: .red),
            ],
            rarity: .starter,
            pools: ["defect"]
        ),
        Relic(
            id: "VAJRA",
            name: "Vajra",
            description: "At the start of each combat, gain 1 Strength.",
            descriptionRuns: [
                Run("At the start of each combat, gain "),
                Run("1", style: .blue),
                Run(" "),
                Run("Strength", style: .gold),
                Run("."),
            ],
            flavor: "A scepter associated with the concept of indestructibility.",
            flavorRuns: [
                Run("A scepter associated with the concept of indestructibility.", style: .red),
            ],
            rarity: .common,
            pools: ["ironclad"]
        ),
        Relic(
            id: "ART_OF_WAR",
            name: "Art of War",
            description: "If you do not play any Attacks during a turn, gain an extra Energy next turn.",
            descriptionRuns: [
                Run("If you do not play any "),
                Run("Attacks", style: .gold),
                Run(" during a turn, gain an extra "),
                Run("Energy", style: .gold),
                Run(" next turn."),
            ],
            rarity: .uncommon,
            pools: ["ironclad", "colorless"]
        ),
        Relic(
            id: "BOTTLED_FLAME",
            name: "Bottled Flame",
            description: "Upon pickup, choose an Attack. Start each combat with that card in your hand.",
            descriptionRuns: [
                Run("Upon pickup, choose an "),
                Run("Attack", style: .gold),
                Run(". Start each combat with that card in your hand."),
            ],
            flavor: "A living flame imprisoned within a bottle.",
            flavorRuns: [
                Run("A living flame imprisoned within a bottle.", style: .red),
            ],
            rarity: .uncommon,
            pools: ["colorless"]
        ),
        Relic(
            id: "SOZU",
            name: "Sozu",
            description: "You cannot obtain Potions.",
            descriptionRuns: [
                Run("You cannot obtain "),
                Run("Potions", style: .gold),
                Run("."),
            ],
            flavor: "The samurai had no need for potions.",
            flavorRuns: [
                Run("The samurai had no need for potions.", style: .red),
            ],
            rarity: .rare,
            pools: ["colorless"]
        ),
        Relic(
            id: "PHILOSOPHERS_STONE",
            name: "Philosopher's Stone",
            description: "Gain 1 extra Energy at the start of each turn. All enemies start each combat with 1 Strength.",
            descriptionRuns: [
                Run("Gain "),
                Run("1", style: .blue),
                Run(" extra "),
                Run("Energy", style: .gold),
                Run(" at the start of each turn. All enemies start each combat with "),
                Run("1", style: .blue),
                Run(" "),
                Run("Strength", style: .gold),
                Run("."),
            ],
            flavor: "All the world's power in a small stone.",
            flavorRuns: [
                Run("All the world's power in a small stone.", style: .red),
            ],
            rarity: .rare,
            pools: ["colorless"]
        ),
        Relic(
            id: "PEDDLERS_TALISMAN",
            name: "Peddler's Talisman",
            description: "Items in the shop cost 20% less.",
            descriptionRuns: [
                Run("Items in the shop cost "),
                Run("20%", style: .green),
                Run(" less."),
            ],
            flavor: "The salesman smiled.",
            flavorRuns: [
                Run("The salesman smiled.", style: .red),
            ],
            rarity: .shop,
            pools: ["shop"]
        ),
        Relic(
            id: "ECTOPLASM",
            name: "Ectoplasm",
            description: "You can no longer gain Gold. Gain 1 extra Energy at the start of each turn.",
            descriptionRuns: [
                Run("You can no longer gain "),
                Run("Gold", style: .gold),
                Run(". Gain "),
                Run("1", style: .blue),
                Run(" extra "),
                Run("Energy", style: .gold),
                Run(" at the start of each turn."),
            ],
            rarity: .event,
            pools: ["event"]
        ),
        Relic(
            id: "TINY_HOUSE",
            name: "Tiny House",
            description: "Gain 50 Gold. Add a Potion to your inventory. Heal 5 HP. Obtain 1 Card.",
            descriptionRuns: [
                Run("Gain "),
                Run("50", style: .blue),
                Run(" "),
                Run("Gold", style: .gold),
                Run(". Add a "),
                Run("Potion", style: .gold),
                Run(" to your inventory. Heal "),
                Run("5", style: .blue),
                Run(" HP. Obtain "),
                Run("1", style: .blue),
                Run(" Card."),
            ],
            rarity: .event,
            pools: ["event"]
        ),
        Relic(
            id: "ASTROLABE",
            name: "Astrolabe",
            description: "Upon pickup, choose and Transform 3 cards. They also become Upgraded.",
            descriptionRuns: [
                Run("Upon pickup, choose and "),
                Run("Transform", style: .gold),
                Run(" "),
                Run("3", style: .blue),
                Run(" cards. They also become "),
                Run("Upgraded", style: .green),
                Run("."),
            ],
            flavor: "The stars mapped your destiny long ago.",
            flavorRuns: [
                Run("The stars mapped your destiny long ago.", style: .red),
            ],
            rarity: .ancient,
            pools: ["ancient"]
        ),
    ]
}
