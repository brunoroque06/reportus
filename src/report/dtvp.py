import dataclasses
import datetime
import itertools

from src import string, table, time


@dataclasses.dataclass(frozen=True)
class RawAge:
    id: str
    raw_min: int
    raw_max: float
    age_eq_y: int
    age_eq_m: int


@dataclasses.dataclass(frozen=True)
class RawSca:
    id: str
    age_min_y: int
    age_min_m: int
    age_max_y: int
    age_max_m: int
    raw_min: int
    raw_max: float
    scaled: int
    percentile: int


@dataclasses.dataclass(frozen=True)
class ScaPer:
    id: str
    scaled: int
    percentile: int
    index: int


def _load() -> tuple[table.Table[RawAge], table.Table[RawSca], table.Table[ScaPer]]:
    ra = table.read_csv("public/dtvp-raw-ageeq.csv", RawAge)
    rs = table.read_csv("public/dtvp-raw-sca.csv", RawSca)
    sp = table.read_csv("public/dtvp-sca-per.csv", ScaPer)
    return ra, rs, sp


def _get_ra(data: table.Table[RawAge], i: str, raw: int) -> RawAge:
    return data.filter(
        id=i,
        raw_min=lambda v: v <= raw,
        raw_max=lambda v: v >= raw,
    ).item()


def _get_rs(data: table.Table[RawSca], i: str, age: time.Delta, raw: int) -> RawSca:
    months = age.years * 12 + age.months
    matching = [
        r
        for r in data.rows
        if r.id == i
        and r.raw_min <= raw
        and r.raw_max >= raw
        and (r.age_min_y * 12 + r.age_min_m) <= months
        and (r.age_max_y * 12 + r.age_max_m) >= months
    ]
    return matching[0]


def _get_sp(data: table.Table[ScaPer], i: str, s: int) -> ScaPer:
    return data.filter(id=i, scaled=s).item()


def validate():
    ra, rs, sp = _load()

    for i, r in itertools.product(get_tests().keys(), range(0, 188)):
        row = _get_ra(ra, i, r)
        assert row.age_eq_y >= 0
        assert row.age_eq_m >= 0

    for i, y, m, r in itertools.product(
        get_tests().keys(), range(4, 13), range(0, 12, 2), range(0, 194)
    ):
        row = _get_rs(rs, i, time.Delta(years=y, months=m), r)
        assert row.scaled > 0
        assert row.percentile >= 0

    for i, su in itertools.chain(
        itertools.product(["vmi"], range(2, 41)),
        itertools.product(["mrvp"], range(3, 60)),
        itertools.product(["gvp"], range(5, 99)),
    ):
        row = _get_sp(sp, i, su)
        assert row.percentile >= 0
        assert row.index > 0


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


@dataclasses.dataclass(frozen=True)
class SubRow:
    id: str
    label: str
    raw: int
    age_eq: str
    percentile: str
    scaled: int
    descriptive: str
    level: int


@dataclasses.dataclass(frozen=True)
class CompRow:
    id: str
    sum_scaled: int
    percentile: str
    descriptive: str
    level: int
    index: int


def process(
    age: time.Delta,
    raw: dict[str, int],
    asmt: datetime.date | None = None,
) -> tuple[table.Table[SubRow], table.Table[CompRow], str]:
    if asmt is None:
        asmt = datetime.date.today()

    ra, rs, sp = _load()

    tests = get_tests()

    def age_eq(k: str) -> str:
        row = _get_ra(ra, k, raw[k])
        return f"{row.age_eq_y};{row.age_eq_m}"

    def scaled(k: str) -> tuple[int, int, str, int]:
        row = _get_rs(rs, k, age, raw[k])
        return (row.percentile, row.scaled, *lvl_sca(row.scaled))

    sub_rows: list[SubRow] = []
    for k, v in tests.items():
        per, sca, desc, lvl = scaled(k)
        sub_rows.append(
            SubRow(
                id=k,
                label=v,
                raw=raw[k],
                age_eq=age_eq(k),
                percentile=str(per),
                scaled=sca,
                descriptive=desc,
                level=lvl,
            )
        )

    sub = table.Table(sub_rows)

    def get_sub_scaled(sid: str) -> int:
        return sub.filter(id=sid).item().scaled

    comps = [
        (
            "vmi",
            "Visual-Motor Integration",
            get_sub_scaled("eh") + get_sub_scaled("co"),
        ),
        (
            "mrvp",
            "Motor-reduced Visual Perception",
            get_sub_scaled("fg") + get_sub_scaled("vc") + get_sub_scaled("fc"),
        ),
        (
            "gvp",
            "General Visual Perception",
            sum(r.scaled for r in sub.rows),
        ),
    ]

    comp_rows: list[CompRow] = []
    for k, l, v in comps:
        row = _get_sp(sp, k, v)
        desc, lvl = lvl_idx(row.index)
        comp_rows.append(
            CompRow(
                id=l,
                sum_scaled=v,
                percentile=str(row.percentile),
                descriptive=desc,
                level=lvl,
                index=row.index,
            )
        )

    comp = table.Table(comp_rows)

    rep = report(asmt, sub, comp)

    sub = table.Table(
        [
            dataclasses.replace(
                r, age_eq=to_age(r.age_eq), percentile=to_pr(int(r.percentile))
            )
            for r in sub.rows
        ]
    )
    comp = table.Table(
        [dataclasses.replace(r, percentile=to_pr(int(r.percentile))) for r in comp.rows]
    )

    return sub, comp, rep


def report(
    asmt: datetime.date, sub: table.Table[SubRow], comp: table.Table[CompRow]
) -> str:
    rep = string.StrBuilder()

    rep.add_line(
        f"Developmental Test of Visual Perception (DTVP-3) - {time.format_date(asmt)}"
    )
    rep.add_line()

    for n, i in [
        ("Visuomotorische Integration", 0),
        ("Visuelle Wahrnehmung mit reduzierter motorischer Reaktion", 1),
        ("Globale visuelle Wahrnehmung", 2),
    ]:
        c = comp.rows[i]
        rep.add_line(
            f"{n}: PR {to_pr(int(c.percentile))} - {lvl_idx(c.index, True)[0]}"
        )

    rep.add_line()
    rep.add_line("Subtests:")

    for n, i in [
        ("Augen-Hand-Koordination", 0),
        ("Abzeichnen", 1),
        ("Figur-Grund", 2),
        ("Gesaltschliessen", 3),
        ("Formkonstanz", 4),
    ]:
        s = sub.rows[i]
        rep.add_line(f"{n}: {to_age(s.age_eq)} J ({lvl_sca(s.scaled, True)[0]})")

    return str(rep)
