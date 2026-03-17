import dataclasses
import datetime
import itertools
from typing import Literal

from src import string, table, time

Form = Literal["Classroom", "Home"]
Version = Literal[1, 2]


def forms(ver: Version) -> list[Form]:
    if ver == 1:
        return ["Classroom", "Home"]
    return ["Home"]


@dataclasses.dataclass(frozen=True)
class Filer:
    prep: str | None
    name: str


def filers(form: Form) -> list[Filer]:
    if form == "Classroom":
        return [
            Filer("der", "LP"),
            Filer("der", "BP"),
        ]
    return [
        Filer("der", "Mutter"),
        Filer(None, "Vater"),
        Filer("den", "Eltern"),
    ]


def get_scores() -> dict[str, str]:
    return {
        "vis": "Vision",
        "hea": "Hearing",
        "tou": "Touch",
        "t&s": "Taste and Smell",
        "bod": "Body Awareness",
        "bal": "Balance and Motion",
        "pln": "Planning and Ideas",
        "soc": "Social",
    }


@dataclasses.dataclass(frozen=True)
class CsvRow:
    id: str
    raw_min: int
    raw_max: float
    percentile: int
    t: int
    type: str


def _load() -> table.Table[CsvRow]:
    classroom = table.read_csv("public/spm-classroom.csv", CsvRow)
    home = table.read_csv("public/spm-home.csv", CsvRow)
    home2 = table.read_csv("public/spm2-home.csv", CsvRow)
    return classroom.concat(home).concat(home2)


def _get_row(data: table.Table[CsvRow], form: str, i: str, r: int) -> CsvRow:
    return data.filter(
        type=form,
        id=i,
        raw_min=lambda v: v <= r,
        raw_max=lambda v: v >= r,
    ).item()


def validate(ver: Version):
    data = _load()
    types = ["classroom", "home"] if ver == 1 else ["home"]
    ids = list(get_scores().keys())
    if ver == 1:
        ids.remove("t&s")
    ids.append("st")
    raws = range(0, 171)

    for t, i, r in itertools.product(types, ids, raws):
        row = _get_row(data, t + str(ver), i, r)
        assert row.percentile > 0
        assert row.t > 0


typical = "Typical"


@dataclasses.dataclass(frozen=True)
class ResultRow:
    id: str
    raw: int
    t: int | None
    percentile: str | None
    interpretive: str | None
    level: int | None


def _report(
    asmt: datetime.date,
    form: Form,
    filer: Filer,
    name: str | None,
    ver: Version,
    res: table.Table[ResultRow],
) -> str:
    asmt_fmt = time.format_date(asmt, False)
    spm = f"SPM {ver}"
    rep = string.StrBuilder()
    fil = filer.name if filer.prep is None else f"{filer.prep} {filer.name}"
    if form == "Classroom":
        rep.add_line(f"Sensory Processing Measure ({spm}): Classroom Form")
        rep.add_line(
            f"Fragebogen zur sensorischen Verarbeitung ausgefüllt von {fil} des Kindes ({asmt_fmt})"
        )
    else:
        rep.add_line(f"Sensory Processing Measure ({spm}): Home Form")
        rep.add_line(
            f"Elternfragebogen zur sensorischen Verarbeitung ausgefüllt von {fil} des Kindes ({asmt_fmt})"
        )
        rep.add_line(
            "Die Fähigkeit, sensorische Reize zu verarbeiten, beeinflusst die motorischen und selbstregulativen Fähigkeiten eines Kindes sowie sein soziales Verhalten."
        )

    scores = [
        None,
        ("vis", "Vision"),
        ("hea", "Hearing"),
        ("tou", "Touch"),
        ("bod", "Body Awareness"),
        ("bal", "Balance and Motion"),
        None,
        ("st", "Gesamttestwert"),
        None,
        ("pln", "Planning and Ideas"),
        ("soc", "Social"),
    ]

    if ver == 2:
        scores.insert(4, ("t&s", "Taste and Smell"))

    def get_int(s: str) -> str | None:
        return res.filter(id=s).item().interpretive

    for s in scores:
        if not s:
            rep.add_line()
            continue
        rep.add_line(
            f'{s[1]}: PR {res.filter(id=s[0]).item().percentile} - "{get_int(s[0])}"'
        )

    if ver == 2:
        rep.add_line()
        if get_int("st") == typical:
            rep.add_line(
                f'{name} sensorisches Profil liegt im Bereich "Typical" und ist somit unauffällig.'
            )
        else:
            rep.add_line("Zusammenfassung der sensorischen Verarbeitung des Kindes:")
            rep.add_line()
            rep.add_line(
                f'{name} sensorisches Profil liegt im Bereich "Moderate Difficulties" (Gesamttestwert). Es zeigen sich Auffälligkeiten in mehreren sensorischen Systemen, welche sich in folgenden beobachtbaren Verhaltensweisen widerspiegeln:',
            )
            rep.add_line()
            scores = [
                ("Sehen", "vis"),
                ("Hören", "hea"),
                ("Tasten", "tou"),
                ("Geschmack und Geruch", "t&s"),
                ("Körperwahrnehmung (Propriozeptive Wahrnehmung)", "bod"),
                ("Gleichgewicht (Vestibulär Wahrnehmung)", "bal"),
            ]

            def summary_score(k: str) -> str:
                return "unauffällig" if get_int(k) == typical else ""

            for l, k in scores:
                rep.add_line(f"{l}: {summary_score(k)}")

            if get_int("pln") != typical or get_int("soc") != typical:
                rep.add_line()
                rep.add_line("Auswirkungen auf den Alltag:")
                rep.add_line()
                rep.add_line("Planung und Ideenfindung: " + summary_score("pln"))
                rep.add_line("Soziale Teilhabe: " + summary_score("soc"))

    return str(rep)


def process(
    asmt: datetime.date,
    form: Form,
    ver: Version,
    filer: Filer,
    name: str | None,
    raw: dict[str, int],
) -> tuple[table.Table[ResultRow], str]:
    data = _load()

    def ver1():
        return ver == 1

    raw["st"] = sum(
        [raw["vis"], raw["hea"], raw["tou"], raw["t&s"], raw["bod"], raw["bal"]]
    )

    def per(p: int) -> str:
        if p == 100:
            return ">99"
        return str(p)

    def inter(t: int) -> tuple[str, int]:
        if t < 60:
            return (typical, 0)
        if t < 70:
            return ("Some Problems" if ver1() else "Moderate Difficulties", 1)
        return ("Definite Dysfunction" if ver1() else "Severe Difficulties", 2)

    def form_row(i: str, r: int) -> ResultRow:
        if ver1() and i == "t&s":
            return ResultRow(
                id="t&s", raw=r, t=None, percentile=None, interpretive=None, level=None
            )
        key = f"{form.lower()}{ver}"
        row = _get_row(data, key, i, r)
        t_val = row.t
        interpretive, level = inter(t_val)
        return ResultRow(
            id=i,
            raw=r,
            t=t_val,
            percentile=per(row.percentile),
            interpretive=interpretive,
            level=level,
        )

    res = table.from_list([form_row(i, r) for i, r in raw.items()])

    return res, _report(asmt, form, filer, name, ver, res)
