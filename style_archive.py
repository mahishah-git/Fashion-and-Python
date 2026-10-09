"""Page five: The Style Archive (saved outfits)."""
import streamlit as st

import data_manager as dm
import ui
from sample_data import OCCASIONS, STYLES

KEYS = ["ar_style", "ar_occasion", "ar_fav"]


def _favourite(outfit_id):
    dm.toggle_favourite(outfit_id)


def _ask(outfit_id):
    st.session_state["confirm_delete_outfit"] = outfit_id


def _cancel():
    st.session_state["confirm_delete_outfit"] = None


def _confirm(outfit_id):
    dm.delete_outfit(outfit_id)
    st.session_state["confirm_delete_outfit"] = None
    ui.flash("success", "The look was removed from the archive.")


def render():
    ui.keep_alive(KEYS)
    st.session_state.setdefault("confirm_delete_outfit", None)
    ui.section_header("The Style Archive", "Looks worth keeping",
                      "Every outfit you save lands here. Favourite the ones you reach for, "
                      "filter by style or occasion, and retire the rest.")
    ui.show_flash()

    outfits = dm.get_outfits()
    by_id = dm.items_by_id()
    f1, f2, f3 = st.columns([2, 2, 2])
    style = f1.selectbox("Style", ["All"] + STYLES, key="ar_style")
    occasion = f2.selectbox("Occasion", ["All"] + OCCASIONS, key="ar_occasion")
    f3.markdown("<div class='fp-spacer'></div>", unsafe_allow_html=True)
    only_fav = f3.checkbox("Favourites only", key="ar_fav")

    shown = [o for o in reversed(outfits)
             if (style == "All" or o["style"] == style)
             and (occasion == "All" or o["occasion"] == occasion)
             and (not only_fav or o["favourite"])]
    st.markdown(f'<p class="fp-count">Showing {len(shown)} of {len(outfits)} looks</p>',
                unsafe_allow_html=True)

    if not outfits:
        ui.empty_state("The archive is empty",
                       "Build a look in the Outfit Studio and save it. It will be filed here.")
        st.button("Go to the Outfit Studio", key="empty_to_studio", type="primary",
                  on_click=ui.go_to, args=("The Outfit Studio",))
    elif not shown:
        ui.empty_state("No looks match these filters", "Change the style or occasion, or untick favourites.")
    else:
        for start in range(0, len(shown), 3):
            for column, outfit in zip(st.columns(3, gap="large"), shown[start:start + 3]):
                with column:
                    st.markdown(ui.outfit_card_html(outfit, by_id), unsafe_allow_html=True)
                    if st.session_state["confirm_delete_outfit"] == outfit["id"]:
                        yes, no = st.columns(2)
                        yes.button("Confirm remove", key=f"oyes_{outfit['id']}", type="primary",
                                   on_click=_confirm, args=(outfit["id"],), use_container_width=True)
                        no.button("Keep", key=f"ono_{outfit['id']}", on_click=_cancel, use_container_width=True)
                    else:
                        fav, remove = st.columns(2)
                        fav.button("Unfavourite" if outfit["favourite"] else "Favourite",
                                   key=f"fav_{outfit['id']}", on_click=_favourite,
                                   args=(outfit["id"],), use_container_width=True)
                        remove.button("Remove", key=f"orm_{outfit['id']}", on_click=_ask,
                                      args=(outfit["id"],), use_container_width=True)

    with st.expander("Back up your data"):
        st.caption(dm.SESSION_NOTE)
        d1, d2 = st.columns(2)
        d1.download_button("Download JSON backup", dm.export_json(),
                           file_name="fashion-and-python-backup.json", mime="application/json",
                           use_container_width=True)
        d2.download_button("Download wardrobe CSV", dm.export_wardrobe_csv(),
                           file_name="fashion-and-python-wardrobe.csv", mime="text/csv",
                           use_container_width=True)
