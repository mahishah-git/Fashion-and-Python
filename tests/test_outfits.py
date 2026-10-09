"""Tests for the outfit rules and Style Shuffle. Run: python -m unittest discover -s tests"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import outfit_logic
from colour_logic import colours_compatible
from sample_data import CLOTHING


class StyleShuffleTests(unittest.TestCase):
    def test_empty_wardrobe_returns_empty_slots_and_a_note(self):
        result = outfit_logic.style_shuffle([], "Casual", "Minimal", random.Random(1))
        self.assertTrue(all(piece is None for piece in result["pieces"].values()))
        self.assertTrue(result["notes"])

    def test_missing_categories_do_not_crash(self):
        only_tops = [i for i in CLOTHING if i["category"] == "Tops"]
        result = outfit_logic.style_shuffle(only_tops, "College", "Classic", random.Random(2))
        self.assertIsNotNone(result["pieces"]["top"])
        self.assertIsNone(result["pieces"]["shoes"])
        self.assertTrue(any("no footwear" in note.lower() for note in result["notes"]))

    def test_pieces_come_from_the_right_categories(self):
        for seed in range(30):
            pieces = outfit_logic.style_shuffle(CLOTHING, "Party", "Chic", random.Random(seed))["pieces"]
            for slot, _label, categories in outfit_logic.SLOTS:
                if pieces[slot] is not None:
                    self.assertIn(pieces[slot]["category"], categories)

    def test_full_wardrobe_colours_are_compatible(self):
        # The sample wardrobe has plenty of neutrals, so no clash is ever needed.
        for seed in range(50):
            chosen = [p for p in outfit_logic.style_shuffle(
                CLOTHING, "College", "Minimal", random.Random(seed))["pieces"].values() if p]
            for first in chosen:
                for second in chosen:
                    self.assertTrue(colours_compatible(first["color"], second["color"]))

    def test_same_seed_gives_same_result(self):
        first = outfit_logic.style_shuffle(CLOTHING, "Casual", "Streetwear", random.Random(7))
        second = outfit_logic.style_shuffle(CLOTHING, "Casual", "Streetwear", random.Random(7))
        self.assertEqual({k: v and v["id"] for k, v in first["pieces"].items()},
                         {k: v and v["id"] for k, v in second["pieces"].items()})

    def test_narrow_by_occasion_falls_back_to_whole_pool(self):
        pool = [{"occasion": ["Casual"], "color": "Ivory"}]
        self.assertEqual(outfit_logic.narrow_by_occasion(pool, "Formal"), pool)


class OutfitValidationTests(unittest.TestCase):
    def test_valid_outfit(self):
        self.assertEqual(outfit_logic.validate_outfit("Look", "Casual", "Minimal", [1, 2]), [])

    def test_rejects_blank_name_bad_choices_and_single_piece(self):
        errors = outfit_logic.validate_outfit("  ", "Picnic", "Goth", [1, 1])
        self.assertEqual(len(errors), 4)

    def test_make_outfit_removes_duplicate_ids(self):
        outfit = outfit_logic.make_outfit(5, " Look ", "Casual", "Minimal", [3, 3, 4])
        self.assertEqual(outfit["item_ids"], [3, 4])
        self.assertEqual(outfit["name"], "Look")

    def test_resolve_outfit_counts_missing_items(self):
        outfit = {"item_ids": [1, 999]}
        pieces, missing = outfit_logic.resolve_outfit(outfit, {1: {"id": 1}})
        self.assertEqual((len(pieces), missing), (1, 1))


if __name__ == "__main__":
    unittest.main()
