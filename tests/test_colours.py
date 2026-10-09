"""Tests for the colour rules."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import colour_logic as cl


class ColourTests(unittest.TestCase):
    def test_neutrals_go_with_everything(self):
        self.assertTrue(cl.colours_compatible("Ink Black", "Burgundy"))
        self.assertTrue(cl.colours_compatible("Cobalt", "Ivory"))

    def test_analogous_and_complementary_pairs_are_compatible(self):
        self.assertTrue(cl.colours_compatible("Burgundy", "Blush"))
        self.assertTrue(cl.colours_compatible("Burgundy", "Cobalt"))

    def test_clashing_pair_is_rejected(self):
        self.assertFalse(cl.colours_compatible("Burgundy", "Sage"))

    def test_palette_for_a_colour_has_suggestions(self):
        palette = cl.build_palette("Burgundy")
        self.assertIn("Blush", palette["analogous"])
        self.assertIn("Cobalt", palette["complementary"])

    def test_neutral_base_gets_accents_instead(self):
        palette = cl.build_palette("Ink Black")
        self.assertTrue(palette["neutral"])
        self.assertTrue(palette["accents"])
        self.assertEqual(palette["analogous"], [])

    def test_unknown_base_falls_back(self):
        self.assertEqual(cl.build_palette("Chartreuse")["base"], "Burgundy")

    def test_bad_hex_falls_back(self):
        self.assertEqual(cl.hex_to_rgb("nonsense"), cl.hex_to_rgb(cl.DEFAULT_HEX))

    def test_items_matching_uses_colour_names(self):
        items = [{"color": "Blush"}, {"color": "Sage"}, {"color": "Ink Black"}]
        self.assertEqual(len(cl.items_matching(items, ["Blush"])), 1)
        self.assertEqual(len(cl.items_matching(items, ["Blush"], include_neutrals=True)), 2)


if __name__ == "__main__":
    unittest.main()
