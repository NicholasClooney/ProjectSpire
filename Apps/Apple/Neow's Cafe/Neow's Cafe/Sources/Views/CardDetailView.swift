import SwiftUI

struct CardDetailView: View {
    let card: Card

    @State private var showingUpgrade = false

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            GeometryReader { geo in
                let scale = geo.size.width / CardView.Constraints.width
                CardView(card: card)
                    .scaleEffect(scale, anchor: .topLeading)
            }
            .aspectRatio(CardView.Constraints.width / CardView.Constraints.height, contentMode: .fit)
            .padding(.horizontal, 24)

            Spacer()

            viewUpgradesButton
                .padding(.bottom, 24)
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

#Preview("Common Attack") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[0])
    }
}

#Preview("Ancient Power") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[2])
    }
}

#Preview("Dark Mode") {
    NavigationStack {
        CardDetailView(card: MockCards.cards[3])
    }
    .preferredColorScheme(.dark)
}
