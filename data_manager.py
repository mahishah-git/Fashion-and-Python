"""Data access layer.

Pages never touch the stored lists directly; they call the functions below.
Right now the records live in Streamlit session state, which means they last
only for the current browser session and reset when the app restarts.

To move to SQLite later, rewrite the bodies of the functions in the
"storage" section; the page files will not need to change.
"""
import copy
import csv
import io
import json
from datetime import datetime

import streamlit as st

import outfit_logic
from sample_data import (CATEGORIES, CLOTHING, OCCASIONS, OUTFITS, PALETTE,
                         PALETTES, SEASONS)

SESSION_NOTE = ("Stored for this browser session only. Changes reset when the app "
                "restarts; use the backup download to keep a copy.")

SORT_OPTIONS = ["Newest first", "Name A to Z", "Price: low to high",
                "Price: high to low", "Colour"]

# ---------------------------------------------------------------- storage

def init_state():
    """Load the sample records once per browser session."""
    if "wardrobe" not in st.session_state:
        st.session_state["wardrobe"] = copy.deepcopy(CLOTHING)
    if "outfits" not in st.session_state:
        st.session_state["outfits"] = copy.deepcopy(OUTFITS)
    if "palettes" not in st.session_state:
        st.session_state["palettes"] = copy.deepcopy(PALETTES)


def _next_id(records):
    return max((record["id"] for record in records), default=0) + 1

# --------------------------------------------------------------- wardrobe

def get_items():
    return st.session_state["wardrobe"]


def get_item(item_id):
    for item in get_items():
        if item["id"] == item_id:
            return item
    return None


def items_by_id():
    return {item["id"]: item for item in get_items()}


def validate_item(data):
    """Return a list of problems with a clothing record (empty list = valid)."""
    errors = []
    name = str(data.get("name", "")).strip()
    if not name:
        errors.append("Enter a name for the piece.")
    elif len(name) > 60:
        errors.append("Keep the name under 60 characters.")
    if data.get("category") not in CATEGORIES:
        errors.append("Choose a category from the list.")
    if data.get("color") not in PALETTE:
        errors.append("Choose a colour from the list.")
    if data.get("season") not in SEASONS:
        errors.append("Choose a season from the list.")
    occasions = data.get("occasion")
    if not occasions or not set(occasions) <= set(OCCASIONS):
        errors.append("Choose at least one occasion.")
    try:
        price = float(data.get("price"))
        if price < 0 or price > 1_000_000:
            errors.append("Enter a price between 0 and 1,000,000.")
    except (TypeError, ValueError):
        errors.append("Enter the price as a number.")
    return errors


def _clean_item(data):
    return {
        "name": str(data["name"]).strip(),
        "category": data["category"],
        "color": data["color"],
        "season": data["season"],
        "occasion": list(data["occasion"]),
        "price": round(float(data["price"])),
        "image": data.get("image", "") or "",
    }


def add_item(data):
    """Returns (new item, []) on success or (None, [errors])."""
    errors = validate_item(data)
    if errors:
        return None, errors
    item = _clean_item(data)
    item["id"] = _next_id(get_items())
    get_items().append(item)
    return item, []


def update_item(item_id, data):
    errors = validate_item(data)
    if errors:
        return None, errors
    item = get_item(item_id)
    if item is None:
        return None, ["That piece no longer exists."]
    item.update(_clean_item(data))
    return item, []


def delete_item(item_id):
    """Outfits keep the id; they show a 'piece removed' note instead of breaking."""
    items = get_items()
    for index, item in enumerate(items):
        if item["id"] == item_id:
            del items[index]
            return True
    return False


def filter_items(items, search="", category="All", colour="All"):
    """Search matches name, category, colour and occasion (case-insensitive)."""
    term = search.strip().lower()
    result = []
    for item in items:
        if category != "All" and item["category"] != category:
            continue
        if colour != "All" and item["color"] != colour:
            continue
        if term:
            text = " ".join([item["name"], item["category"], item["color"],
                             " ".join(item["occasion"])]).lower()
            if term not in text:
                continue
        result.append(item)
    return result


def sort_items(items, sort_by):
    if sort_by == "Name A to Z":
        return sorted(items, key=lambda item: item["name"].lower())
    if sort_by == "Price: low to high":
        return sorted(items, key=lambda item: item["price"])
    if sort_by == "Price: high to low":
        return sorted(items, key=lambda item: item["price"], reverse=True)
    if sort_by == "Colour":
        return sorted(items, key=lambda item: (item["color"], item["name"].lower()))
    return sorted(items, key=lambda item: item["id"], reverse=True)

# ---------------------------------------------------------------- outfits

def get_outfits():
    return st.session_state["outfits"]


def save_outfit(name, occasion, style, item_ids):
    """Returns (outfit, []) on success or (None, [errors])."""
    errors = outfit_logic.validate_outfit(name, occasion, style, item_ids)
    if errors:
        return None, errors
    outfit = outfit_logic.make_outfit(_next_id(get_outfits()), name, occasion, style, item_ids)
    get_outfits().append(outfit)
    return outfit, []


def delete_outfit(outfit_id):
    outfits = get_outfits()
    for index, outfit in enumerate(outfits):
        if outfit["id"] == outfit_id:
            del outfits[index]
            return True
    return False


def toggle_favourite(outfit_id):
    for outfit in get_outfits():
        if outfit["id"] == outfit_id:
            outfit["favourite"] = not outfit["favourite"]
            return outfit["favourite"]
    return False

# --------------------------------------------------------------- palettes

def get_palettes():
    return st.session_state["palettes"]


def save_palette(name, base, colours):
    name = (name or "").strip()
    if not name:
        return None, ["Name the palette before saving it."]
    if base not in PALETTE:
        return None, ["Choose a base colour."]
    palette = {"id": _next_id(get_palettes()), "name": name[:60], "base": base,
               "colours": list(colours), "created": datetime.now().strftime("%d %b %Y, %H:%M")}
    get_palettes().append(palette)
    return palette, []


def delete_palette(palette_id):
    palettes = get_palettes()
    for index, palette in enumerate(palettes):
        if palette["id"] == palette_id:
            del palettes[index]
            return True
    return False

# ------------------------------------------------------- export / backup

def export_json():
    """Whole collection as JSON text, ready for a download button."""
    backup = {"app": "Fashion & Python", "exported": datetime.now().isoformat(timespec="seconds"),
              "wardrobe": get_items(), "outfits": get_outfits(), "palettes": get_palettes()}
    return json.dumps(backup, indent=2)


def export_wardrobe_csv():
    """Wardrobe as CSV text. Uploaded photos are left out to keep the file small."""
    fields = ["id", "name", "category", "color", "season", "occasion", "price", "image"]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for item in get_items():
        row = {field: item.get(field, "") for field in fields}
        row["occasion"] = "|".join(item["occasion"])
        if str(row["image"]).startswith("data:"):
            row["image"] = ""
        writer.writerow(row)
    return buffer.getvalue()


def parse_backup(text):
    """Prepared for the later 'restore' feature. Returns (data, error message)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None, "That file is not valid JSON."
    if not isinstance(data, dict) or not isinstance(data.get("wardrobe"), list):
        return None, "That file does not look like a Fashion & Python backup."
    return data, ""
