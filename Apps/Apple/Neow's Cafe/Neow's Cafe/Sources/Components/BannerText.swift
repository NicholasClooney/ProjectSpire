import SwiftUI
import UIKit

struct BannerText: View {
    var text: String
    var font: UIFont

    var body: some View {
        ZStack {
            OutlinedLabelView(
                text: text,
                font: font,
                textColor: .clear,
                outlineColor: UIColor(red: 0.30078125, green: 0.29296875, blue: 0.25390625, alpha: 1),
                outlineWidth: 5
            )

            OutlinedLabelView(
                text: text,
                font: font,
                textColor: UIColor(red: 0.96, green: 0.96, blue: 0.94, alpha: 1),
                outlineColor: .clear,
                outlineWidth: 0
            )
        }
        .shadow(color: .black.opacity(0.5), radius: 3, x: 0, y: 2)
        .fixedSize()
    }
}

#Preview {
    BannerText(
        text: "Ball Lightning",
        font: NeowSCafeFontFamily.Kreon.regular.font(size: 32),
    )
    .padding(32)
    .background(Color(red: 0.55, green: 0.55, blue: 0.58))
}
