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

    let card = Card(
        id: "BALL_LIGHTNING",
        title: "Ball Lightning",
        description: """
            Deal 7 damage.
            Channel 1 Lightning.
            """,
        energyCost: 1,
        rarity: .common,
        cardType: .attack,
        cardPool: .defect
    )

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

    var portraitBorder: some View {
        Image(card.portraitBorder)
            .resizable()
            .cardAssetColor(card.rarityColor)
            .frame(width: 275, height: 210)
            .offset(x: 12.5, y: 47)
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

    var energyIcon: some View {
        Image(card.energyIcon)
            .resizable()
            .frame(width: 64, height: 64)
            .offset(x: -16, y: -16)
    }

    var energyText: some View {
        BallLightningTextEffect(
            text: "\(card.energyCost)",
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

private extension Image {
    func cardAssetColor(_ approximation: CardAssetColor) -> some View {
        self
            .hueRotation(approximation.hueRotation)
            .saturation(approximation.saturation)
            .brightness(approximation.brightness)
    }
}
