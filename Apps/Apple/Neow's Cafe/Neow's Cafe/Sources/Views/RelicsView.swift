import SwiftUI

struct RelicsView: View {
    let relics: [Relic]

    @Binding var searchText: String
    @State private var selectedRarity: Relic.Rarity?

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                rarityPicker
                    .padding(16)

                LazyVStack(spacing: 10) {
                    ForEach(filteredRelics, id: \.id) { relic in
                        NavigationLink {
                            RelicDetailView(relic: relic)
                        } label: {
                            RelicRow(relic: relic)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 16)
            }
        }
        .background(NeowSCafeTheme.background)
    }

    private var filteredRelics: [Relic] {
        relics.filter { relic in
            let matchesRarity = selectedRarity.map { relic.rarity == $0 } ?? true
            let matchesSearch = searchText.isEmpty
                || relic.name.localizedCaseInsensitiveContains(searchText)
                || relic.description.localizedCaseInsensitiveContains(searchText)
            return matchesRarity && matchesSearch
        }
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

private struct RelicRow: View {
    let relic: Relic

    var body: some View {
        HStack(alignment: .center, spacing: 14) {
            portrait

            VStack(alignment: .leading, spacing: 5) {
                metadataLine
                Text(relic.descriptionAttributed(defaultColor: NeowSCafeTheme.secondaryText))
                    .font(.neow(.body))
                    .multilineTextAlignment(.leading)
                    .lineLimit(3)
            }

            Spacer(minLength: 0)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(NeowSCafeTheme.surfaceElevated)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(NeowSCafeTheme.separator.opacity(0.4), lineWidth: 1)
        }
    }

    private var metadataLine: some View {
        HStack(spacing: 0) {
            Text(relic.name)
                .font(.neow(.headline, weight: .bold))
                .foregroundStyle(NeowSCafeTheme.text)

            Text("  ·  ")
                .font(.neow(.headline))
                .foregroundStyle(NeowSCafeTheme.separator)

            Group {
                if let pool = primaryPool {
                    Text(pool + "  ")
                }
                Text(relic.rarity.displayName)
            }
            .font(.neow(.body))
            .foregroundStyle(NeowSCafeTheme.secondaryText)
        }
    }

    private var primaryPool: String? {
        let meaningful = relic.pools.first { !["colorless", "event", "shop", "ancient"].contains($0) }
        guard let pool = meaningful else { return nil }
        return pool.capitalized
    }

    private var portrait: some View {
        Group {
            if let url = relic.portraitURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image.resizable().scaledToFit()
                    default:
                        portraitPlaceholder
                    }
                }
            } else {
                portraitPlaceholder
            }
        }
        .frame(width: 60, height: 60)
    }

    private var portraitPlaceholder: some View {
        Image(systemName: "shield.fill")
            .font(.system(size: 32))
            .foregroundStyle(relic.rarity.color.opacity(0.7))
    }
}

#Preview {
    NavigationStack {
        RelicsView(relics: MockRelics.relics, searchText: .constant(""))
            .navigationTitle("Relics")
            .navigationBarTitleDisplayMode(.inline)
    }
}
