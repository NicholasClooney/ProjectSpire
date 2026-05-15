import SwiftUI

struct RelicDetailView: View {
    let relic: Relic

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                nameSection
                    .padding(.top, 32)

                portraitSection
                    .padding(.top, 24)

                descriptionSection
                    .padding(.top, 24)
                    .padding(.horizontal, 24)

                if relic.flavor != nil {
                    divider
                        .padding(.top, 20)
                        .padding(.horizontal, 24)

                    flavorSection
                        .padding(.top, 16)
                        .padding(.horizontal, 24)
                }

                Spacer(minLength: 40)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(stoneBackground)
        .navigationTitle(relic.name)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var stoneBackground: some View {
        Color(red: 0.10, green: 0.08, blue: 0.12)
            .ignoresSafeArea()
    }

    private var nameSection: some View {
        VStack(spacing: 6) {
            Text(relic.name)
                .font(.neow(.title, weight: .bold))
                .foregroundStyle(Color(StsColors.gold))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)

            Text(relic.rarity.relicLabel)
                .font(.neow(.subheadline))
                .foregroundStyle(relic.rarity.color)
        }
    }

    private var portraitSection: some View {
        RelicPortraitView(url: relic.portraitURL, rarityColor: relic.rarity.color)
            .frame(width: 200, height: 200)
            .shadow(color: relic.rarity.color.opacity(0.5), radius: 12)
    }

    private var descriptionSection: some View {
        Text(relic.descriptionAttributed(defaultColor: Color(StsColors.cream)))
            .font(.neow(.body))
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity)
    }

    private var divider: some View {
        Rectangle()
            .fill(Color(StsColors.halfTransparentCream))
            .frame(height: 1)
    }

    private var flavorSection: some View {
        Text(relic.flavorAttributed(defaultColor: Color(StsColors.red)))
            .font(.neow(.body))
            .italic()
            .multilineTextAlignment(.center)
            .frame(maxWidth: .infinity)
    }
}

private struct RelicPortraitView: View {
    let url: URL?
    let rarityColor: Color

    private let bracketLength: CGFloat = 22
    private let bracketThickness: CGFloat = 3

    var body: some View {
        portraitImage
            .clipShape(RoundedRectangle(cornerRadius: 4))
            .overlay {
                RoundedRectangle(cornerRadius: 4)
                    .stroke(rarityColor.opacity(0.5), lineWidth: 1)
            }
            .overlay {
                GeometryReader { geo in
                    cornerBrackets(in: geo.size)
                }
            }
    }

    @ViewBuilder
    private var portraitImage: some View {
        if let url {
            AsyncImage(url: url) { phase in
                switch phase {
                case .success(let image):
                    image.resizable().scaledToFill()
                default:
                    placeholder
                }
            }
        } else {
            placeholder
        }
    }

    private var placeholder: some View {
        Rectangle()
            .fill(Color(red: 0.15, green: 0.13, blue: 0.18))
            .overlay {
                Image(systemName: "photo")
                    .font(.system(size: 40))
                    .foregroundStyle(rarityColor.opacity(0.4))
            }
    }

    private func cornerBrackets(in size: CGSize) -> some View {
        ZStack {
            bracketPath(for: .topLeft, in: size)
            bracketPath(for: .topRight, in: size)
            bracketPath(for: .bottomLeft, in: size)
            bracketPath(for: .bottomRight, in: size)
        }
    }

    private enum Corner { case topLeft, topRight, bottomLeft, bottomRight }

    private func bracketPath(for corner: Corner, in size: CGSize) -> some View {
        let l = bracketLength
        let w = size.width
        let h = size.height

        let path: Path = {
            var p = Path()
            switch corner {
            case .topLeft:
                p.move(to: CGPoint(x: 0, y: l))
                p.addLine(to: CGPoint(x: 0, y: 0))
                p.addLine(to: CGPoint(x: l, y: 0))
            case .topRight:
                p.move(to: CGPoint(x: w - l, y: 0))
                p.addLine(to: CGPoint(x: w, y: 0))
                p.addLine(to: CGPoint(x: w, y: l))
            case .bottomLeft:
                p.move(to: CGPoint(x: 0, y: h - l))
                p.addLine(to: CGPoint(x: 0, y: h))
                p.addLine(to: CGPoint(x: l, y: h))
            case .bottomRight:
                p.move(to: CGPoint(x: w - l, y: h))
                p.addLine(to: CGPoint(x: w, y: h))
                p.addLine(to: CGPoint(x: w, y: h - l))
            }
            return p
        }()

        return path.stroke(rarityColor, lineWidth: bracketThickness)
    }
}

private extension Relic.Rarity {
    var relicLabel: String {
        switch self {
        case .starter:  return "Starter Relic"
        case .common:   return "Common Relic"
        case .uncommon: return "Uncommon Relic"
        case .rare:     return "Rare Relic"
        case .shop:     return "Shop Relic"
        case .event:    return "Event Relic"
        case .ancient:  return "Ancient Relic"
        case .none:     return "Relic"
        }
    }
}

#Preview("Starter (Burning Blood)") {
    NavigationStack {
        RelicDetailView(relic: MockRelics.relics[0])
    }
}

#Preview("Ancient (Astrolabe)") {
    NavigationStack {
        RelicDetailView(relic: MockRelics.relics.last!)
    }
}

#Preview("No Flavor") {
    NavigationStack {
        RelicDetailView(relic: MockRelics.relics[4])
    }
}
