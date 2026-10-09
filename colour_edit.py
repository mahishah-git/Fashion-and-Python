"""Page four: The Colour Edit (palette explorer)."""
import streamlit as st

import colour_logic as cl
import data_manager as dm
import ui
from sample_data import PALETTE

KEYS = ["ce_base", "ce_neutrals", "ce_palette_name"]


def _row(names, big=True):
    html = "".join(ui.swatch_html(n, cl.hex_for(n), big=big) for n in names)
    return f'<div class="fp-palette-row">{html}</div>'


def _save():
    palette = cl.build_palette(st.session_state["ce_base"])
    name = st.session_state.get("ce_palette_name", "").strip() or f"{palette['base']} Edit"
    saved, errors = dm.save_palette(name, palette["base"], cl.palette_colours(palette))
    if errors:
        ui.flash("error", " ".join(errors))
    else:
        ui.flash("success", f"Palette '{saved['name']}' saved (this session only).")
        st.session_state["ce_palette_name"] = ""


def _delete(palette_id):
    dm.delete_palette(palette_id)


def render():
    ui.keep_alive(KEYS)
    ui.section_header("The Colour Edit", "Colour, considered",
                      "Choose a base colour. The edit shows what sits beside it, what contrasts "
                      "with it, and which pieces you already own in those shades.")
    ui.show_flash()

    st.session_state.setdefault("ce_base", "Burgundy")
    base = st.selectbox("Base colour", list(PALETTE), key="ce_base")
    palette = cl.build_palette(base)

    ui.subhead("The curated palette", "Sixteen shades")
    st.markdown('<div class="fp-swatch-grid">' + "".join(
        ui.swatch_html(name, hex_value, selected=(name == base)) for name, hex_value in PALETTE.items())
        + "</div>", unsafe_allow_html=True)

    ui.subhead("Your edit", f"Built around {ui.esc(base)}")
    text, swatches = st.columns([4, 8], gap="large")
    with text:
        st.markdown(f'<p class="fp-lede">{ui.esc(cl.describe_palette(palette))}</p>', unsafe_allow_html=True)
    with swatches:
        st.markdown('<div class="fp-eyebrow">Base</div>' + _row([base]), unsafe_allow_html=True)
        groups = ([("Accent colours", palette["accents"])] if palette["neutral"] else
                  [("Analogous: close on the wheel", palette["analogous"]),
                   ("Complementary: opposite", palette["complementary"])])
        for title, names in groups:
            if names:
                st.markdown(f'<div class="fp-eyebrow">{title}</div>' + _row(names), unsafe_allow_html=True)

    names = cl.palette_colours(palette)
    st.session_state.setdefault("ce_neutrals", True)
    include = st.checkbox("Include neutrals in the matches", key="ce_neutrals")
    matches = cl.items_matching(dm.get_items(), names, include_neutrals=include)
    ui.subhead("From your wardrobe", f"{len(matches)} matching pieces")
    if matches:
        for start in range(0, min(len(matches), 8), 4):
            for column, item in zip(st.columns(4), matches[start:start + 4]):
                column.markdown(ui.item_card_html(item), unsafe_allow_html=True)
    else:
        ui.empty_state("No pieces in these shades", "Add something in this palette to The Wardrobe, "
                                                    "or choose a different base colour.")

    ui.subhead("Keep it", "Save this palette")
    n1, n2 = st.columns([3, 1])
    n1.text_input("Palette name", key="ce_palette_name", placeholder=f"{base} Edit")
    n2.markdown("<div class='fp-spacer'></div>", unsafe_allow_html=True)
    n2.button("Save palette", key="save_palette", type="primary", on_click=_save, use_container_width=True)

    saved = dm.get_palettes()
    if saved:
        st.markdown('<div class="fp-eyebrow">Saved palettes</div>', unsafe_allow_html=True)
        for palette_record in reversed(saved):
            a, b = st.columns([6, 1])
            a.markdown(f'<div class="fp-saved"><strong>{ui.esc(palette_record["name"])}</strong>'
                       + _row(palette_record["colours"], big=False) + "</div>", unsafe_allow_html=True)
            b.button("Delete", key=f"delpal_{palette_record['id']}", on_click=_delete,
                     args=(palette_record["id"],), use_container_width=True)
    st.caption(dm.SESSION_NOTE)
