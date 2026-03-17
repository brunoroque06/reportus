import typing

import streamlit as st

from src import ui
from src.report import mabc
from src.time import Delta


def display_age(a: Delta) -> ui.Color:
    if a.years < 7:
        return "red"
    if a.years < 11:
        return "green"
    return "blue"


def page():
    left, right = ui.structure("MABC")

    with left:
        asmt_date, _, age = ui.dates(5, 16, display_age, key="mabc")

        comps = mabc.get_comps(age)
        comp_ids = list(comps.keys())

        cols = st.columns([1, 2])
        with cols[0]:
            hand = st.selectbox("Preferred Hand", ("Right", "Left"))

        with cols[1]:
            failed = st.multiselect("Failed", mabc.get_failed(), format_func=str.upper)

        cols = st.columns(len(comp_ids))

        raw: dict[str, typing.Optional[int]] = {}

        for i, col in enumerate(cols):
            comp_id = comp_ids[i]
            col.markdown(f"***{comp_id}***")
            for exe in comps[comp_id]:
                raw[exe] = col.number_input(
                    label=exe.upper(),
                    min_value=0,
                    max_value=150,
                    step=1,
                    disabled=(exe in failed),
                )

        for f in failed:
            raw[f] = None

        comp, agg, rep = mabc.process(age, raw, asmt=asmt_date, hand=hand)
        ui.text(rep)

    with right:
        for c in [
            ("Handgeschicklichkeit", "hg"),
            ("Ballfertigkeiten", "bf"),
            ("Balance", "bl"),
        ]:
            t = comp.filter(id=lambda i: i.startswith(c[1]))  # pyright: ignore[reportUnknownMemberType]
            t = t.sort(key=lambda r: r.id if len(r.id) == 4 else r.id + "z")
            ui.table(t, c[0])

        ui.table(agg, "Aggregated")
