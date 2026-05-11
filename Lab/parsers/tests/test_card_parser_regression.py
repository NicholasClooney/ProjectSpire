"""Regression tests: parse representative cards and compare against committed JSON.

Requires decompiled source and localization files on disk. Skipped automatically
if decompiled source is absent. Run with:

    python3 -m unittest tests.test_card_parser_regression
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import card_parser
from common import class_name_to_id, to_jsonable

LAB_DIR = Path(__file__).resolve().parent.parent.parent
VERSION = "v0.103.2"
CARDS_DIR = LAB_DIR / "decompiled" / VERSION / "MegaCrit.Sts2.Core.Models.Cards"
DATA_DIR = LAB_DIR / "data" / VERSION / "cards"
LOC_DIR = LAB_DIR / "resources" / "localization" / "eng"

DECOMPILED_PRESENT = CARDS_DIR.exists()

# One card per meaningful parser path:
#   BallLightning  — simple attack, one var, two tips, upgrade changes value
#   Abrasive       — multiple vars, keyword, beta portrait
#   Cascade        — IfUpgraded in localization description
#   BladeDance     — X-cost card
#   Shiv           — creates card, card tag
REGRESSION_CARDS = ["BallLightning", "Abrasive", "Cascade", "BladeDance", "Shiv"]


@unittest.skipUnless(DECOMPILED_PRESENT, "Decompiled source not present")
class TestCardParserRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.localization = card_parser.load_localization(LOC_DIR / "cards.json")
        cls.keyword_localization = card_parser.load_localization(LOC_DIR / "card_keywords.json")
        cls.card_pools = card_parser.load_card_pool_map(VERSION)

    def _parse(self, card_name):
        path = CARDS_DIR / f"{card_name}.cs"
        card = card_parser.parse_card(path, self.localization, self.keyword_localization, self.card_pools)
        return json.loads(json.dumps(to_jsonable(card), indent=2, sort_keys=False))

    def _committed(self, card_name):
        path = DATA_DIR / f"{class_name_to_id(card_name).lower()}.json"
        with path.open() as f:
            return json.load(f)

    def _assert_matches(self, card_name):
        self.assertEqual(
            self._parse(card_name),
            self._committed(card_name),
            msg=f"{card_name} output differs from committed JSON — run the card parser over all cards and check git diff Lab/data/",
        )

    def test_ball_lightning(self):
        self._assert_matches("BallLightning")

    def test_abrasive(self):
        self._assert_matches("Abrasive")

    def test_cascade(self):
        self._assert_matches("Cascade")

    def test_blade_dance(self):
        self._assert_matches("BladeDance")

    def test_shiv(self):
        self._assert_matches("Shiv")


if __name__ == "__main__":
    unittest.main()
