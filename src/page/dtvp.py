import typing

import streamlit as st

from src import ui
from src.report import dtvp, dtvpa


def page(rep: typing.Literal["dtvp3", "dtvpa"]) -> None:
    if rep == "dtvp3":
        title = "DTVP-3"
        min_age = 4
        max_age = 13
        get_tests = dtvp.get_tests
        process = dtvp.process
    else:
        title = "DTVP-A"
        min_age = 11
        max_age = 18
        get_tests = dtvpa.get_tests
        process = dtvpa.process

    hori, vert = ui.structure(title)

    with hori():
        with vert():
            asmt_date, _, age = ui.dates(min_age, max_age, key=rep)

            raw: dict[str, int] = {}
            tests = get_tests()

            for k, v in tests.items():
                raw[k] = st.number_input(v, step=1)

        with vert():
            sub, comp, report = process(age, raw, asmt_date)
            ui.text(report)
            ui.table(sub, hide_cols=["id"])
            ui.table(comp)
