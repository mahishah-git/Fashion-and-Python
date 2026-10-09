"""Outfit rules and the Style Shuffle algorithm (no Streamlit code in here).

Style Shuffle is a plain rule-based picker, not artificial intelligence:
  1. Choose an anchor: a dress (for dressy occasions) or a top + bottom.
  2. For every slot, start with the wardrobe items of that category.
  3. Prefer items tagged for the chosen occasion.
  4. Keep only items whose colour is compatible with the pieces already chosen.
  5. Prefer colours that suit the chosen style, then pick one at random.
If a rule leaves nothing to choose from, it is relaxed and a note says so.
"""
import random
from datetime import datetime

from colour_logic import colours_compatible
from sample_data import OCCASIONS, STYLES

# (slot key, label shown to the user, categories allowed in the slot)
SLOTS = [
    ("top", "Top", ("Tops",)),
    ("bottom", "Bottom", ("Bottoms",)),
    ("shoes", "Footwear", ("Shoes",)),
    ("accessory", "Accessory or bag", ("Accessories", "Bags")),
    ("layer", "Dress or outerwear", ("Dresses", "Outerwear")),
]

DRESSY_OCCASIONS = {"Party", "Formal"}

STYLE_COLOURS = {
    "Minimal": {"Ivory", "White", "Ink Black", "Taupe", "Charcoal", "Camel"},
    "Classic": {"Navy", "Camel", "White", "Ivory", "Burgundy", "Denim"},
    "Streetwear": {"Ink Black", "Charcoal", "Cobalt", "Olive", "White", "Denim"},
    "Romantic": {"Blush", "Burgundy", "Lilac", "Ivory", "Sage"},
    "Chic": {"Ink Black", "Burgundy", "Ivory", "Camel", "Butter Yellow"},
}


def items_in_categories(items, categories):
    return [item for item in items if item.get("category") in categories]


def narrow_by_occasion(pool, occasion):
    """Keep items tagged for the occasion; if none are, keep the whole pool."""
    matches = [item for item in pool if occasion in item.get("occasion", [])]
    return matches if matches else pool


def narrow_by_colour(pool, chosen):
    """Keep items whose colour works with every piece chosen so far."""
    return [item for item in pool
            if all(colours_compatible(item["color"], piece["color"]) for piece in chosen)]


def prefer_style(pool, style):
    """Prefer the style's signature colours when the pool contains any."""
    wanted = STYLE_COLOURS.get(style, set())
    preferred = [item for item in pool if item["color"] in wanted]
    return preferred if preferred else pool


def pick_piece(items, categories, occasion, style, chosen, rng):
    """Pick one item for a slot. Returns (item or None, colour_rule_relaxed)."""
    pool = items_in_categories(items, categories)
    if not pool:
        return None, False
    pool = narrow_by_occasion(pool, occasion)
    compatible = narrow_by_colour(pool, chosen)
    relaxed = not compatible
    if relaxed:
        compatible = pool
    return rng.choice(prefer_style(compatible, style)), relaxed


def style_shuffle(items, occasion, style, rng=None):
    """Build a look. Returns {"pieces": {slot: item or None}, "notes": [str]}.

    Pass a random.Random(seed) as rng to get repeatable results in tests.
    """
    rng = rng or random
    pieces = {key: None for key, _label, _cats in SLOTS}
    notes = []

    if not items:
        notes.append("The wardrobe is empty. Add a few pieces first, then shuffle again.")
        return {"pieces": pieces, "notes": notes}

    has_dresses = bool(items_in_categories(items, ("Dresses",)))
    has_separates = (bool(items_in_categories(items, ("Tops",)))
                     and bool(items_in_categories(items, ("Bottoms",))))
    dressy = occasion in DRESSY_OCCASIONS and rng.random() < 0.5
    use_dress = has_dresses and (dressy or not has_separates)

    # Plan: which slots to fill, in order, and which categories each may use.
    if use_dress:
        plan = [("layer", "dress", ("Dresses",))]
    else:
        plan = [("top", "top", ("Tops",)), ("bottom", "bottom", ("Bottoms",))]
    plan.append(("shoes", "footwear", ("Shoes",)))
    plan.append(("accessory", "accessory", ("Accessories", "Bags")))
    if not use_dress and rng.random() < 0.5:
        plan.append(("layer", "outerwear", ("Outerwear",)))

    chosen = []
    for slot, label, categories in plan:
        piece, relaxed = pick_piece(items, categories, occasion, style, chosen, rng)
        if piece is None:
            notes.append(f"There are no {label} pieces in the wardrobe, so that slot stays empty.")
            continue
        pieces[slot] = piece
        chosen.append(piece)
        if relaxed:
            notes.append(f"No {label} matched the colour rules, so the {piece['name']} was the closest option.")

    if chosen:
        notes.insert(0, f"Built around the {chosen[0]['name']} for a {style.lower()} {occasion.lower()} look.")
    else:
        notes.append("Nothing could be selected from this wardrobe.")
    return {"pieces": pieces, "notes": notes}


def auto_name(style, occasion):
    return f"{style} {occasion} Look"


def validate_outfit(name, occasion, style, item_ids):
    """Return a list of problems; an empty list means the outfit is valid."""
    errors = []
    if not name or not name.strip():
        errors.append("Give the outfit a name.")
    elif len(name.strip()) > 60:
        errors.append("Keep the outfit name under 60 characters.")
    if occasion not in OCCASIONS:
        errors.append("Choose an occasion from the list.")
    if style not in STYLES:
        errors.append("Choose a style from the list.")
    if len(set(item_ids)) < 2:
        errors.append("Choose at least two different pieces.")
    return errors


def make_outfit(outfit_id, name, occasion, style, item_ids):
    """The one outfit shape used by the Studio, the Archive and any future database."""
    return {
        "id": outfit_id,
        "name": name.strip(),
        "occasion": occasion,
        "style": style,
        "item_ids": list(dict.fromkeys(item_ids)),  # drops duplicates, keeps order
        "favourite": False,
        "created": datetime.now().strftime("%d %b %Y, %H:%M"),
    }


def resolve_outfit(outfit, items_by_id):
    """Turn an outfit's ids into items. Returns (items, number_missing)."""
    pieces = []
    missing = 0
    for item_id in outfit.get("item_ids", []):
        item = items_by_id.get(item_id)
        if item is None:
            missing += 1
        else:
            pieces.append(item)
    return pieces, missing
