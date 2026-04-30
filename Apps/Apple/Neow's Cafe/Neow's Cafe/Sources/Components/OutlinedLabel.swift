import SwiftUI
import UIKit

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

        c?.setLineWidth(outlineWidth)
        c?.setLineJoin(.round)
        c?.setTextDrawingMode(.stroke)
        self.textAlignment = .center
        self.textColor = outlineColor
        super.drawText(in: insetRect)

        if let shadowColor = shadowColor {
            super.shadowColor = shadowColor
            super.shadowOffset = shadowOffset
            super.drawText(in: insetRect)
        }

        c?.setTextDrawingMode(.fill)
        self.textColor = textColor
        self.shadowOffset = CGSize(width: 0, height: 0)
        super.drawText(in: insetRect)

        self.shadowOffset = shadowOffset
    }
}

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
