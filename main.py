from os import path

import streamlit as st


st.set_page_config(
    initial_sidebar_state="expanded",
    layout="wide",
    page_title="Reportus",
)


def pages():
    return [
        ("dtvp3.py", "DTVP-3"),
        ("dtvpa.py", "DTVP-A"),
        ("mabc.py", "MABC"),
        ("spm.py", "SPM"),
    ]


pg = st.navigation(
    [st.Page(path.join("src", "page", file), title=title) for file, title in pages()]
)

pg.run()
