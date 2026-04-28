//
//  OutlinedLabel.swift
//

import SwiftUI
import UIKit

// MARK: - UIKit Label

@IBDesignable
class OutlinedLabel: UILabel {

    @IBInspectable
    var outlineWidth: CGFloat = 0 {
        didSet { setNeedsLayout() }
    }

    @IBInspectable
    var outlineColor: UIColor = .clear {
        didSet { setNeedsLayout() }
    }

    override var intrinsicContentSize: CGSize {
        let size = super.intrinsicContentSize
        return CGSize(
            width: size.width + outlineWidth,
            height: size.height + outlineWidth
        )
    }

    override func drawText(in rect: CGRect) {
        let inset = outlineWidth / 2
        let insetRect = rect.insetBy(dx: inset, dy: inset)

        let shadowOffset = self.shadowOffset
        let textColor = self.textColor
        let c = UIGraphicsGetCurrentContext()

        // Stroke pass
        c?.setLineWidth(outlineWidth)
        c?.setLineJoin(.round)
        c?.setTextDrawingMode(.stroke)
        self.textAlignment = .center
        self.textColor = outlineColor
        super.drawText(in: insetRect)

        // Shadow pass
        if let shadowColor = shadowColor {
            super.shadowColor = shadowColor
            super.shadowOffset = shadowOffset
            super.drawText(in: insetRect)
        }

        // Fill pass
        c?.setTextDrawingMode(.fill)
        self.textColor = textColor
        self.shadowOffset = CGSize(width: 0, height: 0)
        super.drawText(in: insetRect)

        self.shadowOffset = shadowOffset
    }
}

// MARK: - SwiftUI Representable

struct OutlinedLabelView: UIViewRepresentable {
    var text: String
    var font: UIFont = .systemFont(ofSize: 17, weight: .bold)
    var textColor: UIColor = .label
    var outlineColor: UIColor = .black
    var outlineWidth: CGFloat = 2

    func makeUIView(context: Context) -> OutlinedLabel {
        let label = OutlinedLabel()
        label.textAlignment = .center
        label.setContentHuggingPriority(.required, for: .horizontal)
        label.setContentHuggingPriority(.required, for: .vertical)
        return label
    }

    func updateUIView(_ uiView: OutlinedLabel, context: Context) {
        uiView.text = text
        uiView.font = font
        uiView.textColor = textColor
        uiView.outlineColor = outlineColor
        uiView.outlineWidth = outlineWidth
    }
}

// MARK: - Ball Lightning Effect

struct BallLightningTextEffect: View {
    var text: String = "Ball Lightning"
    var font: UIFont = .systemFont(ofSize: 48, weight: .black)

    var body: some View {
        ZStack {
            // Layer 1: dark shell
            OutlinedLabelView(
                text: text,
                font: font,
                textColor: .clear,
                outlineColor: UIColor(red: 0.30078125, green: 0.29296875, blue: 0.25390625, alpha: 1),
                outlineWidth: 5
            )
            // Layer 2: bright near-white core
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

// MARK: - Preview

#Preview {
    BallLightningTextEffect(
        text: "Ball Lightning",
        font: NeowSCafeFontFamily.Kreon.regular.font(size: 32),
    )
    .padding(32)
    .background(Color(red: 0.55, green: 0.55, blue: 0.58))
}
