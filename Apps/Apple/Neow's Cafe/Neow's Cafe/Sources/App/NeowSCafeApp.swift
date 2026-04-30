import SwiftUI

@main
struct NeowSCafeApp: App {
    let dependencies: Dependencies = .live

    var body: some Scene {
        WindowGroup {
            ContentView(dependencies: dependencies)
        }
    }
}
