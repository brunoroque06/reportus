import datetime
import typing

import pandas as pd
import streamlit as st
from dateutil import relativedelta
from pandas.io.formats import style


def header(title: str):
    st.subheader(title)


def date_input(label: str, date: datetime.date, **kwargs: typing.Any):
    return st.date_input(label, date, format="DD.MM.YYYY", **kwargs)


Color = typing.Literal["blue", "green", "red"]


def dates(
    min_years: int,
    max_years: int,
    disp: typing.Callable[[relativedelta.relativedelta], Color] = lambda _: "blue",
) -> tuple[datetime.date, datetime.date, relativedelta.relativedelta]:
    col1, col2, col3 = st.columns([1, 1, 2])

    today = datetime.date.today()
    with col1:
        asmt = date_input("Assessment", today, max_value=today)

    with col2:
        birth = date_input(
            "Birthday",
            asmt
            - relativedelta.relativedelta(
                years=min_years + int((max_years - min_years) / 2)
            ),
            max_value=asmt - relativedelta.relativedelta(years=min_years),
            min_value=asmt - relativedelta.relativedelta(years=max_years - 1, days=364),
        )

    age = relativedelta.relativedelta(asmt, birth)

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


def table(df: pd.DataFrame | style.Styler, title: str | None = None):
    if isinstance(df, pd.DataFrame):
        df = df.style

    def color_row(row: pd.DataFrame) -> list[str]:
        levels = {
            0: "rgba(33, 195, 84, 0.1)",
            1: "rgba(255, 193, 7, 0.1)",
            2: "rgba(255, 43, 43, 0.09)",
            3: "rgba(255, 43, 43, 0.09)",
        }
        lvl: int | None = row["level"]  # type: ignore
        if pd.isna(lvl):
            return [""] * len(row)
        color = levels[lvl]
        return [f"background-color: {color};"] * len(row)

    df = df.apply(color_row, axis=1)  # type: ignore

    if title:
        st.text(title)
    st.dataframe(  # type: ignore
        df, column_config={"level": {"hidden": True}}
    )


def text(txt: str):
    st.code(txt, language=None, wrap_lines=True)
