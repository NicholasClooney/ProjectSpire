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
            .fill(Color(StsColors.halfTransparentBlack))
            .overlay {
                Image(systemName: "photo")
                    .font(.system(size: 32))
                    .foregroundStyle(Color(StsColors.halfTransparentWhite))
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
            .foregroundStyle(Color(StsColors.ninetyPercentBlack))
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
            textColor: card.energyCostTextColor,
            outlineColor: card.energyCostOutlineColor
        )
        .frame(width: 64, height: 64)
        .offset(x: -16, y: -16)
    }

    var rulesText: some View {
        Text(card.rulesAttributedString)
            .shadow(color: Color(StsColors.halfTransparentBlack), radius: 0, x: 2, y: 2)
            .multilineTextAlignment(.center)
            .lineLimit(10)
            .minimumScaleFactor(0.55)
            .allowsTightening(true)
            .frame(width: 243, height: 136)
            .offset(x: 28, y: 248)
    }
}

private extension Card {
    var isAncient: Bool {
        rarity == .ancient
    }

    var displayTitle: String {
        title
    }

    var titleTextColor: UIColor {
        upgradeLevel > 0
            ? StsColors.green
            : StsColors.cream
    }

    var titleOutlineColor: UIColor {
        guard upgradeLevel > 0 else { return rarityTitleOutlineColor }
        return StsColors.cardTitleOutlineSpecial
    }

    var energyCostTextColor: UIColor {
        energyCostReduced
            ? StsColors.green
            : StsColors.cream
    }

    var energyCostOutlineColor: UIColor {
        energyCostReduced
            ? StsColors.energyGreenOutline
            : StsColors.cardTitleOutlineCommon
    }

    private var rarityTitleOutlineColor: UIColor {
        switch rarity {
        case .uncommon:
            return StsColors.cardTitleOutlineUncommon
        case .rare:
            return StsColors.cardTitleOutlineRare
        case .curse:
            return StsColors.cardTitleOutlineCurse
        case .quest:
            return StsColors.cardTitleOutlineQuest
        case .status:
            return StsColors.cardTitleOutlineStatus
        case .event:
            return StsColors.cardTitleOutlineSpecial
        default:
            return StsColors.cardTitleOutlineCommon
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
        appendDescriptionRuns(to: &result)
        appendRulesText(keywordText(for: .afterDescription), style: .keyword, to: &result)

        return result
    }

    private func appendDescriptionRuns(to result: inout AttributedString) {
        if descriptionRuns.isEmpty {
            appendRulesText(description, style: .description, to: &result)
            return
        }

        appendRunSeparatorIfNeeded(to: &result)
        for run in descriptionRuns {
            var segment = AttributedString(run.text)
            segment.font = RulesTextStyle.description.font
            segment.foregroundColor = Color(run.style?.descriptionTextColor ?? StsColors.cream)
            result += segment
        }
    }

    private func appendRulesText(_ text: String, style: RulesTextStyle, to result: inout AttributedString) {
        guard !text.isEmpty else {
            return
        }

        appendRunSeparatorIfNeeded(to: &result)

        var segment = AttributedString(text)
        segment.font = style.font
        segment.foregroundColor = style.color
        result += segment
    }

    private func appendRunSeparatorIfNeeded(to result: inout AttributedString) {
        if !result.characters.isEmpty {
            result += AttributedString("\n")
        }
    }
}

private extension Card.DescriptionRun.Style {
    var descriptionTextColor: UIColor {
        switch self {
        case .gold:
            return StsColors.gold
        case .green:
            return StsColors.green
        case .red:
            return StsColors.red
        case .blue:
            return StsColors.blue
        case .purple:
            return StsColors.purple
        case .unknown:
            return StsColors.cream
        }
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
            return Color(StsColors.cream)
        case .keyword:
            return Color(StsColors.gold)
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
