import SwiftUI
import UIKit

enum NeowSCafeTypography {
    enum Weight {
        case regular
        case bold

        fileprivate var font: NeowSCafeFontConvertible {
            switch self {
            case .regular:
                return NeowSCafeFontFamily.Kreon.regular
            case .bold:
                return NeowSCafeFontFamily.Kreon.bold
            }
        }
    }

    enum Tier {
        case largeTitle
        case title
        case title2
        case title3
        case headline
        case body
        case callout
        case subheadline
        case footnote
        case caption
        case caption2
        case cardTitle
        case cardType
        case cardEnergy
        case cardDescription

        var size: CGFloat {
            switch self {
            case .largeTitle, .cardEnergy:
                return 32
            case .title, .cardTitle:
                return 26
            case .title2:
                return 24
            case .title3, .cardDescription:
                return 21
            case .headline:
                return 18
            case .body:
                return 17
            case .callout, .cardType:
                return 16
            case .subheadline:
                return 15
            case .footnote:
                return 13
            case .caption:
                return 12
            case .caption2:
                return 11
            }
        }
    }

    static func registerFonts() {
        NeowSCafeFontFamily.registerAllCustomFonts()
    }

    static func uiFont(_ tier: Tier, weight: Weight = .regular) -> UIFont {
        weight.font.font(size: tier.size)
    }

    static func swiftUIFont(_ tier: Tier, weight: Weight = .regular) -> Font {
        weight.font.swiftUIFont(size: tier.size)
    }
}

extension Font {
    static func neow(_ tier: NeowSCafeTypography.Tier, weight: NeowSCafeTypography.Weight = .regular) -> Font {
        NeowSCafeTypography.swiftUIFont(tier, weight: weight)
    }
}

extension UIFont {
    static func neow(_ tier: NeowSCafeTypography.Tier, weight: NeowSCafeTypography.Weight = .regular) -> UIFont {
        NeowSCafeTypography.uiFont(tier, weight: weight)
    }
}
