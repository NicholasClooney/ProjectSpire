import SwiftUI

struct EventDetailView: View {
    let event: Event

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                if let url = event.portraitURL {
                    AsyncImage(url: url) { phase in
                        switch phase {
                        case .success(let image):
                            image
                                .resizable()
                                .scaledToFit()
                                .frame(maxWidth: .infinity)
                        default:
                            EmptyView()
                        }
                    }
                }

                VStack(alignment: .leading, spacing: 24) {
                    ForEach(event.pages, id: \.id) { page in
                        PageSection(page: page)
                    }
                }
                .padding(20)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(NeowSCafeTheme.background)
        .navigationTitle(event.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct PageSection: View {
    let page: Event.Page

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(page.id.capitalized.replacingOccurrences(of: "_", with: " "))
                .font(.neow(.caption, weight: .bold))
                .foregroundStyle(NeowSCafeTheme.secondaryText)

            if !page.description.isEmpty {
                Text(page.description)
                    .font(.neow(.body))
                    .foregroundStyle(NeowSCafeTheme.text)
            }

            if !page.options.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(page.options, id: \.id) { option in
                        OptionRow(option: option)
                    }
                }
            }
        }
        .padding(16)
        .background {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(NeowSCafeTheme.surface)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(NeowSCafeTheme.separator.opacity(0.4), lineWidth: 1)
        }
    }
}

private struct OptionRow: View {
    let option: Event.Option

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "chevron.right")
                .font(.neow(.caption))
                .foregroundStyle(Color(StsColors.gold))
                .padding(.top, 2)

            Text(option.text)
                .font(.neow(.body))
                .foregroundStyle(NeowSCafeTheme.text)
        }
    }
}

#Preview("Big Fish") {
    NavigationStack {
        EventDetailView(event: MockEvents.events[0])
    }
}

#Preview("Ancient") {
    NavigationStack {
        EventDetailView(event: MockEvents.events.last!)
    }
}
