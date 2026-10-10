"""Shared presentation helpers: CSS, images, navigation and HTML snippets."""
import base64
import html
from pathlib import Path
from urllib.parse import quote

import streamlit as st

import outfit_logic
from colour_logic import hex_for

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
CSS_PATH = BASE_DIR / "styles" / "magazine.css"

PAGES = ["The Editorial", "The Wardrobe", "The Outfit Studio",
         "The Colour Edit", "The Style Archive"]

MAX_UPLOAD_BYTES = 2_000_000
IMAGE_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".png": "image/png", ".webp": "image/webp"}
_image_cache = {}

# ------------------------------------------------------------ app plumbing

def load_css():
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
    except OSError:
        st.warning("styles/magazine.css was not found, so the default theme is showing.")
        return
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def go_to(page):
    """Button callback: switch the visible page."""
    st.session_state["page"] = page


def keep_alive(keys):
    """Streamlit forgets a widget's value when the widget is not drawn.
    Re-assigning the value keeps filters and selections when you change page."""
    for key in keys:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def flash(kind, message):
    st.session_state["flash"] = (kind, message)


def show_flash():
    pending = st.session_state.pop("flash", None)
    if pending:
        kind, message = pending
        (st.error if kind == "error" else st.success)(message)


def esc(text):
    """Escape user-entered text before it goes into HTML."""
    return html.escape(str(text), quote=True)


def format_price(price):
    try:
        return f"\u20b9{float(price):,.0f}"
    except (TypeError, ValueError):
        return "Price unknown"

# ------------------------------------------------------------------ images

# Simple flat silhouettes, drawn in the item's own colour when no photo exists.
def _shape(path):
    return (f'<path d="{path}" fill="FILL" stroke="#202020" stroke-opacity=".35" '
            f'stroke-width="2" stroke-linejoin="round"/>')


GARMENTS = {
    "Tops": _shape("M62 38 L86 28 Q100 46 114 28 L138 38 L176 76 L153 98 L140 84 L140 192 L60 192 L60 84 L47 98 L24 76 Z"),
    "Bottoms": _shape("M64 32 L136 32 L146 208 L108 208 L100 84 L92 208 L54 208 Z"),
    "Dresses": _shape("M80 25 L92 25 Q100 46 108 25 L120 25 L128 86 L165 210 L35 210 L72 86 Z"),
    "Outerwear": _shape("M62 28 L88 22 L100 60 L112 22 L138 28 L180 92 L156 110 L142 94 L146 216 L54 216 L58 94 L44 110 L20 92 Z")
                 + '<path d="M100 60 L100 216" stroke="#202020" stroke-opacity=".3" stroke-width="2"/>',
    "Shoes": _shape("M28 164 Q28 112 66 102 L84 102 Q94 142 150 150 Q178 154 178 170 L28 170 Z")
             + '<rect x="28" y="170" width="150" height="8" fill="#202020" fill-opacity=".55"/>',
    "Bags": _shape("M44 96 L156 96 L166 198 L34 198 Z")
            + '<path d="M72 96 Q72 48 100 48 Q128 48 128 96" fill="none" stroke="#202020" '
              'stroke-opacity=".5" stroke-width="5"/>',
    "Accessories": _shape("M72 34 Q100 22 128 34 Q134 60 122 82 L142 206 L108 200 L100 100 L92 200 L58 206 L78 82 Q66 60 72 34 Z"),
}


def garment_svg(category, colour_hex):
    body = GARMENTS.get(category, GARMENTS["Accessories"]).replace("FILL", colour_hex)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 250">'
           '<rect width="200" height="250" fill="#EFE9DF"/>'
           '<ellipse cx="100" cy="228" rx="56" ry="6" fill="#202020" fill-opacity=".08"/>'
           + body + "</svg>")
    return "data:image/svg+xml;utf8," + quote(svg, safe="")


def _read_image(path):
    """Local image file -> data URI, or '' if it is missing or unreadable."""
    key = str(path)
    if key in _image_cache:
        return _image_cache[key]
    mime = IMAGE_MIME.get(Path(path).suffix.lower())
    try:
        if mime and Path(path).is_file():
            encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
            _image_cache[key] = f"data:{mime};base64,{encoded}"
            return _image_cache[key]
    except OSError:
        pass
    return ""


# Photos are searched for in the repo root first (next to app.py), then in assets/.
IMAGE_FOLDERS = [BASE_DIR, ASSETS_DIR / "clothing", ASSETS_DIR]


def _normal(text):
    """'Silk Crepe_Blouse.JPG' -> 'silk-crepe-blouse' so file names are forgiving."""
    return Path(str(text)).stem.lower().replace(" ", "-").replace("_", "-")


def find_image(name):
    """Data URI for a photo called `name` (any of jpg/jpeg/png/webp, any capitalisation),
    or '' if no such file exists."""
    wanted = _normal(name)
    if not wanted:
        return ""
    for folder in IMAGE_FOLDERS:
        try:
            files = sorted(folder.iterdir())
        except OSError:
            continue
        for path in files:
            if path.is_file() and path.suffix.lower() in IMAGE_MIME and _normal(path.name) == wanted:
                found = _read_image(path)
                if found:
                    return found
    return ""


def item_image_uri(item):
    """Uploaded photo, then a repo photo named after the item, then a drawn silhouette."""
    image = item.get("image") or ""
    if image.startswith("data:"):
        return image
    if image:
        found = find_image(image)
        if found:
            return found
    return garment_svg(item.get("category"), hex_for(item.get("color")))


def uploaded_to_data_uri(upload):
    """Streamlit upload -> data URI. Returns (uri, error message)."""
    if upload.size > MAX_UPLOAD_BYTES:
        return "", "That photo is over 2 MB. Choose a smaller image."
    mime = IMAGE_MIME.get(Path(upload.name).suffix.lower())
    if not mime:
        return "", "Use a JPG, PNG or WebP image."
    return f"data:{mime};base64," + base64.b64encode(upload.getvalue()).decode("ascii"), ""


def cover_uri():
    """cover.jpg (repo root or assets/) if present, otherwise a generated cover."""
    found = find_image("cover")
    if found:
        return found
    dress = GARMENTS["Dresses"].replace("FILL", "#F7F4EE")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 750">'
           '<rect width="600" height="750" fill="#6F1D32"/>'
           '<rect x="40" y="40" width="520" height="670" fill="none" stroke="#E8C9C4" stroke-opacity=".45"/>'
           '<ellipse cx="300" cy="420" rx="190" ry="250" fill="#E8C9C4"/>'
           f'<g transform="translate(150 215) scale(1.5)">{dress}</g>'
           '<text x="300" y="112" text-anchor="middle" font-family="Georgia,serif" font-size="20" '
           'letter-spacing="9" fill="#F7F4EE">ISSUE 01</text>'
           '<text x="300" y="672" text-anchor="middle" font-family="Georgia,serif" font-size="30" '
           'font-style="italic" fill="#F7F4EE">The Autumn Edit</text></svg>')
    return "data:image/svg+xml;utf8," + quote(svg, safe="")

# ---------------------------------------------------------------- HTML bits

def section_header(eyebrow, title, intro):
    st.markdown(
        f'<div class="fp-header"><div><div class="fp-eyebrow">{eyebrow}</div>'
        f'<h1 class="fp-title">{title}</h1></div><p class="fp-lede">{intro}</p></div>',
        unsafe_allow_html=True)


def subhead(eyebrow, title):
    st.markdown(f'<div class="fp-sub"><div class="fp-eyebrow">{eyebrow}</div>'
                f'<h2 class="fp-h2">{title}</h2></div>', unsafe_allow_html=True)


def empty_state(title, message):
    st.markdown(f'<div class="fp-empty"><div class="fp-h2">{esc(title)}</div>'
                f'<p>{esc(message)}</p></div>', unsafe_allow_html=True)


def item_card_html(item):
    name = esc(item.get("name", ""))
    return ('<div class="fp-card"><div class="fp-card-img">'
            f'<img src="{item_image_uri(item)}" alt="{name}"/></div><div class="fp-card-body">'
            f'<div class="fp-eyebrow">{esc(item.get("category", ""))}</div>'
            f'<div class="fp-card-title">{name}</div>'
            f'<div class="fp-card-meta"><span>{esc(item.get("color", ""))}, {esc(item.get("season", ""))}</span>'
            f'<span>{format_price(item.get("price"))}</span></div></div></div>')


def tile_html(item):
    return ('<div class="fp-tile">'
            f'<img src="{item_image_uri(item)}" alt="{esc(item.get("name", ""))}"/>'
            f'<div class="fp-tile-cat">{esc(item.get("category", ""))}</div>'
            f'<div class="fp-tile-name">{esc(item.get("name", ""))}</div></div>')


def lookbook_html(pieces):
    return '<div class="fp-lookbook">' + "".join(tile_html(p) for p in pieces) + "</div>"


def outfit_card_html(outfit, by_id):
    pieces, missing = outfit_logic.resolve_outfit(outfit, by_id)
    thumbs = "".join(f'<img src="{item_image_uri(p)}" alt="{esc(p["name"])}"/>' for p in pieces)
    names = "".join(f"<li>{esc(p['name'])}</li>" for p in pieces)
    note = (f'<div class="fp-card-meta">{missing} piece(s) removed from the wardrobe</div>'
            if missing else "")
    fav = '<span class="fp-tag fav">Favourite</span>' if outfit.get("favourite") else ""
    total = format_price(sum(p["price"] for p in pieces))
    return ('<div class="fp-outfit">'
            f'<div class="fp-outfit-thumbs">{thumbs or "<div class=fp-outfit-none>No pieces</div>"}</div>'
            f'<div class="fp-outfit-tags"><span class="fp-tag">{esc(outfit.get("style", ""))}</span>'
            f'<span class="fp-tag">{esc(outfit.get("occasion", ""))}</span>{fav}</div>'
            f'<div class="fp-card-title">{esc(outfit.get("name", ""))}</div>'
            f'<ul class="fp-outfit-list">{names}</ul>{note}'
            f'<div class="fp-card-meta"><span>{esc(outfit.get("created", ""))}</span><span>{total}</span></div></div>')


def swatch_html(name, hex_value, selected=False, big=False):
    classes = "fp-swatch" + (" big" if big else "") + (" selected" if selected else "")
    return (f'<div class="{classes}"><div class="fp-swatch-color" style="background:{esc(hex_value)}"></div>'
            f'<div class="fp-swatch-label"><strong>{esc(name)}</strong><span>{esc(hex_value)}</span></div></div>')
