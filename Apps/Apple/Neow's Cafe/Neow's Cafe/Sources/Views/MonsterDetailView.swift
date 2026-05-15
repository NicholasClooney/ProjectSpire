import SwiftUI

struct MonsterDetailView: View {
    let monster: Monster

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                hpSection

                Divider()
                    .overlay(NeowSCafeTheme.separator)

                Text("Moves")
                    .font(.neow(.headline, weight: .bold))
                    .foregroundStyle(NeowSCafeTheme.text)

                ForEach(monster.moves, id: \.id) { move in
                    MoveCard(move: move)
                }
            }
            .padding(20)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(NeowSCafeTheme.background)
        .navigationTitle(monster.name)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var hpSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Hit Points")
                .font(.neow(.caption, weight: .bold))
                .foregroundStyle(NeowSCafeTheme.secondaryText)

            HStack(spacing: 16) {
                HPPill(label: "Base", value: monster.hp.displayRange, color: Color(StsColors.green))

                if let asc = monster.hp.ascensionRange {
                    HPPill(label: "Ascension", value: asc, color: Color(StsColors.red))
                }
            }
        }
    }
}

private struct HPPill: View {
    let label: String
    let value: String
    let color: Color

    var body: some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.neow(.caption2))
                .foregroundStyle(NeowSCafeTheme.secondaryText)
            Text(value)
                .font(.neow(.title3, weight: .bold))
                .foregroundStyle(color)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background {
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .fill(NeowSCafeTheme.surface)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .stroke(color.opacity(0.4), lineWidth: 1.5)
        }
    }
}

private struct MoveCard: View {
    let move: Monster.Move

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(move.title)
                .font(.neow(.body, weight: .bold))
                .foregroundStyle(NeowSCafeTheme.text)

            if let effects = move.effects {
                if !effects.intents.isEmpty {
                    IntentsRow(intents: effects.intents)
                }

                VStack(alignment: .leading, spacing: 6) {
                    if let block = effects.block {
                        effectRow(icon: "shield.fill", label: "Block \(block)", color: Color(StsColors.blue))
                    }
                    ForEach(effects.powers, id: \.name) { power in
                        let label = power.amount.map { "\(power.name) \($0)" } ?? power.name
                        effectRow(icon: "bolt.fill", label: label, color: Color(StsColors.gold))
                    }
                    ForEach(effects.statusCards, id: \.card) { sc in
                        effectRow(icon: "rectangle.stack.fill", label: "\(sc.card) x\(sc.count) → \(sc.pile)", color: Color(StsColors.purple))
                    }
                    if let heal = effects.heal {
                        effectRow(icon: "cross.fill", label: "Heal \(heal)", color: Color(StsColors.green))
                    }
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(NeowSCafeTheme.surface)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(NeowSCafeTheme.separator.opacity(0.4), lineWidth: 1)
        }
    }

    private func effectRow(icon: String, label: String, color: Color) -> some View {
        HStack(spacing: 8) {
            Image(systemName: icon)
                .font(.neow(.caption))
                .foregroundStyle(color)
                .frame(width: 16)
            Text(label)
                .font(.neow(.body))
                .foregroundStyle(NeowSCafeTheme.text)
        }
    }
}

private struct IntentsRow: View {
    let intents: [Monster.Move.Intent]

    var body: some View {
        ScrollView(.horizontal) {
            HStack(spacing: 8) {
                ForEach(intents.indices, id: \.self) { i in
                    IntentBadge(intent: intents[i])
                }
            }
        }
        .scrollIndicators(.hidden)
    }
}

private struct IntentBadge: View {
    let intent: Monster.Move.Intent

    var body: some View {
        VStack(spacing: 2) {
            Text(intent.kind)
                .font(.neow(.caption2, weight: .bold))
                .foregroundStyle(intentColor)

            if let dmgText = intent.damageText {
                Text(dmgText)
                    .font(.neow(.caption2))
                    .foregroundStyle(Color(StsColors.red))
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background {
            Capsule()
                .fill(intentColor.opacity(0.15))
        }
        .overlay {
            Capsule()
                .stroke(intentColor.opacity(0.5), lineWidth: 1)
        }
    }

    private var intentColor: Color {
        switch intent.kind {
        case "SingleAttack", "MultiAttack", "DeathBlow": return Color(StsColors.red)
        case "Defend": return Color(StsColors.blue)
        case "Buff": return Color(StsColors.green)
        case "Debuff", "CardDebuff": return Color(StsColors.purple)
        case "Status": return Color(StsColors.orange)
        case "Heal": return Color(StsColors.green)
        default: return Color(StsColors.cream)
        }
    }
}

#Preview("Axebot") {
    NavigationStack {
        MonsterDetailView(monster: MockMonsters.monsters[0])
    }
}

#Preview("Cultist") {
    NavigationStack {
        MonsterDetailView(monster: MockMonsters.monsters[2])
    }
}
