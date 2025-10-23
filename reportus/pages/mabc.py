import typing

import pandas as pd
import streamlit as st

from reportus import mabc, ui
from reportus.time import Delta

ui.header("MABC")


def display_age(a: Delta) -> ui.Color:
    if a.years < 7:
        return "red"
    if a.years < 11:
        return "green"
    return "blue"


asmt_date, birth, age = ui.dates(5, 16, display_age)

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

for c in [
    ("Handgeschicklichkeit", "hg"),
    ("Ballfertigkeiten", "bf"),
    ("Balance", "bl"),
]:
    cat = (
        comp.to_pandas()
        .astype({"raw": pd.Int64Dtype()})  # type: ignore
        .set_index("id")  # type: ignore
        .filter(like=c[1], axis=0)  # type: ignore
        .sort_values(
            by=["id"],
            key=lambda s: s.map(lambda i: i if len(i) == 4 else i + "z"),  # type: ignore
        )
    )
    ui.table(cat, c[0])

order = {"hg": 0, "bf": 1, "bl": 2, "total": 4}
agg = agg.to_pandas().set_index("id").sort_values(by=["id"], key=lambda x: x.map(order))  # type: ignore
agg = agg.style.format({"percentile": "{:.1f}"})  # type: ignore
ui.table(agg, "Aggregated")  # type: ignore
