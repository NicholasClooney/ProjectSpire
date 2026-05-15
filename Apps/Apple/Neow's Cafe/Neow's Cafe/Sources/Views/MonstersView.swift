import SwiftUI

struct MonstersView: View {
    let monsters: [Monster]

    var body: some View {
        List {
            ForEach(monsters, id: \.id) { monster in
                NavigationLink {
                    MonsterDetailView(monster: monster)
                } label: {
                    MonsterRow(monster: monster)
                }
                .listRowBackground(NeowSCafeTheme.surface)
            }
        }
        .listStyle(.plain)
        .background(NeowSCafeTheme.background)
    }
}

private struct MonsterRow: View {
    let monster: Monster

    var body: some View {
        HStack(spacing: 12) {
            portrait

            VStack(alignment: .leading, spacing: 4) {
                Text(monster.name)
                    .font(.neow(.body, weight: .bold))
                    .foregroundStyle(NeowSCafeTheme.text)

                Text("HP: \(monster.hp.displayRange)")
                    .font(.neow(.caption))
                    .foregroundStyle(Color(StsColors.green))

                Text("\(monster.moves.count) move\(monster.moves.count == 1 ? "" : "s")")
                    .font(.neow(.caption2))
                    .foregroundStyle(NeowSCafeTheme.secondaryText)
            }

            Spacer()
        }
        .padding(.vertical, 4)
    }

    private var portrait: some View {
        Group {
            if let url = monster.portraitURL {
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
        .frame(width: 52, height: 52)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(StsColors.red).opacity(0.5), lineWidth: 1.5)
        }
    }

    private var portraitPlaceholder: some View {
        Rectangle()
            .fill(NeowSCafeTheme.surfaceElevated)
            .overlay {
                Image(systemName: "person.fill")
                    .font(.system(size: 20))
                    .foregroundStyle(Color(StsColors.red).opacity(0.5))
            }
    }
}

#Preview {
    NavigationStack {
        MonstersView(monsters: MockMonsters.monsters)
            .navigationTitle("Monsters")
            .navigationBarTitleDisplayMode(.inline)
    }
}
