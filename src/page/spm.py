import datetime

import streamlit as st

from src import ui
from src.report import spm


def page():
    hori, vert = ui.structure("SPM")

    with hori():
        with vert():
            today = datetime.date.today()

            def ver1():
                return ver == 1

            with hori():
                asmt = ui.date_input("Assessment", today, key="spm", max_value=today)
            with hori():
                ver = st.selectbox("Version", (1, 2))
                form = st.selectbox("Form", spm.forms(ver))
                filer = st.selectbox(
                    "Filled by",
                    spm.filers(form),
                    format_func=lambda f: f.name,
                )

            scores = spm.get_scores()

            left_forms = (
                ["soc", "vis", "hea"]
                if ver1()
                else ["vis", "hea", "tou", "t&s", "bod", "bal"]
            )
            right_forms = (
                ["tou", "t&s", "bod", "bal", "pln"] if ver1() else ["pln", "soc"]
            )

            raw: dict[str, int] = {}

            with hori():
                with vert():
                    for s in left_forms:
                        raw[s] = st.number_input(scores[s], step=1)

                with vert():
                    for s in right_forms:
                        raw[s] = st.number_input(scores[s], step=1)

            name = None
            if not ver1():
                name = st.text_input("Name")

        with vert():
            res, rep = spm.process(asmt, form, ver, filer, name, raw)
            ui.text(rep)
            ui.table(res)
