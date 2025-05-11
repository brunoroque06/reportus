from os import path

import streamlit as st

st.set_page_config(
    initial_sidebar_state="expanded", page_icon=":sparkles:", page_title="Reportus"
)


def page(file: str, title: str):
    return st.Page(path.join("reportus", "pages", file), title=title)


pages = [
    ("dtvp3.py", "DTVP-3"),
    ("dtvpa.py", "DTVP-A"),
    ("mabc.py", "MABC"),
    ("spm.py", "SPM"),
]
pages = [page(file, title) for file, title in pages]

pg = st.navigation(pages)

pg.run()
