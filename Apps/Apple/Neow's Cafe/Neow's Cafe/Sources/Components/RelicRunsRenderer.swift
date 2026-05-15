import SwiftUI

extension Relic {
    func descriptionAttributed(defaultColor: Color) -> AttributedString {
        attributed(runs: descriptionRuns, fallback: description, defaultColor: defaultColor)
    }

    func flavorAttributed(defaultColor: Color) -> AttributedString {
        attributed(runs: flavorRuns, fallback: flavor ?? "", defaultColor: defaultColor)
    }

    private func attributed(runs: [DescriptionRun], fallback: String, defaultColor: Color) -> AttributedString {
        guard !runs.isEmpty else { return AttributedString(fallback) }
        var result = AttributedString()
        for run in runs {
            var segment = AttributedString(run.text)
            segment.foregroundColor = run.style.map { Color(stsColor: $0) } ?? defaultColor
            result += segment
        }
        return result
    }
}

private extension Color {
    init(stsColor: DescriptionRun.Style) {
        switch stsColor {
        case .gold:         self = NeowSCafeTheme.RunColors.gold
        case .green:        self = NeowSCafeTheme.RunColors.green
        case .red:          self = NeowSCafeTheme.RunColors.red
        case .blue:         self = NeowSCafeTheme.RunColors.blue
        case .purple:       self = NeowSCafeTheme.RunColors.purple
        case .unknown:      self = Color(StsColors.cream)
        }
    }
}
