import Foundation

struct Event {
    let id: String
    let title: String
    let kind: Kind
    let pages: [Page]
    let portraitURL: URL?

    enum Kind: String {
        case regular = "event"
        case ancient
    }

    struct Page {
        let id: String
        let description: String
        let options: [Option]
    }

    struct Option {
        let id: String
        let text: String
    }
}
