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
    hori, vert = ui.structure("MABC")

    with hori():
        with vert():
            asmt_date, _, age = ui.dates(5, 16, disp=display_age, key="mabc")

            comps = mabc.get_comps(age)
            comp_ids = list(comps.keys())

            with hori():
                hand = st.selectbox("Preferred Hand", ("Right", "Left"))
                failed = st.multiselect(
                    "Failed", mabc.get_failed(), format_func=str.upper, width=400
                )

            raw: dict[str, typing.Optional[int]] = {}

            with hori():
                for comp_id in comp_ids:
                    with vert():
                        st.markdown(f"**{comp_id}**")
                        for exe in comps[comp_id]:
                            raw[exe] = st.number_input(
                                label=exe.upper(),
                                min_value=0,
                                max_value=150,
                                step=1,
                                disabled=(exe in failed),
                            )

            for f in failed:
                raw[f] = None

        with vert():
            comp, agg, rep = mabc.process(age, raw, asmt=asmt_date, hand=hand)
            ui.text(rep)

            with hori():
                for c in ["hg", "bf", "bl"]:
                    t = comp.filter(id=lambda i: i.startswith(c))  # pyright: ignore[reportUnknownMemberType]
                    t = t.sort(key=lambda r: r.id if len(r.id) == 4 else r.id + "z")
                    ui.table(t)

            ui.table(agg)
