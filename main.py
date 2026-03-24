import streamlit as st

from src.page import dtvp, mabc, spm

st.set_page_config(
    layout="wide",
    page_title="Reportus",
)


def tabs():
    return [
        ("DTVP-3", lambda: dtvp.page("dtvp3")),
        ("DTVP-A", lambda: dtvp.page("dtvpa")),
        ("MABC", mabc.page),
        ("SPM", spm.page),
    ]


for t_def, t in zip(tabs(), st.tabs([t[0] for t in tabs()])):
    with t:
        t_def[1]()
