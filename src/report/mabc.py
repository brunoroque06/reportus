import dataclasses
import datetime
import itertools
import math
import typing

from src import string, table, time, ui


@dataclasses.dataclass(frozen=True)
class IRow:
    id: str
    age_min: int
    age_max: float
    raw_min: int
    raw_max: float
    standard: int
    rank: int


@dataclasses.dataclass(frozen=True)
class TRow:
    id: str
    raw_min: int
    raw_max: float
    standard: int
    percentile: float
    rank: int


@ui.cache
def _load() -> tuple[table.Table[IRow], table.Table[TRow]]:
    map_i = table.read_csv("public/mabc-i.csv", IRow)
    map_t = table.read_csv("public/mabc-t.csv", TRow)
    return map_i, map_t


def _get_i_row(data: table.Table[IRow], i: str, age: int, r: int) -> IRow:
    return data.filter(
        id=i,
        age_min=lambda v: v <= age,
        age_max=lambda v: v > age,
        raw_min=lambda v: v <= r,
        raw_max=lambda v: v >= r,
    ).item()


def _get_t_row(data: table.Table[TRow], i: str, r: int) -> TRow:
    return data.filter(
        id=i,
        raw_min=lambda v: v <= r,
        raw_max=lambda v: v >= r,
    ).item()


def validate():
    map_i, map_t = _load()
    age_min = min(r.age_min for r in map_i.rows)
    age_max = max(int(r.age_max) for r in map_i.rows if r.age_max != float("inf"))
    ages = range(age_min, age_max)
    for a in ages:
        ids = [i for lst in get_comps(time.Delta(years=a)).values() for i in lst]
        raws = range(0, 122)

        for i, r in itertools.product(ids, raws):
            row = _get_i_row(map_i, i, a, r)
            assert row.standard > 0

    ids = ["hg", "bf", "bl", "gw"]
    raws = range(0, 109)
    for i, r in itertools.product(ids, raws):
        row = _get_t_row(map_t, i, r)
        assert row.standard > 0
        assert row.percentile > 0


def get_comps(age: time.Delta) -> dict[str, list[str]]:
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
    map_i: table.Table[IRow], age: int, raw: dict[str, typing.Optional[int]]
) -> dict[str, tuple[int | None, int]]:
    comp: dict[str, tuple[int | None, int]] = {}
    for k, v in raw.items():
        std = 1 if v is None else _get_i_row(map_i, k, age, v).standard
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
    map_t: table.Table[TRow], comp: dict[str, tuple[int | None, int]]
) -> dict[str, list[int | float]]:
    agg: dict[str, list[int | float]] = {}

    for cmp in ["hg", "bf", "bl"]:
        score = sum(
            v[1] if len(k) == 3 and k.startswith(cmp) else 0 for k, v in comp.items()
        )
        row = _get_t_row(map_t, cmp, score)
        agg[cmp] = [score, row.standard, row.percentile]

    score = sum(int(v[0]) for v in agg.values())
    row = _get_t_row(map_t, "gw", score)
    agg["total"] = [score, row.standard, row.percentile]

    return agg


def level(std: int) -> typing.Literal[0, 1, 2, 3]:
    if std > 7:
        return 0
    if std == 7:
        return 1
    if std == 6:
        return 2
    return 3


@dataclasses.dataclass(frozen=True)
class CompResultRow:
    id: str
    raw: int | None
    standard: int
    level: int


@dataclasses.dataclass(frozen=True)
class AggResultRow:
    id: str
    raw: int
    standard: int
    percentile: float
    level: int


def process(
    age: time.Delta,
    raw: dict[str, typing.Optional[int]],
    asmt: datetime.date,
    hand: str = "Right",
) -> tuple[table.Table[CompResultRow], table.Table[AggResultRow], str]:
    map_i, map_t = _load()

    comp = _process_comp(map_i, age.years, raw)

    agg = _process_agg(map_t, comp)

    comp_rows = [
        CompResultRow(id=k, raw=v[0], standard=v[1], level=level(v[1]))
        for k, v in comp.items()
    ]

    agg_rows = [
        AggResultRow(
            id=k,
            raw=int(v[0]),
            standard=int(v[1]),
            percentile=v[2],
            level=level(int(v[1])),
        )
        for k, v in agg.items()
    ]

    return (
        table.Table(comp_rows),
        table.Table(agg_rows),
        report(asmt, age, hand, table.Table(agg_rows)),
    )


def report(
    asmt: datetime.date, age: time.Delta, hand: str, agg: table.Table[AggResultRow]
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

    def perc(i: str) -> float:
        return agg.filter(id=i).item().percentile

    def std(i: str) -> int:
        return agg.filter(id=i).item().standard

    tot = agg.filter(id="total").item()

    rep = string.StrBuilder()

    rep.add(
        f"Movement Assessment Battery for Children 2nd Edition (M-ABC 2) - {time.format_date(asmt)}"
    )
    rep.add(f"Protokollbogen Altersgruppe: {group} Jahre")
    rep.add()
    rep.add(f"Handgeschicklichkeit: PR {perc('hg')} - {level_str(std('hg'))}")
    rep.add(f"Händigkeit: {'Rechts' if hand == 'Right' else 'Links'}")
    rep.add(f"Ballfertigkeit: PR {perc('bf')} - {level_str(std('bf'))}")
    rep.add(f"Balance: PR {perc('bl')} - {level_str(std('bl'))}")
    rep.add()
    rep.add(f"Gesamttestwert: PR {tot.percentile} - {level_str(tot.standard)}")

    return rep.build()
