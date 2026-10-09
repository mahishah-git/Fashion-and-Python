"""Tests for filtering, sorting and validating wardrobe records."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import data_manager as dm
from sample_data import CLOTHING

GOOD = {"name": "Test Shirt", "category": "Tops", "color": "Ivory", "season": "Summer",
        "occasion": ["Casual"], "price": 999}


class DataTests(unittest.TestCase):
    def test_valid_item_has_no_errors(self):
        self.assertEqual(dm.validate_item(GOOD), [])

    def test_invalid_item_reports_each_problem(self):
        bad = {"name": "", "category": "Hats", "color": "Pink", "season": "Monsoon",
               "occasion": [], "price": "abc"}
        self.assertEqual(len(dm.validate_item(bad)), 6)

    def test_negative_price_is_rejected(self):
        self.assertTrue(dm.validate_item({**GOOD, "price": -5}))

    def test_search_category_and_colour_filters(self):
        self.assertTrue(all(i["category"] == "Shoes" for i in dm.filter_items(CLOTHING, category="Shoes")))
        self.assertTrue(all(i["color"] == "Burgundy" for i in dm.filter_items(CLOTHING, colour="Burgundy")))
        self.assertTrue(dm.filter_items(CLOTHING, search="loafers"))
        self.assertEqual(dm.filter_items(CLOTHING, search="zzzz"), [])

    def test_sorting(self):
        prices = [i["price"] for i in dm.sort_items(CLOTHING, "Price: low to high")]
        self.assertEqual(prices, sorted(prices))
        names = [i["name"].lower() for i in dm.sort_items(CLOTHING, "Name A to Z")]
        self.assertEqual(names, sorted(names))

    def test_every_sample_item_is_valid(self):
        for item in CLOTHING:
            self.assertEqual(dm.validate_item(item), [], item["name"])

    def test_parse_backup_rejects_bad_files(self):
        self.assertTrue(dm.parse_backup("not json")[1])
        self.assertTrue(dm.parse_backup('{"hello": 1}')[1])
        self.assertEqual(dm.parse_backup('{"wardrobe": []}')[1], "")


if __name__ == "__main__":
    unittest.main()
