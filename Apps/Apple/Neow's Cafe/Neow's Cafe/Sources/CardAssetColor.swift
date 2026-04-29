//
//  CardAssetColor.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 29/04/2026.
//

import SwiftUI

enum CardAssetColor {
    case defectFrameBlue
    case commonBannerGray

    var hueRotation: Angle {
        switch self {
        case .defectFrameBlue:
            return .degrees(198)
        case .commonBannerGray:
            return .degrees(0)
        }
    }

    var saturation: Double {
        switch self {
        case .defectFrameBlue:
            return 1.35
        case .commonBannerGray:
            return 0
        }
    }

    var brightness: Double {
        switch self {
        case .defectFrameBlue:
            return 0.02
        case .commonBannerGray:
            return -0.06
        }
    }
}
