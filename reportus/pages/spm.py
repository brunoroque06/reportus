import datetime

import streamlit as st

from reportus import spm, ui

ui.header("SPM")

cols = st.columns(4)
today = datetime.date.today()

with cols[0]:
    ver = st.selectbox("Version", (1, 2))
with cols[1]:
    asmt = ui.date_input("Assessment", today, max_value=today)


def ver1():
    return ver == 1


with cols[2]:
    form: spm.Form = st.selectbox("Form", ("Classroom", "Home") if ver1() else ("Home"))  # type: ignore
with cols[3]:
    filled = st.selectbox(
        "Filled by",
        ("Km", "Kv", "Ke") if form == "Home" else ("LP", "BP"),
    )

scores = spm.get_scores()

left = ["soc", "vis", "hea"] if ver1() else ["vis", "hea", "tou", "t&s", "bod", "bal"]
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

res, rep = spm.process(asmt, form, ver, filled, name, raw)

ui.text(rep)

res = res.to_pandas().set_index("id")  # type: ignore

res = res.style.format({"t": "{:.0f}"})  # type: ignore
ui.table(res)
