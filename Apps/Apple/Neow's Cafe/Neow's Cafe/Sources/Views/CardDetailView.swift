import SwiftUI

struct CardDetailView: View {
    let card: Card

    @State private var showingUpgrade = false

    private var displayedCard: Card {
        guard showingUpgrade, let upgrade = card.upgradeSummary else { return card }
        return Card(
            id: card.id,
            title: upgrade.title,
            description: upgrade.description,
            keywords: upgrade.keywords,
            keywordPeriod: upgrade.keywordPeriod,
            energyCost: upgrade.energyCost,
            upgradeLevel: 1,
            maxUpgradeLevel: card.maxUpgradeLevel,
            rarity: card.rarity,
            cardType: card.cardType,
            cardPool: card.cardPool,
            portraitURL: card.portraitURL
        )
    }

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            GeometryReader { geo in
                let scale = geo.size.width / CardView.Constraints.width
                CardView(card: displayedCard)
                    .scaleEffect(scale, anchor: .topLeading)
            }
            .aspectRatio(CardView.Constraints.width / CardView.Constraints.height, contentMode: .fit)
            .padding(.horizontal, 24)

            Spacer()

            if card.upgradeSummary != nil {
                viewUpgradesButton
                    .padding(.bottom, 24)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(NeowSCafeTheme.background)
        .navigationTitle(card.title)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var viewUpgradesButton: some View {
        Button {
            showingUpgrade.toggle()
        } label: {
            Label(
                "View Upgrades",
                systemImage: showingUpgrade ? "checkmark.square.fill" : "square"
            )
            .font(.neow(.headline, weight: .bold))
            .foregroundStyle(NeowSCafeTheme.accent)
        }
        .buttonStyle(.plain)
    }
}

#Preview("With Upgrade") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[1]) // Anger: 6→8 damage
    }
}

#Preview("Ancient Power") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[2]) // Corruption
    }
}

#Preview("Dark Mode") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[3]) // Adrenaline
    }
    .preferredColorScheme(.dark)
}

#Preview("No Upgrade (Curse)") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[8]) // Doubt
    }
}
