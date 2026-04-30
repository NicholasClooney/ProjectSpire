//
//  CardAssetColor.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 29/04/2026.
//

import SwiftUI

enum CardAssetColor {
    case ironcladFrameRed
    case silentFrameGreen
    case defectFrameBlue
    case regentFrameOrange
    case necrobinderFramePink
    case colorlessFrameWhite
    case curseFramePurple
    case questFrameWhite
    case ancientBannerGray
    case commonBannerGray
    case uncommonBannerWhite
    case rareBannerBlue
    case curseBannerGreen
    case statusBannerBlue
    case eventBannerMagenta
    case questBannerCyan

    var hueRotation: Angle {
        switch self {
        case .ironcladFrameRed:
            return .degrees(9)
        case .silentFrameGreen:
            return .degrees(115.2)
        case .defectFrameBlue:
            return .degrees(198)
        case .regentFrameOrange:
            return .degrees(43.2)
        case .necrobinderFramePink:
            return .degrees(347.4)
        case .colorlessFrameWhite:
            return .degrees(0)
        case .curseFramePurple:
            return .degrees(306)
        case .questFrameWhite:
            return .degrees(0)
        case .ancientBannerGray:
            return .degrees(0)
        case .commonBannerGray:
            return .degrees(0)
        case .uncommonBannerWhite:
            return .degrees(0)
        case .rareBannerBlue:
            return .degrees(202.68)
        case .curseBannerGreen:
            return .degrees(97.2)
        case .statusBannerBlue:
            return .degrees(228.24)
        case .eventBannerMagenta:
            return .degrees(315)
        case .questBannerCyan:
            return .degrees(185.4)
        }
    }

    var saturation: Double {
        switch self {
        case .ironcladFrameRed:
            return 1.275
        case .silentFrameGreen:
            return 0.675
        case .defectFrameBlue:
            return 1.35
        case .regentFrameOrange:
            return 2.25
        case .necrobinderFramePink:
            return 0.825
        case .colorlessFrameWhite:
            return 0
        case .curseFramePurple:
            return 0.075
        case .questFrameWhite:
            return 1.5
        case .ancientBannerGray:
            return 0.3
        case .commonBannerGray:
            return 0
        case .uncommonBannerWhite:
            return 1.5
        case .rareBannerBlue:
            return 1.797
        case .curseBannerGreen:
            return 1.65
        case .statusBannerBlue:
            return 0.525
        case .eventBannerMagenta:
            return 1.275
        case .questBannerCyan:
            return 2.5905
        }
    }

    var brightness: Double {
        switch self {
        case .ironcladFrameRed:
            return 0
        case .silentFrameGreen:
            return 0.08
        case .defectFrameBlue:
            return 0.02
        case .regentFrameOrange:
            return 0.08
        case .necrobinderFramePink:
            return 0.08
        case .colorlessFrameWhite:
            return 0.08
        case .curseFramePurple:
            return -0.18
        case .questFrameWhite:
            return 0
        case .ancientBannerGray:
            return -0.04
        case .commonBannerGray:
            return -0.06
        case .uncommonBannerWhite:
            return 0
        case .rareBannerBlue:
            return 0.056
        case .curseBannerGreen:
            return -0.04
        case .statusBannerBlue:
            return -0.08
        case .eventBannerMagenta:
            return -0.04
        case .questBannerCyan:
            return -0.04
        }
    }
}
