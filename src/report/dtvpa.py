import dataclasses
import datetime
import itertools

from src import string, table, time
from src.report import dtvp


@dataclasses.dataclass(frozen=True)
class Std:
    id: str
    age_min: int
    age_max: float
    raw_min: int
    raw_max: float
    standard: int
    percentile: int


@dataclasses.dataclass(frozen=True)
class Sum:
    id: str
    sum: int
    index: int
    percentile: int


def _load() -> tuple[table.Table[Std], table.Table[Sum]]:
    std = table.read_csv("public/dtvpa-std.csv", Std)
    sums = table.read_csv("public/dtvpa-sum.csv", Sum)
    return std, sums


def _get_std(data: table.Table[Std], i: str, age: time.Delta, r: int) -> Std:
    return data.filter(
        id=i,
        age_min=lambda v: v <= age.years,
        age_max=lambda v: v > age.years,
        raw_min=lambda v: v <= r,
        raw_max=lambda v: v >= r,
    ).item()


def _get_sum(data: table.Table[Sum], i: str, su: int) -> Sum:
    return data.filter(id=i, sum=su).item()


def validate():
    std, sums = _load()
    ids = get_tests().keys()
    ages = range(11, 18)
    raws = range(0, 109)

    for i, a, r in itertools.product(ids, ages, raws):
        row = _get_std(std, i, time.Delta(years=a), r)
        assert row.standard > 0
        assert row.percentile >= 0

    for i, su in itertools.chain(
        itertools.product(["sum3"], range(3, 61)),
        itertools.product(["sum6"], range(6, 116)),
    ):
        row = _get_sum(sums, i, su)
        assert row.index > 0
        assert row.percentile >= 0


def get_tests() -> dict[str, str]:
    return {
        "co": "Copying",
        "fg": "Figure-Ground",
        "vse": "Visual-Motor Search",
        "vc": "Visual Closure",
        "vsp": "Visual-Motor Speed",
        "fc": "Form Constancy",
    }


@dataclasses.dataclass(frozen=True)
class Sub:
    id: str
    label: str
    raw: int
    standard: int
    percentile: int
    description: str
    level: int


@dataclasses.dataclass(frozen=True)
class Comp:
    id: str
    sum_standard: int
    index: int
    percentile: int
    description: str
    level: int


def report(asmt: datetime.date, sub: table.Table[Sub], comp: table.Table[Comp]) -> str:
    rep = string.StrBuilder()
    rep.add(
        f"Developmental Test of Visual Perception - Adolescent and Adult (DTVP-A) - ({time.format_date(asmt)})"
    )
    rep.add()

    for n, i in [
        ("Visuomotorische Integration", "Visual-Motor Integration (VMII)"),
        (
            "Motorik-Reduzierte Wahrnehmung",
            "Motor-Reduced Visual Perception (MRPI)",
        ),
        ("Globale Visuelle Wahrnehmung", "General Visual Perception (GVPI)"),
    ]:
        row = comp.filter(id=i).item()
        rep.add(
            f"{n}: PR {dtvp.to_pr(row.percentile)} - {dtvp.lvl_idx(row.index, True)[0]}"
        )

    rep.add()
    rep.add("Subtests:")

    for n, i in [
        ("Abzeichnen", "co"),
        ("Figur-Grund", "fg"),
        ("Visuomotorisches Suchen", "vse"),
        ("Gesaltschliessen", "vc"),
        ("Visuomotorische Geschwindigkeit", "vsp"),
        ("Formkonstanz", "fc"),
    ]:
        row = sub.filter(id=i).item()
        rep.add(
            f"{n}: PR {dtvp.to_pr(row.percentile)} - {dtvp.lvl_sca(row.standard, True)[0]}"
        )

    return rep.build()


def process(
    age: time.Delta,
    raw: dict[str, int],
    asmt: datetime.date | None = None,
) -> tuple[table.Table[Sub], table.Table[Comp], str]:
    if asmt is None:
        asmt = datetime.date.today()

    std, sums = _load()

    tests = get_tests()

    sub_rows: list[Sub] = []
    for k, v in tests.items():
        row = _get_std(std, k, age, raw[k])
        desc, lvl = dtvp.lvl_sca(row.standard)
        sub_rows.append(
            Sub(
                id=k,
                label=v,
                raw=raw[k],
                percentile=row.percentile,
                standard=row.standard,
                description=desc,
                level=lvl,
            )
        )

    sub = table.Table(sub_rows)

    def get_sub_std(sid: str) -> int:
        return sub.filter(id=sid).item().standard

    comps = [
        (
            "gvpi",
            "General Visual Perception (GVPI)",
            sum(r.standard for r in sub.rows),
            "sum6",
        ),
        (
            "mrpi",
            "Motor-Reduced Visual Perception (MRPI)",
            get_sub_std("fg") + get_sub_std("vc") + get_sub_std("fc"),
            "sum3",
        ),
        (
            "vmii",
            "Visual-Motor Integration (VMII)",
            get_sub_std("co") + get_sub_std("vse") + get_sub_std("vsp"),
            "sum3",
        ),
    ]

    comp_rows: list[Comp] = []
    for _, l, su, i in comps:
        row = _get_sum(sums, i, su)
        desc, lvl = dtvp.lvl_idx(row.index)
        comp_rows.append(
            Comp(
                id=l,
                sum_standard=su,
                index=row.index,
                percentile=row.percentile,
                description=desc,
                level=lvl,
            )
        )

    comp = table.Table(comp_rows)

    return sub, comp, report(asmt, sub, comp)
