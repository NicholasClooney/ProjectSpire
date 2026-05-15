import Foundation

struct DescriptionRun: Equatable {
    let text: String
    let sourceVar: String?
    let style: Style?

    init(_ text: String, sourceVar: String? = nil, style: Style? = nil) {
        self.text = text
        self.sourceVar = sourceVar
        self.style = style
    }

    enum Style: Equatable, Decodable {
        case gold
        case green
        case red
        case blue
        case purple
        case unknown(String)

        init(from decoder: Decoder) throws {
            let container = try decoder.singleValueContainer()
            let rawValue = try container.decode(String.self)
            switch rawValue {
            case "gold":   self = .gold
            case "green":  self = .green
            case "red":    self = .red
            case "blue":   self = .blue
            case "purple": self = .purple
            default:
                assertionFailure("Unknown description run style: \(rawValue)")
                self = .unknown(rawValue)
            }
        }
    }
}
