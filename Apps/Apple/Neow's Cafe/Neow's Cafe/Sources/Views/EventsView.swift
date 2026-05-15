import SwiftUI

struct EventsView: View {
    let events: [Event]

    @State private var selectedKind: Event.Kind?

    var body: some View {
        List {
            ForEach(filteredEvents, id: \.id) { event in
                NavigationLink {
                    EventDetailView(event: event)
                } label: {
                    EventRow(event: event)
                }
                .listRowBackground(NeowSCafeTheme.surface)
            }
        }
        .listStyle(.plain)
        .background(NeowSCafeTheme.background)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                kindMenu
            }
        }
    }

    private var filteredEvents: [Event] {
        guard let kind = selectedKind else { return events }
        return events.filter { $0.kind == kind }
    }

    private var kindMenu: some View {
        Menu {
            Button("All") { selectedKind = nil }
            Button("Events") { selectedKind = .regular }
            Button("Ancient Events") { selectedKind = .ancient }
        } label: {
            Label(selectedKind.map { kindLabel($0) } ?? "All", systemImage: "line.3.horizontal.decrease.circle")
                .font(.neow(.body))
        }
    }

    private func kindLabel(_ kind: Event.Kind) -> String {
        switch kind {
        case .regular: return "Events"
        case .ancient: return "Ancient"
        }
    }
}

private struct EventRow: View {
    let event: Event

    var body: some View {
        HStack(spacing: 12) {
            portrait

            VStack(alignment: .leading, spacing: 4) {
                Text(event.title)
                    .font(.neow(.body, weight: .bold))
                    .foregroundStyle(NeowSCafeTheme.text)

                Text(kindLabel)
                    .font(.neow(.caption))
                    .foregroundStyle(kindColor)

                Text("\(event.pages.count) page\(event.pages.count == 1 ? "" : "s")")
                    .font(.neow(.caption2))
                    .foregroundStyle(NeowSCafeTheme.secondaryText)
            }

            Spacer()
        }
        .padding(.vertical, 4)
    }

    private var portrait: some View {
        Group {
            if let url = event.portraitURL {
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
                .stroke(kindColor.opacity(0.6), lineWidth: 1.5)
        }
    }

    private var portraitPlaceholder: some View {
        Rectangle()
            .fill(NeowSCafeTheme.surfaceElevated)
            .overlay {
                Image(systemName: "scroll")
                    .font(.system(size: 20))
                    .foregroundStyle(kindColor.opacity(0.5))
            }
    }

    private var kindLabel: String {
        switch event.kind {
        case .regular: return "Event"
        case .ancient: return "Ancient Event"
        }
    }

    private var kindColor: Color {
        switch event.kind {
        case .regular: return Color(StsColors.aqua)
        case .ancient: return Color(StsColors.gold)
        }
    }
}

#Preview {
    NavigationStack {
        EventsView(events: MockEvents.events)
            .navigationTitle("Events")
            .navigationBarTitleDisplayMode(.inline)
    }
}
