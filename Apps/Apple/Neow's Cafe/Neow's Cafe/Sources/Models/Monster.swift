import Foundation

struct Monster {
    let id: String
    let name: String
    let hp: HP
    let moves: [Move]
    let portraitURL: URL?

    struct HP {
        let min: Int
        let max: Int
        let minAscension: Int?
        let maxAscension: Int?

        var displayRange: String {
            min == max ? "\(min)" : "\(min)–\(max)"
        }

        var ascensionRange: String? {
            guard let lo = minAscension, let hi = maxAscension else { return nil }
            return lo == hi ? "\(lo)" : "\(lo)–\(hi)"
        }
    }

    struct Move {
        let id: String
        let title: String
        let effects: Effects?

        struct Effects {
            let intents: [Intent]
            let block: Int?
            let blockAscension: Int?
            let powers: [Power]
            let statusCards: [StatusCard]
            let heal: Int?
        }

        struct Intent {
            let kind: String
            let damage: Int?
            let damageAscension: Int?
            let times: Int?

            var displayName: String { kind }

            var damageText: String? {
                guard let d = damage else { return nil }
                let base = times.map { "\(d) x\($0)" } ?? "\(d)"
                if let asc = damageAscension {
                    return "\(base) (A: \(asc)\(times.map { " x\($0)" } ?? ""))"
                }
                return base
            }
        }

        struct Power {
            let name: String
            let amount: Int?
        }

        struct StatusCard {
            let card: String
            let count: Int
            let pile: String
        }
    }
}
