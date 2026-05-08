import SwiftUI
import UIKit

enum StsColors {
    // Mirrors `Lab/decompiled/.../StsColors.cs`: upstream uses hex strings for
    // most colors and float RGB(A) constructors for black/white/gray variants.
    static let aqua = UIColor(hex: 0x2AEBBE)
    static let cream = UIColor(hex: 0xFFF6E2)
    static let halfTransparentCream = UIColor(hex: 0xFFF6E2, alpha: 0.5)
    static let gold = UIColor(hex: 0xEFC851)
    static let red = UIColor(hex: 0xFF5555)
    static let green = UIColor(hex: 0x7FFF00)
    static let blue = UIColor(hex: 0x87CEEB)
    static let darkBlue = UIColor(hex: 0x67AEEB)
    static let orange = UIColor(hex: 0xFFA518)
    static let pink = UIColor(hex: 0xFF78A0)
    static let purple = UIColor(hex: 0xEE82EE)
    static let blueGlow = UIColor(hex: 0x78FFFE, alpha: 0.75)
    static let redGlow = UIColor(hex: 0xFF0000)
    static let disabledTextForPotionPopup = UIColor(hex: 0x5E5E5E)
    static let screenBackdrop = UIColor(red: 0, green: 0, blue: 0, alpha: 0.8)
    static let transparentBlack = UIColor(red: 0, green: 0, blue: 0, alpha: 0)
    static let halfTransparentBlack = UIColor(red: 0, green: 0, blue: 0, alpha: 0.5)
    static let ninetyPercentBlack = UIColor(red: 0, green: 0, blue: 0, alpha: 0.9)
    static let transparentWhite = UIColor(red: 1, green: 1, blue: 1, alpha: 0)
    static let halfTransparentWhite = UIColor(red: 1, green: 1, blue: 1, alpha: 0.5)
    static let disabledTopBarButton = UIColor(red: 0.5, green: 0.5, blue: 0.5, alpha: 0.75)
    static let quarterTransparentBlack = UIColor(red: 0, green: 0, blue: 0, alpha: 0.25)
    static let quarterTransparentWhite = UIColor(red: 1, green: 1, blue: 1, alpha: 0.25)
    static let exhaustGray = UIColor(red: 0.1, green: 0.1, blue: 0.1, alpha: 0)
    static let lightGray = UIColor(red: 0.75, green: 0.75, blue: 0.75, alpha: 1)
    static let gray = UIColor(red: 0.5, green: 0.5, blue: 0.5, alpha: 1)
    static let placeholderGrayTabButton = UIColor(red: 0.75, green: 0.75, blue: 0.75, alpha: 1)
    static let settingTabsButtonOutline = UIColor(hex: 0xB1F8FF)
    static let settingTabsButtonOutlineFiftyPercent = UIColor(hex: 0xB1F8FF, alpha: 0.5)
    static let bossNodeUntraveled = UIColor(hex: 0x7D6A55, alpha: 0.8470588235)
    static let pathDotTraveled = UIColor(hex: 0x241F1A)
    static let legendText = UIColor(hex: 0x2B3152)
    static let defaultEnergyCostOutline = UIColor(hex: 0x4D4A43, alpha: 0.862745098)
    static let unplayableEnergyCostOutline = UIColor(hex: 0x501717)
    static let defaultStarCostOutline = UIColor(hex: 0x175561, alpha: 0.862745098)
    static let cardTitleOutlineCommon = UIColor(hex: 0x4D4B40)
    static let cardTitleOutlineUncommon = UIColor(hex: 0x005C75)
    static let cardTitleOutlineRare = UIColor(hex: 0x6B4B00)
    static let cardTitleOutlineCurse = UIColor(hex: 0x550B9E)
    static let cardTitleOutlineQuest = UIColor(hex: 0x7E3E15)
    static let cardTitleOutlineStatus = UIColor(hex: 0x4F522F)
    static let cardTitleOutlineSpecial = UIColor(hex: 0x1B6131)
    static let energyBlue = UIColor(hex: 0x40FFFF)
    static let energyBlueOutline = UIColor(hex: 0x20595C)
    static let energyGreenOutline = UIColor(hex: 0x1F5923)
    static let rewardLabelOutline = UIColor(hex: 0x225157)
    static let rewardLabelGoldOutline = UIColor(hex: 0x4B4511)
    static let targetingArrowEnemy = UIColor(hex: 0xE61E1B)
    static let targetingArrowAlly = UIColor(hex: 0x36C78A)
    static let hpBarBackground = UIColor(hex: 0x001134, alpha: 0.5)
    static let merchantBlue = UIColor(hex: 0x516ACF)
}

private extension UIColor {
    convenience init(hex: UInt32, alpha: CGFloat = 1) {
        self.init(
            red: CGFloat((hex >> 16) & 0xFF) / 255,
            green: CGFloat((hex >> 8) & 0xFF) / 255,
            blue: CGFloat(hex & 0xFF) / 255,
            alpha: alpha
        )
    }
}
