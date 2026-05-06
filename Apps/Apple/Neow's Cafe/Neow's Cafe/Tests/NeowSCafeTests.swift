import Testing
import Foundation
@testable import Neow_s_Cafe

struct NeowSCafeTests {

    @Test func decodesCatalogCards() throws {
        let data = """
        {
          "schemaVersion": "neows-cafe-card-catalog.v1",
          "gameVersion": "v0.103.2",
          "generatedAt": "2026-05-06T00:00:00Z",
          "cards": [
            {
              "id": "ANGER",
              "slug": "anger",
              "title": "Anger",
              "description": "Deal 6 damage.",
              "energyCost": { "kind": "int", "value": 0 },
              "type": "attack",
              "rarity": "common",
              "pool": "ironclad",
              "portraitPath": "images/card_portraits/ironclad/anger.webp",
              "detailPath": "cards/anger.json"
            },
            {
              "id": "SKEWER",
              "slug": "skewer",
              "title": "Skewer",
              "description": "Deal 7 damage X times.",
              "energyCost": { "kind": "x", "value": 0 },
              "type": "attack",
              "rarity": "uncommon",
              "pool": "silent",
              "portraitPath": null,
              "detailPath": "cards/skewer.json"
            }
          ]
        }
        """.data(using: .utf8)!

        let cards = try CardCatalogDecoder.decodeCards(
            from: data,
            baseURL: URL(string: "http://127.0.0.1:8765/v0.103.2/")!
        )

        #expect(cards.count == 2)
        #expect(cards[0].id == "ANGER")
        #expect(cards[0].energyCost == .int(0))
        #expect(cards[0].cardPool == .ironclad)
        #expect(cards[0].portraitURL?.absoluteString == "http://127.0.0.1:8765/v0.103.2/images/card_portraits/ironclad/anger.webp")

        #expect(cards[1].id == "SKEWER")
        #expect(cards[1].energyCost == .x)
        #expect(cards[1].portraitURL == nil)
    }

}
