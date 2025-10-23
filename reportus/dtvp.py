import dataclasses
import datetime
import itertools

import polars as pl

from reportus import perf, str_builder, time


@dataclasses.dataclass(frozen=True)
class Data:
    ra: pl.DataFrame
    rs: pl.DataFrame
    sp: pl.DataFrame

    def get_ra(self, i: str, raw: int):
        return self.ra.filter(
            (pl.col("id") == i)
            & (pl.col("raw_min") <= raw)
            & (pl.col("raw_max") >= raw)
        )

    def get_rs(self, i: str, age: time.Delta, raw: int):
        months = age.years * 12 + age.months
        return self.rs.filter(
            (pl.col("id") == i)
            & (pl.col("age_min") <= months)
            & (pl.col("age_max") >= months)
            & (pl.col("raw_min") <= raw)
            & (pl.col("raw_max") >= raw)
        )

    def get_sp(self, i: str, s: int):
        return self.sp.filter((pl.col("id") == i) & (pl.col("scaled") == s))


@perf.cache
def _load() -> Data:
    ra = pl.read_csv("data/dtvp-raw-ageeq.csv")
    rs = pl.read_csv("data/dtvp-raw-sca.csv")
    rs = rs.with_columns(
        age_min=pl.col("age_min_y") * 12 + pl.col("age_min_m"),
        age_max=pl.col("age_max_y") * 12 + pl.col("age_max_m"),
    )
    sp = pl.read_csv("data/dtvp-sca-per.csv")
    return Data(ra, rs, sp)


def validate():
    data = _load()

    for i, r in itertools.product(get_tests().keys(), range(0, 188)):
        row = data.get_ra(i, r)
        assert row.select("age_eq_y").item() >= 0
        assert row.select("age_eq_m").item() >= 0

    for i, y, m, r in itertools.product(
        get_tests().keys(), range(4, 13), range(0, 12, 2), range(0, 194)
    ):
        row = data.get_rs(i, time.Delta(years=y, months=m), r)
        assert row.select("scaled").item() > 0
        assert row.select("percentile").item() >= 0

    for i, su in itertools.chain(
        itertools.product(["vmi"], range(2, 41)),
        itertools.product(["mrvp"], range(3, 60)),
        itertools.product(["gvp"], range(5, 99)),
    ):
        row = data.get_sp(i, su)
        assert row.select("percentile").item() >= 0
        assert row.select("index").item() > 0


def get_tests() -> dict[str, str]:
    return {
        "eh": "Eye-Hand Coordination (EH)",
        "co": "Copying (CO)",
        "fg": "Figure-Ground (FG)",
        "vc": "Visual Closure (VC)",
        "fc": "Form Constancy (FC)",
    }


VERY_POOR = "Very Poor"
POOR = "Poor"
BELOW_AVERAGE = "Below Average"
AVERAGE = "Average"
ABOVE_AVERAGE = "Above Average"
SUPERIOR = "Superior"
VERY_SUPERIOR = "Very Superior"


def lvl_sca(s: int, de: bool = False) -> tuple[str, int]:
    if s < 4:
        return ("weit unterdurchschnittlich" if de else VERY_POOR, 2)
    if s < 6:
        return ("unterdurchschnittlich" if de else POOR, 2)
    if s < 8:
        return ("unterdurchschnittlich" if de else BELOW_AVERAGE, 2)
    if s < 13:
        return ("durchschnittlich" if de else AVERAGE, 1)
    if s < 15:
        return ("überdurchschnittlich" if de else ABOVE_AVERAGE, 0)
    if s < 17:
        return ("weit überdurchschnittlich" if de else SUPERIOR, 0)
    return ("weit überdurchschnittlich" if de else VERY_SUPERIOR, 0)


def lvl_idx(i: int, de: bool = False) -> tuple[str, int]:
    if i < 70:
        return ("Weit unter der Norm" if de else VERY_POOR, 2)
    if i < 80:
        return ("Weit unter der Norm" if de else POOR, 2)
    if i < 90:
        return ("Unter der Norm" if de else BELOW_AVERAGE, 2)
    if i < 111:
        return ("Norm" if de else AVERAGE, 1)
    if i < 121:
        return ("Über der Norm" if de else ABOVE_AVERAGE, 0)
    if i < 131:
        return ("Weit über der Norm" if de else SUPERIOR, 0)
    return ("Weit über der Norm" if de else VERY_SUPERIOR, 0)


def to_pr(p: int) -> str:
    if p == 0:
        return "<1"
    if p == 100:
        return ">99"
    return str(p)


def to_age(a: str) -> str:
    if a == "3;11":
        return "<4;0"
    if a == "13;0":
        return ">12;9"
    return a


def process(
    age: time.Delta,
    raw: dict[str, int],
    asmt: datetime.date | None = None,
) -> tuple[pl.DataFrame, pl.DataFrame, str]:
    if asmt is None:
        asmt = datetime.date.today()

    data = _load()

    tests = get_tests()

    def age_eq(k: str) -> str:
        row = data.get_ra(k, raw[k])
        years = row.select("age_eq_y").item()
        months = row.select("age_eq_m").item()
        return f"{years};{months}"

    def scaled(k: str):
        row = data.get_rs(k, age, raw[k])
        per = row.select("percentile").item()
        sca = row.select("scaled").item()
        return [per, sca, *lvl_sca(sca)]

    sub = pl.DataFrame(
        [[k, v, raw[k], age_eq(k), *scaled(k)] for k, v in tests.items()],
        orient="row",
        schema=[
            "id",
            "label",
            "raw",
            "age_eq",
            "percentile",
            "scaled",
            "descriptive",
            "level",
        ],
    )

    comps = [
        (
            "vmi",
            "Visual-Motor Integration",
            sub.filter(pl.col("id") == "eh").select("scaled").item()
            + sub.filter(pl.col("id") == "co").select("scaled").item(),
        ),
        (
            "mrvp",
            "Motor-reduced Visual Perception",
            sub.filter(pl.col("id") == "fg").select("scaled").item()
            + sub.filter(pl.col("id") == "vc").select("scaled").item()
            + sub.filter(pl.col("id") == "fc").select("scaled").item(),
        ),
        (
            "gvp",
            "General Visual Perception",
            sub.select("scaled").sum().item(),
        ),
    ]

    def get_sp(i: str, s: int):
        row = data.get_sp(i, s)
        return [
            row.select("percentile").item(),
            *lvl_idx(row.select("index").item()),
            row.select("index").item(),
        ]

    comp = pl.DataFrame(
        [[l, v, *get_sp(k, v)] for k, l, v in comps],
        orient="row",
        schema=["id", "sum_scaled", "percentile", "descriptive", "level", "index"],
    )

    rep = report(asmt, sub, comp)

    sub = sub.with_columns(pl.col("age_eq").map_elements(to_age, pl.String))
    sub = sub.with_columns(pl.col("percentile").map_elements(to_pr, pl.String))
    comp = comp.with_columns(pl.col("percentile").map_elements(to_pr, pl.String))

    return sub, comp, rep


def report(asmt: datetime.date, sub: pl.DataFrame, comp: pl.DataFrame) -> str:
    rep = str_builder.StrBuilder()

    rep.append(
        f"Developmental Test of Visual Perception (DTVP-3) - {time.format_date(asmt)}"
    )
    rep.append()

    for n, i in [
        ("Visuomotorische Integration", 0),
        ("Visuelle Wahrnehmung mit reduzierter motorischer Reaktion", 1),
        ("Globale visuelle Wahrnehmung", 2),
    ]:
        rep.append(
            f"{n}: PR {to_pr(comp['percentile'][i])} - {lvl_idx(comp['index'][i], True)[0]}"
        )

    rep.append()
    rep.append("Subtests:")

    for n, i in [
        ("Augen-Hand-Koordination", 0),
        ("Abzeichnen", 1),
        ("Figur-Grund", 2),
        ("Gesaltschliessen", 3),
        ("Formkonstanz", 4),
    ]:
        rep.append(
            f"{n}: {to_age(sub['age_eq'][i])} J ({lvl_sca(sub['scaled'][i], True)[0]})"
        )

    return str(rep)
