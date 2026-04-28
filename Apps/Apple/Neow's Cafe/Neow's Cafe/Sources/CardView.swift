//
//  CardView.swift
//  Neow's Cafe
//
//  Created by Nicholas Clooney on 28/04/2026.
//

import SwiftUI
import UIKit

struct CardView: View {
    var body: some View {
        ZStack(alignment: .topLeading) {
            portrait
            frame
            portraitBorder
            titleBanner
            titleText
            typePlaque
            energyIcon
            description
        }
        .frame(width: 300, height: 422, alignment: .topLeading)
    }

    var titleBanner: some View {
        Image(ImageResource.cardBanner)
            .resizable()
            .frame(width: 327, height: 83)
            .offset(x: -13, y: 14)
    }

    var portrait: some View {
        Image(ImageResource.ballLightning)
            .resizable()
            .frame(width: 250, height: 190)
            .offset(x: 25, y: 43)
    }

    var frame: some View {
        Image(ImageResource.cardFrameAttackS)
            .resizable()
            .frame(width: 300, height: 422)
            .offset(x: 0, y: 0)
    }

    var portraitBorder: some View {
        Image(ImageResource.cardPortraitBorderAttackS)
            .resizable()
            .frame(width: 275, height: 210)
            .offset(x: 12.5, y: 47)
    }

    var title: some View {
        OutlinedText(
            text: "Ball Lightning",
            font: NeowSCafeFontFamily.Kreon.regular.font(size: 32),
            fillColor: UIColor(red: 1, green: 0.965, blue: 0.886, alpha: 1),
            strokeColor: UIColor(red: 0.302, green: 0.294, blue: 0.251, alpha: 1),
            strokeWidth: 4,
            minimumScaleFactor: 0.7
        )
        .frame(width: 250, height: 54)
        .offset(x: 25, y: 7)
    }

    var titleText: some View {
        Text("Ball Lightning")
            .font(NeowSCafeFontFamily.Kreon.regular.swiftUIFont(size: 26))
            .foregroundStyle(Color(red: 1, green: 0.965, blue: 0.886))
            .shadow(color: Color.black.opacity(0.55), radius: 0, x: 2, y: 2)
            .minimumScaleFactor(0.7)
            .lineLimit(1)
            .frame(width: 210, height: 54)
            .offset(x: 45, y: 7)
    }

    var typePlaque: some View {
        ZStack {
            Image(ImageResource.cardPortraitBorderPlaqueS)
                .resizable()

            Text("Attack")
                .font(NeowSCafeFontFamily.Kreon.bold.swiftUIFont(size: 16))
                .foregroundStyle(Color.black.opacity(0.75))
                .minimumScaleFactor(0.7)
                .lineLimit(1)
        }
        .frame(width: 61, height: 37)
        .offset(x: 119.5, y: 212)
    }

    var energyIcon: some View {
        ZStack {
            Image(ImageResource.energyDefect)
                .resizable()

            energyText
        }
        .frame(width: 64, height: 64)
        .offset(x: -16, y: -16)
    }

    var energyOutlinedText: some View {
            OutlinedText(
                text: "1",
                font: NeowSCafeFontFamily.Kreon.bold.font(size: 32),
                fillColor: UIColor(red: 1, green: 0.965, blue: 0.886, alpha: 1),
                strokeColor: UIColor(red: 0.1225, green: 0.35, blue: 0.137667, alpha: 1),
                strokeWidth: 4,
                minimumScaleFactor: 0.7
            )
            .frame(width: 46, height: 56)
            .offset(x: 0, y: 2)
    }

    var energyText: some View {
        Text("1")
            .font(NeowSCafeFontFamily.Kreon.bold.swiftUIFont(size: 32))
            .foregroundStyle(Color(red: 1, green: 0.965, blue: 0.886))
            .shadow(color: Color.black.opacity(0.45), radius: 0, x: 2, y: 2)
            .minimumScaleFactor(0.7)
            .lineLimit(1)
            .frame(width: 46, height: 56)
            .offset(x: 0, y: 2)
    }

    var description: some View {
        VStack(spacing: 4) {
            Text("Deal 7 damage.")
            Text("Channel 1 Lightning.")
                .foregroundStyle(Color(red: 0.96, green: 0.78, blue: 0.28))
        }
        .font(NeowSCafeFontFamily.Kreon.regular.swiftUIFont(size: 21))
        .foregroundStyle(Color(red: 1, green: 0.965, blue: 0.886))
        .shadow(color: Color.black.opacity(0.55), radius: 0, x: 2, y: 2)
        .multilineTextAlignment(.center)
        .minimumScaleFactor(0.6)
        .frame(width: 243, height: 136)
        .offset(x: 28, y: 248)
    }
}

struct OutlinedText: UIViewRepresentable {
    let text: String
    let font: UIFont
    let fillColor: UIColor
    let strokeColor: UIColor
    let strokeWidth: CGFloat
    let minimumScaleFactor: CGFloat

    func makeUIView(context: Context) -> UILabel {
        let label = UILabel()
        label.textAlignment = .center
        label.adjustsFontSizeToFitWidth = true
        label.minimumScaleFactor = minimumScaleFactor
        label.numberOfLines = 1
        label.backgroundColor = .clear
        return label
    }

    func updateUIView(_ label: UILabel, context: Context) {
        label.minimumScaleFactor = minimumScaleFactor
        label.attributedText = NSAttributedString(
            string: text,
            attributes: [
                .font: font,
                .foregroundColor: fillColor,
                .strokeColor: strokeColor,
                .strokeWidth: -strokeWidth,
            ]
        )
    }
}
