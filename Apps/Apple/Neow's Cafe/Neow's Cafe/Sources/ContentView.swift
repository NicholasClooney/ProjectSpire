import SwiftUI

public struct ContentView: View {
    public init() {}

    public var body: some View {
        ScrollView {
            LazyVGrid(
                columns: [GridItem(.adaptive(minimum: 190), spacing: 24)],
                spacing: 32
            ) {
                ForEach(Self.previewCards, id: \.id) { card in
                    CardView(card: card)
                        .scaleEffect(0.6)
                        .frame(width: 180, height: 253)
                }
            }
            .padding(24)
        }
        .background(Color(red: 0.07, green: 0.075, blue: 0.08))
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
            rarity: .rare,
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
