import dataclasses
import datetime
import itertools

import polars as pl
from dateutil import relativedelta

from reportus import dtvp, perf, time


@dataclasses.dataclass(frozen=True)
class Data:
    std: pl.DataFrame
    sums: pl.DataFrame

    def get_std(self, i: str, age: relativedelta.relativedelta, r: int):
        return self.std.filter(
            (pl.col("id") == i)
            & (pl.col("age_min") <= age.years)
            & (pl.col("age_max") > age.years)
            & (pl.col("raw_min") <= r)
            & (pl.col("raw_max") >= r)
        )

    def get_sum(self, i: str, su: int):
        return self.sums.filter((pl.col("id") == i) & (pl.col("sum") == su))


@perf.cache
def _load() -> Data:
    std = pl.read_csv("data/dtvpa-std.csv")
    sums = pl.read_csv("data/dtvpa-sum.csv")
    return Data(std, sums)


def validate():
    data = _load()
    ids = get_tests().keys()
    ages = range(11, 18)
    raws = range(0, 109)

    for i, a, r in itertools.product(ids, ages, raws):
        row = data.get_std(i, relativedelta.relativedelta(years=a), r)
        assert row.select("standard").item() > 0
        assert row.select("percentile").item() >= 0

    for i, su in itertools.chain(
        itertools.product(["sum3"], range(3, 61)),
        itertools.product(["sum6"], range(6, 116)),
    ):
        row = data.get_sum(i, su)
        assert row.select("index").item() > 0
        assert row.select("percentile").item() >= 0


def get_tests() -> dict[str, str]:
    return {
        "co": "Copying",
        "fg": "Figure-Ground",
        "vse": "Visual-Motor Search",
        "vc": "Visual Closure",
        "vsp": "Visual-Motor Speed",
        "fc": "Form Constancy",
    }


def report(asmt: datetime.date, sub: pl.DataFrame, comp: pl.DataFrame) -> str:
    return "\n".join(
        [
            f"Developmental Test of Visual Perception - Adolescent and Adult (DTVP-A) - ({time.format_date(asmt)})",
            "",
        ]
        + [
            f"{n}: PR {comp.filter(pl.col('id') == i).select('%ile').item()} - {dtvp.lvl_idx(comp.filter(pl.col('id') == i).select('index').item(), True)[0]}"
            for n, i in [
                ("Visuomotorische Integration", "Visual-Motor Integration (VMII)"),
                (
                    "Motorik-Reduzierte Wahrnehmung",
                    "Motor-Reduced Visual Perception (MRPI)",
                ),
                ("Globale Visuelle Wahrnehmung", "General Visual Perception (GVPI)"),
            ]
        ]
        + [
            "",
            "Subtests:",
        ]
        + [
            f"{n}: PR {sub.filter(pl.col('id') == i).select('%ile').item()} - {dtvp.lvl_sca(sub.filter(pl.col('id') == i).select('standard').item(), True)[0]}"
            for n, i in [
                ("Abzeichnen", "co"),
                ("Figur-Grund", "fg"),
                ("Visuomotorisches Suchen", "vse"),
                ("Gesaltschliessen", "vc"),
                ("Visuomotorische Geschwindigkeit", "vsp"),
                ("Formkonstanz", "fc"),
            ]
        ]
    )


def process(
    age: relativedelta.relativedelta,
    raw: dict[str, int],
    asmt: datetime.date | None = None,
) -> tuple[pl.DataFrame, pl.DataFrame, str]:
    if asmt is None:
        asmt = datetime.date.today()

    data = _load()

    tests = get_tests()

    def get_std(k: str, r: int):
        row = data.get_std(k, age, r)
        per = row.select("percentile").item()
        std = row.select("standard").item()
        return [
            dtvp.to_pr(per),
            std,
            *dtvp.lvl_sca(std),
        ]

    sub = pl.DataFrame(
        [[k, v, raw[k], *get_std(k, raw[k])] for k, v in tests.items()],
        schema=["id", "label", "raw", "%ile", "standard", "description", "level"],
        orient="row",
    )

    comps = [
        (
            "gvpi",
            "General Visual Perception (GVPI)",
            sub.select("standard").sum().item(),
            "sum6",
        ),
        (
            "mrpi",
            "Motor-Reduced Visual Perception (MRPI)",
            sub.filter(pl.col("id") == "fg").select("standard").item()
            + sub.filter(pl.col("id") == "vc").select("standard").item()
            + sub.filter(pl.col("id") == "fc").select("standard").item(),
            "sum3",
        ),
        (
            "vmii",
            "Visual-Motor Integration (VMII)",
            sub.filter(pl.col("id") == "co").select("standard").item()
            + sub.filter(pl.col("id") == "vse").select("standard").item()
            + sub.filter(pl.col("id") == "vsp").select("standard").item(),
            "sum3",
        ),
    ]

    def get_comp(i: str, su: int):
        row = data.get_sum(i, su)
        idx = row.select("index").item()
        return [idx, dtvp.to_pr(row.select("percentile").item()), *dtvp.lvl_idx(idx)]

    comp = pl.DataFrame(
        [[l, su, *get_comp(i, su)] for _, l, su, i in comps],
        orient="row",
        schema=["id", "sum_standard", "index", "%ile", "description", "level"],
    )

    return sub, comp, report(asmt, sub, comp)
