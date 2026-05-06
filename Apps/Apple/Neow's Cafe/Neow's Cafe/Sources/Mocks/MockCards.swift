enum MockCards {
    static let cards = [
        Card(
            id: "BALL_LIGHTNING",
            title: "Ball Lightning",
            description: """
            Deal 7 damage.
            Channel 1 Lightning.
            """,
            energyCost: .int(1),
            rarity: .common,
            cardType: .attack,
            cardPool: .defect,
            portraitURL: nil
        ),
        Card(
            id: "ANGER",
            title: "Anger",
            description: """
            Deal 6 damage.
            Add a copy into your Discard Pile.
            """,
            energyCost: .int(0),
            rarity: .common,
            cardType: .attack,
            cardPool: .ironclad,
            portraitURL: nil
        ),
        Card(
            id: "CORRUPTION",
            title: "Corruption",
            description: """
            Skills cost 0.
            Whenever you play a Skill, Exhaust it.
            """,
            energyCost: .int(3),
            rarity: .ancient,
            cardType: .power,
            cardPool: .ironclad,
            portraitURL: nil
        ),
        Card(
            id: "ADRENALINE",
            title: "Adrenaline",
            description: """
            Gain 1 Energy.
            Draw 2 cards.
            """,
            energyCost: .int(0),
            rarity: .rare,
            cardType: .skill,
            cardPool: .silent,
            portraitURL: nil
        ),
        Card(
            id: "MEMENTO_MORI",
            title: "Memento Mori",
            description: """
            Deal damage.
            Deals additional damage for each card discarded this turn.
            """,
            energyCost: .int(1),
            rarity: .uncommon,
            cardType: .attack,
            cardPool: .silent,
            portraitURL: nil
        ),
        Card(
            id: "DEFEND_REGENT",
            title: "Defend",
            description: "Gain 5 Block.",
            energyCost: .int(1),
            rarity: .basic,
            cardType: .skill,
            cardPool: .regent,
            portraitURL: nil
        ),
        Card(
            id: "DEATHBRINGER",
            title: "Deathbringer",
            description: """
            Apply 21 Doom and 1 Weak to ALL enemies.
            """,
            energyCost: .int(2),
            rarity: .uncommon,
            cardType: .skill,
            cardPool: .necrobinder,
            portraitURL: nil
        ),
        Card(
            id: "MASTER_OF_STRATEGY",
            title: "Master of Strategy",
            description: "Draw 3 cards.",
            energyCost: .int(0),
            rarity: .rare,
            cardType: .skill,
            cardPool: .colorless,
            portraitURL: nil
        ),
        Card(
            id: "DOUBT",
            title: "Doubt",
            description: """
            At the end of your turn, if this is in your Hand, gain 1 Weak.
            """,
            energyCost: .int(-1),
            rarity: .curse,
            cardType: .curse,
            cardPool: .curse,
            portraitURL: nil
        ),
        Card(
            id: "WOUND",
            title: "Wound",
            description: "",
            energyCost: .int(-1),
            rarity: .status,
            cardType: .status,
            cardPool: .status,
            portraitURL: nil
        ),
        Card(
            id: "LANTERN_KEY",
            title: "Lantern Key",
            description: "Unlocks a special event in the next Act.",
            energyCost: .int(-1),
            rarity: .quest,
            cardType: .quest,
            cardPool: .quest,
            portraitURL: nil
        ),
        Card(
            id: "HELLO_WORLD",
            title: "Hello World",
            description: """
            At the start of your turn, add a random Common card into your Hand.
            """,
            energyCost: .int(1),
            rarity: .event,
            cardType: .power,
            cardPool: .event,
            portraitURL: nil
        )
    ]
}
