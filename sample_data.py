"""Sample records that seed the app.

Everything here is plain Python lists and dictionaries. When a database is
added later, only data_manager.py needs to change: it can load these same
shapes from SQLite instead of from this file.
"""

CATEGORIES = ["Tops", "Bottoms", "Dresses", "Shoes", "Bags", "Accessories", "Outerwear"]
SEASONS = ["Spring", "Summer", "Autumn", "Winter", "All-season"]
OCCASIONS = ["Casual", "College", "Party", "Formal", "Travel"]
STYLES = ["Minimal", "Classic", "Streetwear", "Romantic", "Chic"]

# Colour name -> hex value. Every wardrobe item uses one of these names.
PALETTE = {
    "Ivory": "#F7F4EE",
    "White": "#FFFFFF",
    "Blush": "#E8C9C4",
    "Burgundy": "#6F1D32",
    "Rust": "#B7410E",
    "Butter Yellow": "#F3E3A0",
    "Camel": "#C19A6B",
    "Taupe": "#B9AEA2",
    "Olive": "#6B6B3A",
    "Sage": "#A3B18A",
    "Denim": "#4A6FA5",
    "Cobalt": "#0047AB",
    "Navy": "#1B2A49",
    "Lilac": "#C8A2C8",
    "Charcoal": "#3D3D3D",
    "Ink Black": "#202020",
}


def _item(item_id, name, category, color, season, occasion, price):
    """Build one clothing record. An empty image means 'draw the default
    silhouette'; a filename means 'use assets/clothing/<filename>'."""
    return {
        "id": item_id,
        "name": name,
        "category": category,
        "color": color,
        "season": season,
        "occasion": occasion,
        "price": price,
        "image": "",
    }


CLOTHING = [
    _item(1, "Silk Crepe Blouse", "Tops", "Ivory", "Spring", ["Formal", "College", "Party"], 3200),
    _item(2, "Ribbed Knit Tee", "Tops", "Ink Black", "All-season", ["Casual", "College", "Travel"], 1200),
    _item(3, "Poplin Shirt", "Tops", "Cobalt", "Summer", ["College", "Casual", "Formal"], 2400),
    _item(4, "Cropped Cardigan", "Tops", "Blush", "Autumn", ["Casual", "Party"], 2800),
    _item(5, "Cotton Tank", "Tops", "Butter Yellow", "Summer", ["Casual", "Travel", "Party"], 900),
    _item(6, "Oxford Shirt", "Tops", "White", "All-season", ["College", "Formal", "Casual"], 1800),
    _item(7, "Knit Vest", "Tops", "Lilac", "Spring", ["Casual", "Party"], 1900),
    _item(8, "Wide-Leg Trousers", "Bottoms", "Charcoal", "All-season", ["Formal", "College"], 3400),
    _item(9, "Straight Jeans", "Bottoms", "Denim", "All-season", ["Casual", "College", "Travel"], 2600),
    _item(10, "Pleated Midi Skirt", "Bottoms", "Camel", "Autumn", ["College", "Formal", "Party"], 2900),
    _item(11, "Utility Cargo Pants", "Bottoms", "Ink Black", "All-season", ["Casual", "Travel"], 2200),
    _item(12, "Linen Trousers", "Bottoms", "Olive", "Summer", ["Casual", "Travel"], 2100),
    _item(13, "Corduroy Trousers", "Bottoms", "Rust", "Autumn", ["Casual", "College"], 2700),
    _item(14, "Satin Slip Dress", "Dresses", "Burgundy", "Autumn", ["Party", "Formal"], 5200),
    _item(15, "Wrap Dress", "Dresses", "Sage", "Summer", ["Casual", "College", "Travel"], 3600),
    _item(16, "Column Dress", "Dresses", "Ink Black", "All-season", ["Formal", "Party"], 4800),
    _item(17, "Leather Sneakers", "Shoes", "White", "All-season", ["Casual", "College", "Travel"], 3900),
    _item(18, "Block-Heel Pumps", "Shoes", "Ink Black", "All-season", ["Formal", "Party"], 4500),
    _item(19, "Suede Loafers", "Shoes", "Camel", "Autumn", ["College", "Formal", "Casual"], 4200),
    _item(20, "Leather Ankle Boots", "Shoes", "Burgundy", "Winter", ["Casual", "Party"], 5400),
    _item(21, "Leather Tote", "Bags", "Taupe", "All-season", ["College", "Formal", "Travel"], 6200),
    _item(22, "Mini Shoulder Bag", "Bags", "Ink Black", "All-season", ["Party", "Casual", "Formal"], 3800),
    _item(23, "Silk Scarf", "Accessories", "Butter Yellow", "Spring", ["Casual", "Travel", "College"], 1500),
    _item(24, "Wool Scarf", "Accessories", "Taupe", "Winter", ["Casual", "College", "Travel"], 1700),
    _item(25, "Leather Belt", "Accessories", "Burgundy", "All-season", ["Formal", "College", "Party"], 1900),
    _item(26, "Wool Overcoat", "Outerwear", "Camel", "Winter", ["Formal", "College", "Travel"], 9800),
    _item(27, "Tailored Blazer", "Outerwear", "Navy", "All-season", ["Formal", "College", "Party"], 7400),
    _item(28, "Leather Jacket", "Outerwear", "Ink Black", "Autumn", ["Casual", "Party"], 8800),
]

# Outfits refer to clothing by id, never by copying the item itself.
OUTFITS = [
    {"id": 1, "name": "Monday Lecture", "occasion": "College", "style": "Minimal",
     "item_ids": [6, 8, 17, 21], "favourite": True, "created": "02 Oct 2026, 09:15"},
    {"id": 2, "name": "Dinner at Eight", "occasion": "Party", "style": "Chic",
     "item_ids": [14, 18, 22], "favourite": True, "created": "03 Oct 2026, 19:40"},
    {"id": 3, "name": "Weekend Drift", "occasion": "Casual", "style": "Streetwear",
     "item_ids": [2, 11, 17, 28], "favourite": False, "created": "04 Oct 2026, 11:05"},
    {"id": 4, "name": "Autumn Seminar", "occasion": "Formal", "style": "Classic",
     "item_ids": [1, 10, 19, 26], "favourite": False, "created": "06 Oct 2026, 08:30"},
]

PALETTES = [
    {"id": 1, "name": "Evening in Burgundy", "base": "Burgundy",
     "colours": ["Burgundy", "Blush", "Rust", "Cobalt"], "created": "05 Oct 2026, 21:10"},
]
