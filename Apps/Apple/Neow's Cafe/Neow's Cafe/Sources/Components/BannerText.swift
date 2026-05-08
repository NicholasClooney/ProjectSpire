import SwiftUI
import UIKit

struct BannerText: View {
    var text: String
    var font: UIFont
    var textColor: UIColor = StsColors.cream
    var outlineColor: UIColor = StsColors.cardTitleOutlineCommon

    var body: some View {
        ZStack {
            OutlinedLabelView(
                text: text,
                font: font,
                textColor: .clear,
                outlineColor: outlineColor,
                outlineWidth: 5
            )

            OutlinedLabelView(
                text: text,
                font: font,
                textColor: textColor,
                outlineColor: .clear,
                outlineWidth: 0
            )
        }
        .shadow(color: Color(StsColors.halfTransparentBlack), radius: 3, x: 0, y: 2)
        .fixedSize()
    }
}

#Preview {
    BannerText(
        text: "Ball Lightning",
        font: .neow(.cardEnergy),
    )
    .padding(32)
    .background(Color(StsColors.gray))
}
