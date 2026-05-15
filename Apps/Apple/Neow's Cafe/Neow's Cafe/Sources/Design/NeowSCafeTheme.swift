import SwiftUI
import UIKit

enum NeowSCafeTheme {
    static let background = Color.dynamic(
        light: UIColor(red: 0.933, green: 0.878, blue: 0.729, alpha: 1),
        dark: UIColor(red: 0.075, green: 0.063, blue: 0.071, alpha: 1)
    )

    static let surface = Color.dynamic(
        light: UIColor(red: 0.984, green: 0.945, blue: 0.831, alpha: 1),
        dark: UIColor(red: 0.145, green: 0.118, blue: 0.122, alpha: 1)
    )

    static let surfaceElevated = Color.dynamic(
        light: UIColor(red: 1.000, green: 0.969, blue: 0.878, alpha: 1),
        dark: UIColor(red: 0.208, green: 0.165, blue: 0.153, alpha: 1)
    )

    static let text = Color.dynamic(
        light: UIColor(red: 0.154, green: 0.101, blue: 0.071, alpha: 1),
        dark: UIColor(red: 0.965, green: 0.898, blue: 0.765, alpha: 1)
    )

    static let secondaryText = Color.dynamic(
        light: UIColor(red: 0.392, green: 0.302, blue: 0.216, alpha: 1),
        dark: UIColor(red: 0.737, green: 0.639, blue: 0.510, alpha: 1)
    )

    static let accent = Color.dynamic(
        light: UIColor(red: 0.565, green: 0.118, blue: 0.071, alpha: 1),
        dark: UIColor(red: 0.961, green: 0.553, blue: 0.204, alpha: 1)
    )

    static let separator = Color.dynamic(
        light: UIColor(red: 0.675, green: 0.549, blue: 0.369, alpha: 1),
        dark: UIColor(red: 0.424, green: 0.333, blue: 0.243, alpha: 1)
    )

    enum RunColors {
        // Light: darkened for legibility on cream. Dark: StsColors.
        static let gold   = Color.dynamic(
            light: UIColor(red: 0.545, green: 0.384, blue: 0.000, alpha: 1),
            dark:  StsColors.gold
        )
        static let blue   = Color.dynamic(
            light: UIColor(red: 0.102, green: 0.420, blue: 0.624, alpha: 1),
            dark:  StsColors.blue
        )
        static let green  = Color.dynamic(
            light: UIColor(red: 0.176, green: 0.478, blue: 0.122, alpha: 1),
            dark:  StsColors.green
        )
        static let red    = Color.dynamic(
            light: UIColor(red: 0.800, green: 0.133, blue: 0.133, alpha: 1),
            dark:  StsColors.red
        )
        static let purple = Color.dynamic(
            light: UIColor(red: 0.545, green: 0.243, blue: 0.659, alpha: 1),
            dark:  StsColors.purple
        )
    }

}

extension View {
    func neowCafeAppTheme() -> some View {
        self
            .background(NeowSCafeTheme.background)
            .foregroundStyle(NeowSCafeTheme.text)
            .tint(NeowSCafeTheme.accent)
    }
}

private extension Color {
    static func dynamic(light: UIColor, dark: UIColor) -> Color {
        Color(
            UIColor { traits in
                traits.userInterfaceStyle == .dark ? dark : light
            }
        )
    }
}
