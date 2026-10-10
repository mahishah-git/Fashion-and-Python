"""Page three: The Outfit Studio (manual builder + Style Shuffle)."""
import streamlit as st

import data_manager as dm
import outfit_logic
import ui
from colour_logic import colours_compatible
from outfit_logic import SLOTS
from sample_data import OCCASIONS, STYLES

SLOT_KEYS = [f"studio_{slot}" for slot, _label, _cats in SLOTS]
STATE_KEYS = SLOT_KEYS + ["studio_occasion", "studio_style", "studio_name"]


# Callbacks run before the page redraws, so they can safely set widget values.
def _shuffle():
    result = outfit_logic.style_shuffle(
        dm.get_items(), st.session_state["studio_occasion"], st.session_state["studio_style"])
    for slot, _label, _cats in SLOTS:
        piece = result["pieces"][slot]
        st.session_state[f"studio_{slot}"] = piece["id"] if piece else 0
    st.session_state["studio_notes"] = result["notes"]
    st.session_state["studio_name"] = ""


def _reset():
    for key in SLOT_KEYS:
        st.session_state[key] = 0
    st.session_state["studio_name"] = ""
    st.session_state["studio_notes"] = []


def _save():
    ids = [st.session_state.get(key, 0) for key in SLOT_KEYS]
    ids = [item_id for item_id in ids if item_id]
    occasion = st.session_state["studio_occasion"]
    style = st.session_state["studio_style"]
    name = st.session_state.get("studio_name", "").strip() or outfit_logic.auto_name(style, occasion)
    outfit, errors = dm.save_outfit(name, occasion, style, ids)
    if errors:
        ui.flash("error", " ".join(errors))
    else:
        ui.flash("success", f"{outfit['name']} was added to the Style Archive (this session only).")


def _colour_check(pieces):
    """Plain-language colour feedback using the same rule as Style Shuffle."""
    clashes = []
    for i, first in enumerate(pieces):
        for second in pieces[i + 1:]:
            if not colours_compatible(first["color"], second["color"]):
                clashes.append(f"{first['color']} and {second['color']}")
    if len(pieces) < 2:
        return ""
    if clashes:
        return "Colour check: " + "; ".join(clashes) + " may compete. Try a neutral between them."
    return "Colour check: these colours sit well together."


def render():
    ui.keep_alive(STATE_KEYS)
    st.session_state.setdefault("studio_notes", [])
    ui.section_header("The Outfit Studio", "Compose a look,<br/>piece by piece",
                      "Choose from your wardrobe or let Style Shuffle propose a combination "
                      "using simple colour and occasion rules.")
    ui.show_flash()

    items = dm.get_items()
    by_id = dm.items_by_id()
    controls, preview = st.columns([5, 7], gap="large")

    with controls:
        st.selectbox("Occasion", OCCASIONS, key="studio_occasion")
        st.selectbox("Style", STYLES, key="studio_style")
        st.text_input("Outfit name", key="studio_name", max_chars=60,
                      placeholder="Leave blank for an automatic name")
        for slot, label, categories in SLOTS:
            pool = sorted(outfit_logic.items_in_categories(items, categories),
                          key=lambda item: item["name"].lower())
            options = [0] + [item["id"] for item in pool]
            names = {item["id"]: f"{item['name']} ({item['color']})" for item in pool}
            key = f"studio_{slot}"
            if st.session_state.get(key, 0) not in options:
                st.session_state[key] = 0  # the piece was deleted or re-categorised
            st.selectbox(label, options, key=key,
                         format_func=lambda value, names=names: "None" if value == 0 else names.get(value, "Unknown"))
        st.button("Style Shuffle", key="shuffle", type="primary", on_click=_shuffle, use_container_width=True)
        b2, b3 = st.columns(2)
        b2.button("Save outfit", key="save", on_click=_save, use_container_width=True)
        b3.button("Reset", key="reset", on_click=_reset, use_container_width=True)

    with preview:
        selected = [by_id[st.session_state[key]] for key in SLOT_KEYS
                    if st.session_state.get(key) in by_id]
        if selected:
            st.markdown(ui.lookbook_html(selected), unsafe_allow_html=True)
            check = _colour_check(selected)
            if check:
                st.markdown(f'<p class="fp-quiet">{ui.esc(check)}</p>', unsafe_allow_html=True)
        else:
            ui.empty_state("Your look starts here",
                           "Pick a piece on the left, or press Style Shuffle for a first suggestion.")
        if st.session_state["studio_notes"]:
            st.markdown('<div class="fp-eyebrow">How Style Shuffle chose</div>', unsafe_allow_html=True)
            for note in st.session_state["studio_notes"]:
                st.markdown(f"- {note}")

    ui.subhead("Recently created", "Latest looks")
    recent = list(reversed(dm.get_outfits()))[:3]
    if recent:
        for column, outfit in zip(st.columns(3, gap="large"), recent):
            column.markdown(ui.outfit_card_html(outfit, by_id), unsafe_allow_html=True)
    else:
        ui.empty_state("Nothing saved yet", "Looks you save appear here and in the Style Archive.")
    st.caption(dm.SESSION_NOTE)
