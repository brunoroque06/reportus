import datetime

import streamlit as st

from src import ui
from src.report import spm


def page():
    left_col, right_col = ui.structure("SPM")

    with left_col:
        cols = st.columns(4)
        today = datetime.date.today()

        with cols[0]:
            ver = st.selectbox("Version", (1, 2))
        with cols[1]:
            asmt = ui.date_input("Assessment", today, key="spm", max_value=today)

        def ver1():
            return ver == 1

        with cols[2]:
            form = st.selectbox("Form", spm.forms(ver))
        with cols[3]:
            filer = st.selectbox(
                "Filled by",
                spm.filers(form),
                format_func=lambda f: f.name,
            )

        scores = spm.get_scores()

        left = (
            ["soc", "vis", "hea"]
            if ver1()
            else ["vis", "hea", "tou", "t&s", "bod", "bal"]
        )
        right = ["tou", "t&s", "bod", "bal", "pln"] if ver1() else ["pln", "soc"]

        raw: dict[str, int] = {}

        cols = st.columns(2)
        with cols[0]:
            for s in left:
                raw[s] = st.number_input(scores[s], step=1)

        with cols[1]:
            for s in right:
                raw[s] = st.number_input(scores[s], step=1)

        name = None
        if not ver1():
            cols = st.columns(2)
            with cols[0]:
                name = st.text_input("Name")

        res, rep = spm.process(asmt, form, ver, filer, name, raw)

    with right_col:
        ui.text(rep)
        ui.table(res)
