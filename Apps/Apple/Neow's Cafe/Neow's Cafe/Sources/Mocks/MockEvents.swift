enum MockEvents {
    static let events: [Event] = [
        Event(
            id: "BIG_FISH",
            title: "Big Fish",
            kind: .regular,
            pages: [
                Event.Page(
                    id: "INITIAL",
                    description: "You come across a large lake. A massive fish leaps from the water.",
                    options: [
                        Event.Option(id: "BANANA", text: "Eat the banana. (Heal 33% Max HP)"),
                        Event.Option(id: "DONUT", text: "Eat the donut. (Max HP +5)"),
                        Event.Option(id: "BOX", text: "Open the box. (Obtain a Relic)")
                    ]
                ),
                Event.Page(
                    id: "DONE",
                    description: "The fish returns to the depths.",
                    options: []
                )
            ],
            portraitURL: nil
        ),
        Event(
            id: "THE_CLERIC",
            title: "The Cleric",
            kind: .regular,
            pages: [
                Event.Page(
                    id: "INITIAL",
                    description: "A traveling priest offers you his services.",
                    options: [
                        Event.Option(id: "HEAL", text: "Pay 35 Gold to heal 25% Max HP."),
                        Event.Option(id: "PURIFY", text: "Pay 50 Gold to remove a card from your deck."),
                        Event.Option(id: "LEAVE", text: "Leave.")
                    ]
                )
            ],
            portraitURL: nil
        ),
        Event(
            id: "DEAD_ADVENTURER",
            title: "Dead Adventurer",
            kind: .regular,
            pages: [
                Event.Page(
                    id: "INITIAL",
                    description: "You find a dead adventurer. There are valuables nearby, but the body seems to be guarded by monsters.",
                    options: [
                        Event.Option(id: "SEARCH", text: "Search the body. (Gain 100 Gold)"),
                        Event.Option(id: "LEAVE", text: "Leave.")
                    ]
                )
            ],
            portraitURL: nil
        ),
        Event(
            id: "MUSHROOMS",
            title: "Mushrooms",
            kind: .regular,
            pages: [
                Event.Page(
                    id: "INITIAL",
                    description: "You find a patch of glowing mushrooms. They smell strange.",
                    options: [
                        Event.Option(id: "EAT", text: "Eat the mushrooms. (Fight a Fungi Beast, then obtain a Relic)"),
                        Event.Option(id: "STOMP", text: "Stomp them. (Gain 48 Gold)")
                    ]
                )
            ],
            portraitURL: nil
        ),
        Event(
            id: "OROBAS",
            title: "Orobas",
            kind: .ancient,
            pages: [
                Event.Page(
                    id: "INITIAL",
                    description: "A demonic horse-headed entity appears before you, offering a bargain.",
                    options: [
                        Event.Option(id: "DEAL", text: "Accept the deal."),
                        Event.Option(id: "DENY", text: "Deny the deal.")
                    ]
                )
            ],
            portraitURL: nil
        ),
    ]
}
