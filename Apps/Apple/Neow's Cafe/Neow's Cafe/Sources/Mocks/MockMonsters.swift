enum MockMonsters {
    static let monsters: [Monster] = [
        Monster(
            id: "AXEBOT",
            name: "Axebot",
            hp: Monster.HP(min: 160, max: 170, minAscension: 168, maxAscension: 178),
            moves: [
                Monster.Move(
                    id: "HAMMER_UPPERCUT",
                    title: "Hammer Uppercut",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "SingleAttack", damage: 8, damageAscension: 10, times: nil),
                            Monster.Move.Intent(kind: "Debuff", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [
                            Monster.Move.Power(name: "Weak", amount: 1),
                            Monster.Move.Power(name: "Frail", amount: 1)
                        ],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "PISTON_PUNCH",
                    title: "Piston Punch",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "MultiAttack", damage: 4, damageAscension: 5, times: 4)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "DEFENSIVE_MODE",
                    title: "Defensive Mode",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "Defend", damage: nil, damageAscension: nil, times: nil),
                            Monster.Move.Intent(kind: "Buff", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: 15,
                        blockAscension: 18,
                        powers: [],
                        statusCards: [],
                        heal: nil
                    )
                )
            ],
            portraitURL: nil
        ),
        Monster(
            id: "JAW_WORM",
            name: "Jaw Worm",
            hp: Monster.HP(min: 40, max: 44, minAscension: 42, maxAscension: 46),
            moves: [
                Monster.Move(
                    id: "CHOMP",
                    title: "Chomp",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "SingleAttack", damage: 11, damageAscension: 12, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "THRASH",
                    title: "Thrash",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "SingleAttack", damage: 7, damageAscension: nil, times: nil),
                            Monster.Move.Intent(kind: "Defend", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: 5,
                        blockAscension: nil,
                        powers: [],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "BELLOW",
                    title: "Bellow",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "Buff", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [
                            Monster.Move.Power(name: "Strength", amount: 3),
                            Monster.Move.Power(name: "Metallicize", amount: 2)
                        ],
                        statusCards: [],
                        heal: nil
                    )
                )
            ],
            portraitURL: nil
        ),
        Monster(
            id: "CULTIST",
            name: "Cultist",
            hp: Monster.HP(min: 48, max: 54, minAscension: 50, maxAscension: 56),
            moves: [
                Monster.Move(
                    id: "INCANTATION",
                    title: "Incantation",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "Buff", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [
                            Monster.Move.Power(name: "Ritual", amount: 3)
                        ],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "DARK_STRIKE",
                    title: "Dark Strike",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "SingleAttack", damage: 6, damageAscension: nil, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [],
                        statusCards: [],
                        heal: nil
                    )
                )
            ],
            portraitURL: nil
        ),
        Monster(
            id: "GREMLIN_NOB",
            name: "Gremlin Nob",
            hp: Monster.HP(min: 82, max: 86, minAscension: 85, maxAscension: 90),
            moves: [
                Monster.Move(
                    id: "BELLOW",
                    title: "Bellow",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "Buff", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [
                            Monster.Move.Power(name: "Enrage", amount: 2)
                        ],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "SKULL_BASH",
                    title: "Skull Bash",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "SingleAttack", damage: 6, damageAscension: nil, times: nil),
                            Monster.Move.Intent(kind: "Debuff", damage: nil, damageAscension: nil, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [
                            Monster.Move.Power(name: "Vulnerable", amount: 2)
                        ],
                        statusCards: [],
                        heal: nil
                    )
                ),
                Monster.Move(
                    id: "RUSH",
                    title: "Rush",
                    effects: Monster.Move.Effects(
                        intents: [
                            Monster.Move.Intent(kind: "SingleAttack", damage: 14, damageAscension: 16, times: nil)
                        ],
                        block: nil,
                        blockAscension: nil,
                        powers: [],
                        statusCards: [],
                        heal: nil
                    )
                )
            ],
            portraitURL: nil
        ),
    ]
}
