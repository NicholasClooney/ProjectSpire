import SwiftUI

struct CardDetailView: View {
    let card: Card

    var body: some View {
        GeometryReader { geo in
            let padding: CGFloat = 24
            let scale = min(
                (geo.size.width - padding * 2) / CardView.Constraints.width,
                (geo.size.height - padding * 2) / CardView.Constraints.height
            )
            CardView(card: card)
                .scaleEffect(scale)
                .position(
                    x: geo.size.width / 2,
                    y: geo.size.height / 2
                )
        }
        .background(NeowSCafeTheme.background)
        .navigationTitle(card.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}
