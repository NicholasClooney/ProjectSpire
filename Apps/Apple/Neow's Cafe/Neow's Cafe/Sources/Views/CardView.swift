//
//  CardView.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 28/04/2026.
//

import SwiftUI
import UIKit

struct CardView: View {
    enum Constraints {
        static let width: CGFloat = 300
        static let height: CGFloat = 422
    }

    @State private var offset: CGSize = .zero

    let card: Card

    var body: some View {
        ZStack(alignment: .topLeading) {
            if card.isAncient {
                ancientPortrait
                ancientHighlight
                ancientBorder
                ancientTextBackground
                ancientTitleBanner
            } else {
                portrait
                frame
                portraitBorder
                titleBanner
            }

            title
            typePlaque
            typeText
            energyIcon
            energyText
            rulesText
        }
        .frame(width: Constraints.width, height: Constraints.height, alignment: .topLeading)
//        .rotation3DEffect(
//            .degrees(Double(offset.height / 50)),
//            axis: (x: 1, y: 0, z: 0)
//        )
//        .rotation3DEffect(
//            .degrees(Double(-offset.width / 50)),
//            axis: (x: 0, y: 1, z: 0)
//        )
//        .gesture(
//            DragGesture()
//                .onChanged { value in
//                    offset = value.translation
//                }
//                .onEnded { _ in
//                    withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
//                        offset = .zero
//                    }
//                }
//        )
//        .animation(.interactiveSpring(), value: offset)
    }

    var ancientTitleBanner: some View {
        Image(card.banner)
            .resizable()
            .frame(width: 327, height: 83)
            .offset(x: -13, y: 4)
    }

    var titleBanner: some View {
        Image(card.banner)
            .resizable()
            .cardAssetColor(card.rarityColor)
            .frame(width: 327, height: 83)
            .offset(x: -13, y: 14)
    }

    @ViewBuilder
    var portrait: some View {
        cardPortraitImage
            .frame(width: 250, height: 190)
            .offset(x: 25, y: 43)
    }

    @ViewBuilder
    var ancientPortrait: some View {
        cardPortraitImage
            .frame(width: 299, height: 421)
            .mask(alignment: .topLeading) {
                Image(card.ancientPortraitMask)
                    .resizable()
                    .frame(width: 300, height: 423.5)
                    .offset(x: 2, y: 4)
            }
            .offset(x: -3, y: -4)
    }

    @ViewBuilder
    var cardPortraitImage: some View {
        if let portraitURL = card.portraitURL {
            AsyncImage(url: portraitURL) { phase in
                switch phase {
                case .success(let image):
                    image.resizable()
                case .empty:
                    portraitPlaceholder
                case .failure:
                    portraitPlaceholder
                @unknown default:
                    portraitPlaceholder
                }
            }
        } else {
            portraitPlaceholder
        }
    }

    var portraitPlaceholder: some View {
        Rectangle()
            .fill(Color.black.opacity(0.35))
            .overlay {
                Image(systemName: "photo")
                    .font(.system(size: 32))
                    .foregroundStyle(Color.white.opacity(0.45))
            }
    }

    var frame: some View {
        Image(card.frame)
            .resizable()
            .cardAssetColor(card.frameColor)
            .frame(width: 300, height: 422)
            .offset(x: 0, y: 0)
    }

    var ancientHighlight: some View {
        Image(card.ancientHighlight)
            .resizable()
            .opacity(0.75)
            .frame(width: 310, height: 437)
            .offset(x: -6, y: -9)
    }

    var ancientBorder: some View {
        Image(card.ancientBorder)
            .resizable()
            .frame(width: 306, height: 440)
            .offset(x: -4, y: -12)
    }

    var ancientTextBackground: some View {
        Image(card.ancientTextBackground)
            .resizable()
            .frame(width: 264, height: 203)
            .offset(x: 18, y: 191)
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
        BannerText(
            text: card.displayTitle,
            font: .neow(.cardTitle),
            textColor: card.titleTextColor,
            outlineColor: card.titleOutlineColor
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
            .font(.neow(.cardType, weight: .bold))
            .foregroundStyle(Color.black.opacity(0.75))
            .frame(width: 61, height: 37)
            .offset(x: 119.5, y: 212)
    }

    @ViewBuilder
    var energyIcon: some View {
        if card.showsEnergyIcon {
            Image(card.energyIcon)
                .resizable()
                .frame(width: 64, height: 64)
                .offset(x: -16, y: -16)
        }
    }

    var energyText: some View {
        BannerText(
            text: card.energyCostText,
            font: .neow(.cardEnergy),
        )
        .frame(width: 64, height: 64)
        .offset(x: -16, y: -16)
    }

    var rulesText: some View {
        Text(card.rulesAttributedString)
            .shadow(color: Color.black.opacity(0.55), radius: 0, x: 2, y: 2)
            .multilineTextAlignment(.center)
            .lineLimit(10)
            .minimumScaleFactor(0.55)
            .allowsTightening(true)
            .frame(width: 243, height: 136)
            .offset(x: 28, y: 248)
    }
}

// NOTE: `private extension` makes sense here since this is the only place accessing these values.
// However, it will make all the properties below inaccessible to testing.
// But tests still can be done by doing snapshot testing.
// Just some thoughts.
private extension Card {
    var isAncient: Bool {
        rarity == .ancient
    }

    var displayTitle: String {
        guard upgradeLevel > 0 else { return title }
        return maxUpgradeLevel > 1 ? "\(title)+\(upgradeLevel)" : "\(title)+"
    }

    // StsColors.green (#7FFF00) and cardTitleOutlineSpecial (#1B6131)
    var titleTextColor: UIColor {
        upgradeLevel > 0
            ? UIColor(red: 0.498, green: 1.0, blue: 0.0, alpha: 1)
            : UIColor(red: 0.96, green: 0.96, blue: 0.94, alpha: 1)
    }

    var titleOutlineColor: UIColor {
        guard upgradeLevel > 0 else { return rarityTitleOutlineColor }
        return UIColor(red: 0.106, green: 0.380, blue: 0.192, alpha: 1)
    }

    /// Rarity-based outline color for the unupgraded title, matching StsColors
    private var rarityTitleOutlineColor: UIColor {
        switch rarity {
        case .uncommon:
            return UIColor(red: 0.0, green: 0.361, blue: 0.459, alpha: 1)   // #005C75
        case .rare:
            return UIColor(red: 0.420, green: 0.294, blue: 0.0, alpha: 1)   // #6B4B00
        case .curse:
            return UIColor(red: 0.333, green: 0.043, blue: 0.620, alpha: 1) // #550B9E
        case .quest:
            return UIColor(red: 0.494, green: 0.243, blue: 0.082, alpha: 1) // #7E3E15
        case .status:
            return UIColor(red: 0.310, green: 0.322, blue: 0.184, alpha: 1) // #4F522F
        case .event:
            return UIColor(red: 0.106, green: 0.380, blue: 0.192, alpha: 1) // #1B6131
        default:
            return UIColor(red: 0.302, green: 0.294, blue: 0.251, alpha: 1) // #4D4B40
        }
    }

    /// Decided by `rarity`
    var banner: ImageResource {
        switch rarity {
        case .ancient:
                .ancientBanner
        default:
                .cardBanner
        }
    }

    var ancientBorder: ImageResource {
        .init(name: "ancient_card_border", bundle: .module)
    }

    var ancientHighlight: ImageResource {
        .init(name: "card_highlight_ancient", bundle: .module)
    }

    var ancientPortraitMask: ImageResource {
        .init(name: "ancient_portrait_mask_large", bundle: .module)
    }

    var ancientTextBackground: ImageResource {
        switch cardType {
        case .attack:
            return .init(name: "ancient_card_text_bg_attack", bundle: .module)
        case .power:
            return .init(name: "ancient_card_text_bg_power", bundle: .module)
        case .skill, .curse, .quest, .status:
            return .init(name: "ancient_card_text_bg_skill", bundle: .module)
        }
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
        case .colorless, .status, .event, .token, .deprecated, .mock:
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
        switch energyCost {
        case .x:
            return "X"
        case .int(let value):
            return value < 0 ? "" : "\(value)"
        }
    }

    var showsEnergyIcon: Bool {
        switch energyCost {
        case .x:
            return true
        case .int(let value):
            return value >= 0
        }
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
        case .colorless, .curse, .status, .event, .token, .deprecated, .mock:
            return .energyColorless
        }
    }

    func keywordText(for placement: Keyword.Placement) -> String {
        keywords
            .filter { $0.placement == placement }
            .map { "\($0.title)\(keywordPeriod)" }
            .joined(separator: "\n")
    }

    var rulesAttributedString: AttributedString {
        var result = AttributedString()

        appendRulesText(keywordText(for: .beforeDescription), style: .keyword, to: &result)
        appendRulesText(description, style: .description, to: &result)
        appendRulesText(keywordText(for: .afterDescription), style: .keyword, to: &result)

        return result
    }

    private func appendRulesText(_ text: String, style: RulesTextStyle, to result: inout AttributedString) {
        guard !text.isEmpty else {
            return
        }

        if !result.characters.isEmpty {
            result += AttributedString("\n")
        }

        var segment = AttributedString(text)
        segment.font = style.font
        segment.foregroundColor = style.color
        result += segment
    }
}

private enum RulesTextStyle {
    case description
    case keyword

    var font: Font {
        switch self {
        case .description:
            return .neow(.cardDescription)
        case .keyword:
            return .neow(.cardDescription, weight: .bold)
        }
    }

    var color: Color {
        switch self {
        case .description:
            return Color(red: 1, green: 0.965, blue: 0.886)
        case .keyword:
            return Color(red: 0.965, green: 0.79, blue: 0.33)
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
