import datetime
from typing import Any, Callable, Literal

import streamlit as st

from src.table import Table
from src.time import Delta, minus_delta, to_delta


def header(title: str):
    st.subheader(title)


def hori():
    return st.container(horizontal=True, width="content")


def vert():
    return st.container(
        horizontal=False,
        horizontal_alignment="center",
        width="content",
    )


def structure(title: str):
    st.subheader(title)
    return hori, vert


def date_input(label: str, date: datetime.date, key: str | None = None, **kwargs: Any):
    return st.date_input(label, date, format="DD.MM.YYYY", key=key, **kwargs)


Color = Literal["blue", "green", "red"]


def dates(
    min_years: int,
    max_years: int,
    disp: Callable[[Delta], Color] = lambda _: "blue",
    key: str | None = None,
) -> tuple[datetime.date, datetime.date, Delta]:
    today = datetime.date.today()
    with hori():
        asmt = date_input(
            "Assessment", today, key=f"{key}_asmt" if key else None, max_value=today
        )
        with vert():
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
            age_disp = f"{age.years} years {age.months} months {age.days} days"
            color = disp(age)
            st.badge(age_disp, color=color, icon=":material/cake:")

    return asmt, birth, age


def table(table: Table[Any], hide_cols: list[str] | None = None):
    if hide_cols is None:
        hide_cols = []

    dicts = table.to_dicts()

    def map_level(l: str) -> str:
        return {"0": "↑", "1": "→"}.get(l, "↓")

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
                format_func=map_level,
            ),
            "percentile": st.column_config.ProgressColumn(
                format="%.1f %%", label="%", max_value=100
            ),
            **{c: None for c in hide_cols},
        },
        hide_index=True,
        width="content",
    )


def text(txt: str):
    st.code(txt, language=None, wrap_lines=True, width="content")


cache = st.cache_data
