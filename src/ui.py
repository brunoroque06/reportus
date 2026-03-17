import datetime
from typing import Any, Callable, Literal

import streamlit as st

from src.table import Table
from src.time import Delta, minus_delta, to_delta


def header(title: str):
    st.subheader(title)


def structure(title: str):
    st.subheader(title)
    return st.columns([0.4, 0.6])


def date_input(label: str, date: datetime.date, key: str | None = None, **kwargs: Any):
    return st.date_input(label, date, format="DD.MM.YYYY", key=key, **kwargs)


Color = Literal["blue", "green", "red"]


def dates(
    min_years: int,
    max_years: int,
    disp: Callable[[Delta], Color] = lambda _: "blue",
    key: str | None = None,
) -> tuple[datetime.date, datetime.date, Delta]:
    col1, col2, col3 = st.columns([1, 1, 2])

    today = datetime.date.today()
    with col1:
        asmt = date_input(
            "Assessment", today, key=f"{key}_asmt" if key else None, max_value=today
        )

    with col2:
        birth = date_input(
            "Birthday",
            minus_delta(
                asmt, Delta(years=min_years + int((max_years - min_years) / 2))
            ),
            key=f"{key}_birth" if key else None,
            max_value=minus_delta(asmt, Delta(min_years)),
            min_value=minus_delta(asmt, Delta(years=max_years - 1, days=364)),
        )

    age = to_delta(birth, asmt)

    with col3:
        st.text(" ")
        age_disp = f"Age: {age.years} years, {age.months} months, {age.days} days"
        color = disp(age)
        age_comp = st.info
        if color == "green":
            age_comp = st.success
        elif color == "red":
            age_comp = st.error
        age_comp(age_disp, icon="🎂")
        # st.color_picker(..., disabled=True, label_visibility="collapsed") is an alternative

    return asmt, birth, age


def table(table: Table[Any], title: str | None = None, hide_cols: list[str] = []):
    dicts = table.to_dicts()

    if title:
        st.text(title)

    def level_map(l: str) -> str:
        if l == "0":
            return "OK"
        if l == "1":
            return "-"
        return "X"

    st.dataframe(  # pyright: ignore[reportUnknownMemberType]
        dicts,
        column_config={
            "level": st.column_config.MultiselectColumn(
                "",
                options=[
                    "0",
                    "1",
                    "2",
                    "3",
                ],
                color=["green", "yellow", "red", "red"],
                disabled=True,
                format_func=level_map,
            ),
            "percentile": st.column_config.ProgressColumn(
                format="%.1f %%", label="%", max_value=100
            ),
            **{c: None for c in hide_cols},
        },
        hide_index=True,
    )


def text(txt: str):
    st.code(txt, language=None, wrap_lines=True)


cache = st.cache_data
