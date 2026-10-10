"""Page one: The Editorial (the magazine cover)."""
import streamlit as st

import data_manager as dm
import outfit_logic
import ui


def _first(items, category):
    for item in items:
        if item["category"] == category:
            return item
    return items[0] if items else None


def _signature_colour(items):
    """Most common colour in the wardrobe, counted with a dictionary."""
    counts = {}
    for item in items:
        counts[item["color"]] = counts.get(item["color"], 0) + 1
    return max(counts, key=counts.get) if counts else "None yet"


def _collage(items):
    return ('<div class="fp-collage"><div class="fp-collage-main">'
            f'<img src="{ui.cover_uri()}" alt="Editorial cover"/></div></div>')


def render():
    items = dm.get_items()
    outfits = dm.get_outfits()
    by_id = dm.items_by_id()

    left, right = st.columns([7, 5], gap="large")
    with left:
        st.markdown(
            '<div class="fp-hero"><div class="fp-eyebrow">Issue 01: an exploration of personal style</div>'
            '<h1 class="fp-display">Style is<br/><em>a personal story.</em></h1>'
            '<p class="fp-lede">Fashion &amp; Python is a small studio for your wardrobe. '
            'Catalogue what you own, compose outfits piece by piece, test colours against each '
            'other, and keep the looks you love in an archive of your own.</p></div>',
            unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        b1.button("Open the wardrobe", key="hero_wardrobe", type="primary",
                  on_click=ui.go_to, args=("The Wardrobe",), use_container_width=True)
        b2.button("Enter the studio", key="hero_studio",
                  on_click=ui.go_to, args=("The Outfit Studio",), use_container_width=True)
        st.markdown('<p class="fp-quiet">Discover your wardrobe. Curate your style.</p>',
                    unsafe_allow_html=True)
    with right:
        st.markdown(_collage(items), unsafe_allow_html=True)

    favourites = [o for o in outfits if o.get("favourite")]
    stats = [(len(items), "Pieces in the wardrobe"), (len(outfits), "Looks created"),
             (len(favourites), "Favourite looks"), (_signature_colour(items), "Signature colour")]
    st.markdown('<div class="fp-stats">' + "".join(
        f'<div class="fp-stat"><div class="fp-stat-n">{ui.esc(n)}</div>'
        f'<div class="fp-stat-l">{label}</div></div>' for n, label in stats) + "</div>",
        unsafe_allow_html=True)

    # Featured look: newest favourite, otherwise the newest look.
    featured = favourites[-1] if favourites else (outfits[-1] if outfits else None)
    ui.subhead("The featured look", "Worn well, worn often")
    if featured:
        pieces, _missing = outfit_logic.resolve_outfit(featured, by_id)
        text, tiles = st.columns([4, 8], gap="large")
        with text:
            st.markdown(
                f'<div class="fp-feature"><h3 class="fp-h3">{ui.esc(featured["name"])}</h3>'
                f'<p class="fp-lede">A {ui.esc(featured["style"].lower())} look for '
                f'{ui.esc(featured["occasion"].lower())} days, made from {len(pieces)} pieces '
                f'valued at {ui.format_price(sum(p["price"] for p in pieces))}.</p></div>',
                unsafe_allow_html=True)
            st.button("See all looks", key="feature_archive",
                      on_click=ui.go_to, args=("The Style Archive",))
        with tiles:
            st.markdown(ui.lookbook_html(pieces), unsafe_allow_html=True)
    else:
        ui.empty_state("No looks yet", "Compose your first outfit in the Outfit Studio and it will appear here.")

    ui.subhead("The edit", "Four considered pieces")
    if items:
        chosen = sorted(items, key=lambda item: item["price"], reverse=True)[:4]
        for column, item in zip(st.columns(4), chosen):
            column.markdown(ui.item_card_html(item), unsafe_allow_html=True)
    else:
        ui.empty_state("An empty wardrobe", "Add a piece in The Wardrobe to start the edit.")

    ui.subhead("Continue reading", "Where to next")
    links = [
        ("The Outfit Studio", "Compose a look or let Style Shuffle suggest one."),
        ("The Colour Edit", "Pick a base colour and see what belongs beside it."),
        ("The Style Archive", "Revisit, favourite and curate the looks you saved."),
    ]
    for column, (page, blurb) in zip(st.columns(3, gap="large"), links):
        with column:
            st.markdown(f'<div class="fp-link"><h3 class="fp-h3">{page}</h3><p>{blurb}</p></div>',
                        unsafe_allow_html=True)
            st.button(f"Open {page}", key=f"link_{page}", on_click=ui.go_to, args=(page,),
                      use_container_width=True)
