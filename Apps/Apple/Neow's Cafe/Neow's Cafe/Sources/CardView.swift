//
//  CardView.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 28/04/2026.
//

import SwiftUI
import UIKit

struct CardView: View {
    @State private var offset: CGSize = .zero

    let card: Card

    var body: some View {
        ZStack(alignment: .topLeading) {
            portrait
            frame
            portraitBorder
            titleBanner

            title
            typePlaque
            typeText
            energyIcon
            energyText
            description
        }
        .frame(width: 300, height: 422, alignment: .topLeading)
        .rotation3DEffect(
            .degrees(Double(offset.height / 50)),
            axis: (x: 1, y: 0, z: 0)
        )
        .rotation3DEffect(
            .degrees(Double(-offset.width / 50)),
            axis: (x: 0, y: 1, z: 0)
        )
        .gesture(
            DragGesture()
                .onChanged { value in
                    offset = value.translation
                }
                .onEnded { _ in
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                        offset = .zero
                    }
                }
        )
        .animation(.interactiveSpring(), value: offset)
    }

    var titleBanner: some View {
        Image(card.banner)
            .resizable()
            .cardAssetColor(card.rarityColor)
            .frame(width: 327, height: 83)
            .offset(x: -13, y: 14)
    }

    var portrait: some View {
        Image(card.portrait)
            .resizable()
            .frame(width: 250, height: 190)
            .offset(x: 25, y: 43)
    }

    var frame: some View {
        Image(card.frame)
            .resizable()
            .cardAssetColor(card.frameColor)
            .frame(width: 300, height: 422)
            .offset(x: 0, y: 0)
    }

    @ViewBuilder
    var portraitBorder: some View {
        if let border = card.portraitBorder {
            Image(border)
                .resizable()
                .cardAssetColor(card.rarityColor)
                .frame(width: 275, height: 210)
                .offset(x: 12.5, y: 47)
        }
    }

    var title: some View {
        BallLightningTextEffect(
            text: card.title,
            font: NeowSCafeFontFamily.Kreon.regular.font(size: 26),
        )
        .frame(width: 250, height: 54)
        .offset(x: 25, y: 7)
    }

    var typePlaque: some View {
        Image(ImageResource.cardPortraitBorderPlaqueS)
            .resizable()
            .cardAssetColor(card.rarityColor)
            .frame(width: 61, height: 37)
            .offset(x: 119.5, y: 212)
    }

    var typeText: some View {
        Text(card.typeText)
            .font(NeowSCafeFontFamily.Kreon.bold.swiftUIFont(size: 16))
            .foregroundStyle(Color.black.opacity(0.75))
            .frame(width: 61, height: 37)
            .offset(x: 119.5, y: 212)
    }

    @ViewBuilder
    var energyIcon: some View {
        if card.energyCost >= 0 {
            Image(card.energyIcon)
                .resizable()
                .frame(width: 64, height: 64)
                .offset(x: -16, y: -16)
        }
    }

    var energyText: some View {
        BallLightningTextEffect(
            text: card.energyCostText,
            font: NeowSCafeFontFamily.Kreon.regular.font(size: 32),
        )
        .frame(width: 64, height: 64)
        .offset(x: -16, y: -16)
    }

    var description: some View {
        Text(card.description)
            .font(NeowSCafeFontFamily.Kreon.regular.swiftUIFont(size: 21))
            .foregroundStyle(Color(red: 1, green: 0.965, blue: 0.886))
            .shadow(color: Color.black.opacity(0.55), radius: 0, x: 2, y: 2)
            .multilineTextAlignment(.center)
            .frame(width: 243, height: 136)
            .offset(x: 28, y: 248)
    }
}

// NOTE: `private extension` makes sense here since this is the only place accessing these values.
// However, it will make all the properties below inaccessible to testing.
// But tests still can be done by doing snapshot testing.
// Just some thoughts.
private extension Card {
    /// Decided by `rarity`
    var banner: ImageResource {
        switch rarity {
        case .ancient:
                .ancientBanner
        default:
                .cardBanner
        }
    }

    /// Decided by `id.lowercased()`
    var portrait: ImageResource {
        .init(name: id.lowercased(), bundle: .module)
    }

    /// Decided by `rarity`
    /// Used for banner, portrait border, and plaque
    var rarityColor: CardAssetColor {
        switch rarity {
        case .basic, .common, .token:
            return .commonBannerGray
        case .uncommon:
            return .uncommonBannerWhite
        case .rare:
            return .rareBannerBlue
        case .ancient:
            return .ancientBannerGray
        case .event:
            return .eventBannerMagenta
        case .status:
            return .statusBannerBlue
        case .curse:
            return .curseBannerGreen
        case .quest:
            return .questBannerCyan
        }
    }

    /// Decided by `cardType` && `rarity`
    var frame: ImageResource {
        if rarity == .ancient {
            return .cardFrameAncientS
        }

        switch cardType {
        case .attack:
            return .cardFrameAttackS
        case .power:
            return .cardFramePowerS
        case .quest:
            return .cardFrameQuestS
        case .skill:
            return .cardFrameSkillS
        case .curse, .status:
            return .cardFrameSkillS
        }
    }

    /// Decided by `cardPool`
    var frameColor: CardAssetColor {
        switch cardPool {
        case .ironclad:
            return .ironcladFrameRed
        case .silent:
            return .silentFrameGreen
        case .defect:
            return .defectFrameBlue
        case .regent:
            return .regentFrameOrange
        case .necrobinder:
            return .necrobinderFramePink
        case .colorless, .status, .event, .token, .depreacated, .mock:
            return .colorlessFrameWhite
        case .curse:
            return .curseFramePurple
        case .quest:
            return .questFrameWhite
        }
    }

    /// Decided by `cardType`
    var portraitBorder: ImageResource? {
        if rarity == .ancient {
            return nil
        }
        switch cardType {
        case .attack:
            return .cardPortraitBorderAttackS
        case .power:
            return .cardPortraitBorderPowerS
        case .skill:
            return .cardPortraitBorderSkillS
        case .curse, .quest, .status:
            return .cardPortraitBorderSkillS
        }
    }

    /// Decided by `cardType`
    var typeText: String {
        cardType.rawValue.capitalized
    }

    var energyCostText: String {
        energyCost < 0 ? "" : "\(energyCost)"
    }

    // Decided by `cardPool`
    var energyIcon: ImageResource {
        switch cardPool {
        case .ironclad:
            return .energyIronclad
        case .silent:
            return .energySilent
        case .defect:
            return .energyDefect
        case .regent:
            return .energyRegent
        case .necrobinder:
            return .energyNecrobinder
        case .quest:
            return .energyQuest
        case .colorless, .curse, .status, .event, .token, .depreacated, .mock:
            return .energyColorless
        }
    }
}


private extension Image {
    func cardAssetColor(_ approximation: CardAssetColor) -> some View {
        self
            .hueRotation(approximation.hueRotation)
            .saturation(approximation.saturation)
            .brightness(approximation.brightness)
    }
}
