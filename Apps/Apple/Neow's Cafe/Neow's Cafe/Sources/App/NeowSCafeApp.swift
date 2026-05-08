import SwiftUI

@main
struct NeowSCafeApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView(dependencies: .live())
                .font(.neow(.body))
                .neowCafeAppTheme()
        }
    }
}
