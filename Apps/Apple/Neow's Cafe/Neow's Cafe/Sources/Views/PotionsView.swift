import SwiftUI

struct PotionsView: View {
    let potions: [Potion]

    @State private var selectedRarity: Potion.Rarity?

    private let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16),
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                rarityPicker

                LazyVGrid(columns: columns, spacing: 16) {
                    ForEach(filteredPotions, id: \.id) { potion in
                        PotionGridItem(potion: potion)
                    }
                }
            }
            .padding(16)
        }
        .background(NeowSCafeTheme.background)
    }

    private var filteredPotions: [Potion] {
        guard let rarity = selectedRarity else { return potions }
        return potions.filter { $0.rarity == rarity }
    }

    private var rarityPicker: some View {
        ScrollView(.horizontal) {
            HStack(spacing: 12) {
                EnumPicker("Rarity", selection: $selectedRarity)

                Button {
                    selectedRarity = nil
                } label: {
                    Image(systemName: "arrow.counterclockwise")
                }
                .disabled(selectedRarity == nil)
                .buttonStyle(.bordered)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(NeowSCafeTheme.surfaceElevated)
            }
            .overlay {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .stroke(NeowSCafeTheme.separator.opacity(0.55), lineWidth: 1)
            }
        }
        .scrollIndicators(.hidden)
    }
}

private struct PotionGridItem: View {
    let potion: Potion

    var body: some View {
        VStack(spacing: 8) {
            portraitArea

            Text(potion.name)
                .font(.neow(.caption, weight: .bold))
                .foregroundStyle(NeowSCafeTheme.text)
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .minimumScaleFactor(0.8)

            Text(potion.usage.displayName)
                .font(.neow(.caption2))
                .foregroundStyle(NeowSCafeTheme.secondaryText)
        }
    }

    private var portraitArea: some View {
        Group {
            if let url = potion.portraitURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image.resizable().scaledToFill()
                    default:
                        portraitPlaceholder
                    }
                }
            } else {
                portraitPlaceholder
            }
        }
        .frame(maxWidth: .infinity)
        .aspectRatio(1, contentMode: .fit)
        .clipShape(Circle())
        .overlay {
            Circle()
                .stroke(potion.rarity.color, lineWidth: 2)
        }
    }

    private var portraitPlaceholder: some View {
        Circle()
            .fill(NeowSCafeTheme.surface)
            .overlay {
                Image(systemName: "flask")
                    .font(.system(size: 24))
                    .foregroundStyle(potion.rarity.color.opacity(0.6))
            }
    }
}

#Preview {
    NavigationStack {
        PotionsView(potions: MockPotions.potions)
            .navigationTitle("Potions")
            .navigationBarTitleDisplayMode(.inline)
    }
}
