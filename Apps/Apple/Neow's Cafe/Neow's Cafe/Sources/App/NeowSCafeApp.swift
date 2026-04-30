import SwiftUI

@main
struct NeowSCafeApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView(cards: MockCards.cards)
        }
    }
}
