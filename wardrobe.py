"""Page two: The Wardrobe (search, filter, sort, add, edit, delete)."""
import streamlit as st

import data_manager as dm
import ui
from sample_data import CATEGORIES, OCCASIONS, PALETTE, SEASONS

FILTER_KEYS = ["wd_search", "wd_category", "wd_colour", "wd_sort"]
COLUMNS = 4


def _index(options, value):
    """Position of value in options, or 0 if it is not there."""
    return options.index(value) if value in options else 0


def item_form(form_key, item=None, submit_label="Save piece"):
    """Shared add/edit form. Returns a data dict when submitted, else None."""
    current = item or {}
    colours = list(PALETTE)
    with st.form(form_key, clear_on_submit=item is None):
        name = st.text_input("Name", value=current.get("name", ""), max_chars=60,
                             placeholder="e.g. Silk Crepe Blouse")
        left, right = st.columns(2)
        category = left.selectbox("Category", CATEGORIES, index=_index(CATEGORIES, current.get("category")))
        colour = right.selectbox("Colour", colours, index=_index(colours, current.get("color")))
        season = left.selectbox("Season", SEASONS, index=_index(SEASONS, current.get("season")))
        price = right.number_input("Price (INR)", min_value=0, max_value=1_000_000,
                                   value=int(current.get("price", 0)), step=100)
        occasions = st.multiselect("Occasions", OCCASIONS, default=current.get("occasion", ["Casual"]))
        upload = st.file_uploader("Photograph (optional)", type=["jpg", "jpeg", "png", "webp"],
                                  key=f"{form_key}_photo")
        submitted = st.form_submit_button(submit_label)
    if not submitted:
        return None

    image = current.get("image", "")
    if upload is not None:
        image, problem = ui.uploaded_to_data_uri(upload)
        if problem:
            st.error(problem)
            return None
    return {"name": name, "category": category, "color": colour, "season": season,
            "occasion": occasions, "price": price, "image": image}


# Button callbacks keep the card controls simple.
def _start_edit(item_id):
    st.session_state["editing_id"] = item_id
    st.session_state["confirm_delete_id"] = None


def _stop_edit():
    st.session_state["editing_id"] = None


def _ask_delete(item_id):
    st.session_state["confirm_delete_id"] = item_id


def _cancel_delete():
    st.session_state["confirm_delete_id"] = None


def _confirm_delete(item_id):
    item = dm.get_item(item_id)
    if dm.delete_item(item_id):
        ui.flash("success", f"{item['name']} was removed from the wardrobe.")
    st.session_state["confirm_delete_id"] = None


def _clear_filters():
    st.session_state.update({"wd_search": "", "wd_category": "All", "wd_colour": "All",
                             "wd_sort": dm.SORT_OPTIONS[0]})


def render():
    ui.keep_alive(FILTER_KEYS)
    st.session_state.setdefault("editing_id", None)
    st.session_state.setdefault("confirm_delete_id", None)

    ui.section_header("The Wardrobe", "Everything you own,<br/>in one place",
                      "Browse, search and organise every piece. Add new arrivals, correct details, "
                      "and retire what no longer earns its place.")
    st.caption(dm.SESSION_NOTE)

    # Edit form (only while a piece is being edited)
    editing = dm.get_item(st.session_state["editing_id"]) if st.session_state["editing_id"] else None
    if editing:
        with st.container(border=True):
            st.markdown(f"**Editing: {editing['name']}**")
            data = item_form(f"edit_form_{editing['id']}", editing, "Save changes")
            st.button("Cancel editing", key="cancel_edit", on_click=_stop_edit)
            if data:
                _item, errors = dm.update_item(editing["id"], data)
                if errors:
                    st.error(" ".join(errors))
                else:
                    st.session_state["editing_id"] = None
                    ui.flash("success", "Changes saved.")
                    st.rerun()

    with st.expander("Add a piece to the wardrobe"):
        data = item_form("add_form", None, "Add piece")
        if data:
            item, errors = dm.add_item(data)
            if errors:
                st.error(" ".join(errors))
            else:
                ui.flash("success", f"{item['name']} was added to the wardrobe.")
                st.rerun()

    ui.show_flash()

    # Filters
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    search = c1.text_input("Search", key="wd_search", placeholder="Name, colour, category or occasion")
    category = c2.selectbox("Category", ["All"] + CATEGORIES, key="wd_category")
    colour = c3.selectbox("Colour", ["All"] + list(PALETTE), key="wd_colour")
    sort_by = c4.selectbox("Sort by", dm.SORT_OPTIONS, key="wd_sort")

    items = dm.get_items()
    shown = dm.sort_items(dm.filter_items(items, search, category, colour), sort_by)
    st.markdown(f'<p class="fp-count">Showing {len(shown)} of {len(items)} pieces</p>',
                unsafe_allow_html=True)

    if not items:
        ui.empty_state("The wardrobe is empty", "Open 'Add a piece to the wardrobe' above to begin.")
        return
    if not shown:
        ui.empty_state("Nothing matches this search",
                       "Try a different word, or clear the filters to see every piece again.")
        st.button("Clear filters", key="clear_filters", on_click=_clear_filters)
        return

    for start in range(0, len(shown), COLUMNS):
        columns = st.columns(COLUMNS)
        for column, item in zip(columns, shown[start:start + COLUMNS]):
            with column:
                st.markdown(ui.item_card_html(item), unsafe_allow_html=True)
                if st.session_state["confirm_delete_id"] == item["id"]:
                    st.markdown('<p class="fp-confirm">Remove this piece?</p>', unsafe_allow_html=True)
                    yes, no = st.columns(2)
                    yes.button("Remove", key=f"yes_{item['id']}", type="primary",
                               on_click=_confirm_delete, args=(item["id"],), use_container_width=True)
                    no.button("Keep", key=f"no_{item['id']}", on_click=_cancel_delete,
                              use_container_width=True)
                else:
                    edit, delete = st.columns(2)
                    edit.button("Edit", key=f"edit_{item['id']}", on_click=_start_edit,
                                args=(item["id"],), use_container_width=True)
                    delete.button("Delete", key=f"del_{item['id']}", on_click=_ask_delete,
                                  args=(item["id"],), use_container_width=True)
