"""FASHION & PYTHON: app configuration, navigation and page routing.

Run with:  streamlit run app.py
"""
from datetime import datetime

import streamlit as st

st.set_page_config(page_title="Fashion & Python", layout="wide", initial_sidebar_state="expanded")

import colour_edit
import data_manager as dm
import editorial
import outfit_studio
import style_archive
import ui
import wardrobe

ROUTES = {
    "The Editorial": editorial.render,
    "The Wardrobe": wardrobe.render,
    "The Outfit Studio": outfit_studio.render,
    "The Colour Edit": colour_edit.render,
    "The Style Archive": style_archive.render,
}


def sidebar(current):
    with st.sidebar:
        st.markdown('<div class="fp-brand"><div class="fp-wordmark">Fashion <span>&amp;</span> Python</div>'
                    '<div class="fp-quiet">An exploration of personal style.</div></div>',
                    unsafe_allow_html=True)
        for page in ui.PAGES:
            st.button(page, key=f"nav_{page}", on_click=ui.go_to, args=(page,),
                      type="primary" if page == current else "secondary", use_container_width=True)
        st.markdown(f'<p class="fp-side-note">{dm.SESSION_NOTE}</p>', unsafe_allow_html=True)


def masthead():
    today = datetime.now().strftime("%A, %d %B %Y")
    st.markdown(f'<div class="fp-masthead"><span class="fp-wordmark">Fashion <span>&amp;</span> Python</span>'
                f'<span>{today}</span></div>', unsafe_allow_html=True)


def main():
    dm.init_state()
    ui.load_css()
    st.session_state.setdefault("page", ui.PAGES[0])
    if st.session_state["page"] not in ROUTES:
        st.session_state["page"] = ui.PAGES[0]
    current = st.session_state["page"]
    sidebar(current)
    masthead()
    ROUTES[current]()


main()
