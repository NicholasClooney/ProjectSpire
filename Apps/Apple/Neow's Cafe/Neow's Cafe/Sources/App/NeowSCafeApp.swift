import SwiftUI

@main
struct NeowSCafeApp: App {
    init() {
        NeowSCafeTypography.registerFonts()
    }

    var body: some Scene {
        WindowGroup {
            ContentView(dependencies: .live())
                .font(.neow(.body))
        }
    }
}
