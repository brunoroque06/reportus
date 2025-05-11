import dataclasses
import datetime
import itertools
import math
import typing

import polars as pl
from dateutil import relativedelta

from reportus import perf, str_builder, time


@dataclasses.dataclass(frozen=True)
class Data:
    map_i: pl.DataFrame
    map_t: pl.DataFrame

    def get_i_row(self, i: str, age: int, r: int):
        return self.map_i.filter(
            (pl.col("id") == i)
            & (pl.col("age_min") <= age)
            & (pl.col("age_max") > age)
            & (pl.col("raw_min") <= r)
            & (pl.col("raw_max") >= r)
        )

    def get_t_row(self, i: str, r: int):
        return self.map_t.filter(
            (pl.col("id") == i) & (pl.col("raw_min") <= r) & (pl.col("raw_max") >= r)
        )


@perf.cache
def _load() -> Data:
    map_i = pl.read_csv("data/mabc-i.csv")
    map_t = pl.read_csv("data/mabc-t.csv")
    return Data(map_i, map_t)


def validate():
    data = _load()
    ages = range(
        data.map_i.select("age_min").min().item(),
        data.map_i.select("age_max").max().item(),
    )
    for a in ages:
        ids = [
            i
            for lst in get_comps(relativedelta.relativedelta(years=a)).values()
            for i in lst
        ]
        raws = range(0, 122)

        for i, r in itertools.product(ids, raws):
            row = data.get_i_row(i, a, r)
            assert row.select("standard").item() > 0

    ids = ["hg", "bf", "bl", "gw"]
    raws = range(0, 109)
    for i, r in itertools.product(ids, raws):
        row = data.get_t_row(i, r)
        assert row.select("standard").item() > 0
        assert row.select("percentile").item() > 0


def get_comps(age: relativedelta.relativedelta) -> dict[str, list[str]]:
    return {
        "Handgeschicklichkeit": ["hg11", "hg12", "hg2", "hg3"],
        "Ballfertigkeiten": (
            ["bf1", "bf2"] if age.years < 11 else ["bf11", "bf12", "bf2"]
        ),
        "Balance": (
            ["bl11", "bl12", "bl2", "bl3"]
            if age.years < 7
            else (
                ["bl11", "bl12", "bl2", "bl31", "bl32"]
                if age.years < 11
                else ["bl1", "bl2", "bl31", "bl32"]
            )
        ),
    }


def get_failed() -> list[str]:
    return ["hg11", "hg12", "hg2", "hg3"]


def _process_comp(
    data: Data, age: int, raw: dict[str, typing.Optional[int]]
) -> dict[str, tuple[int | None, int]]:
    comp: dict[str, tuple[int | None, int]] = {}
    for k, v in raw.items():
        std = 1 if v is None else data.get_i_row(k, age, v).select("standard").item()
        comp[k] = (v, std)

    def avg(v0: int, v1: int) -> int:
        a = (v0 + v1) / 2
        if a < 10:
            return math.floor(a)
        return math.ceil(a)

    comp["hg1"] = (None, avg(comp["hg11"][1], comp["hg12"][1]))
    if age > 10:
        comp["bf1"] = (None, avg(comp["bf11"][1], comp["bf12"][1]))
    if age < 11:
        comp["bl1"] = (None, avg(comp["bl11"][1], comp["bl12"][1]))
    if age > 6:
        comp["bl3"] = (None, avg(comp["bl31"][1], comp["bl32"][1]))

    return comp


def _process_agg(
    data: Data, comp: dict[str, tuple[int | None, int]]
) -> dict[str, list[int]]:
    agg: dict[str, list[int]] = {}

    for cmp in ["hg", "bf", "bl"]:
        score = sum(
            v[1] if len(k) == 3 and k.startswith(cmp) else 0 for k, v in comp.items()
        )
        row = data.get_t_row(cmp, score)
        agg[cmp] = [
            score,
            row.select("standard").item(),
            row.select("percentile").item(),
        ]

    score = sum(v[0] for v in agg.values())
    row = data.get_t_row("gw", score)
    agg["total"] = [
        score,
        row.select("standard").item(),
        row.select("percentile").item(),
    ]

    return agg


def level(std: int) -> typing.Literal[0, 1, 2, 3]:
    if std > 7:
        return 0
    if std == 7:
        return 1
    if std == 6:
        return 2
    return 3


def process(
    age: relativedelta.relativedelta,
    raw: dict[str, typing.Optional[int]],
    asmt: datetime.date | None = None,
    hand: str = "Right",
) -> tuple[pl.DataFrame, pl.DataFrame, str]:
    if asmt is None:
        asmt = datetime.date.today()

    data = _load()

    comp = _process_comp(data, age.years, raw)

    agg = _process_agg(data, comp)

    comp_res = pl.DataFrame(
        [[k, *list(v), level(v[1])] for k, v in comp.items()],
        schema=["id", "raw", "standard", "level"],
        orient="row",
    )

    agg_res = pl.DataFrame(
        [[k, *list(v), level(v[1])] for k, v in agg.items()],
        schema=["id", "raw", "standard", "percentile", "level"],
        orient="row",
    )

    return comp_res, agg_res, report(asmt, age, hand, agg_res)


def report(
    asmt: datetime.date, age: relativedelta.relativedelta, hand: str, agg: pl.DataFrame
) -> str:
    if age.years < 7:
        group = "3-6"
    elif age.years < 11:
        group = "7-10"
    else:
        group = "11-16"

    def level_str(std: int) -> str:
        lvl = level(std)
        if lvl == 0:
            return "unauffällig"
        if lvl == 1:
            return "unauffällig im untersten Normbereich"
        if lvl == 2:
            return "kritisch"
        return "therapiebedürftig"

    def perc(i: str):
        return agg.filter(pl.col("id") == i).select("percentile").item()

    def std(i: str):
        return agg.filter(pl.col("id") == i).select("standard").item()

    tot = agg.filter(pl.col("id") == "total")

    rep = str_builder.StrBuilder()

    rep.append(
        f"Movement Assessment Battery for Children 2nd Edition (M-ABC 2) - {time.format_date(asmt)}"
    )
    rep.append(f"Protokollbogen Altersgruppe: {group} Jahre")
    rep.append()
    rep.append(f"Handgeschicklichkeit: PR {perc('hg')} - {level_str(std('hg'))}")
    rep.append(f"Händigkeit: {'Rechts' if hand == 'Right' else 'Links'}")
    rep.append(f"Ballfertigkeit: PR {perc('bf')} - {level_str(std('bf'))}")
    rep.append(f"Balance: PR {perc('bl')} - {level_str(std('bl'))}")
    rep.append()
    rep.append(
        f"Gesamttestwert: PR {tot.select('percentile').item()} - {level_str(tot.select('standard').item())}"
    )

    return str(rep)
