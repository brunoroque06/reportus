import dataclasses
import datetime
import itertools
from typing import Literal

import polars as pl

from reportus import perf, str_builder, time

Form = Literal["Classroom", "Home"]
Version = Literal[1, 2]


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
class Data:
    data: pl.DataFrame

    def get_row(self, form: str, i: str, r: int):
        return self.data.filter(
            (pl.col("type") == form)
            & (pl.col("id") == i)
            & (pl.col("raw_min") <= r)
            & (pl.col("raw_max") >= r)
        )


@perf.cache
def _load() -> Data:
    classroom = pl.read_csv("data/spm-classroom.csv")
    classroom = classroom.with_columns(pl.lit("classroom1").alias("type"))

    home = pl.read_csv("data/spm-home.csv")
    home = home.with_columns(pl.lit("home1").alias("type"))

    home2 = pl.read_csv("data/spm2-home.csv")
    home2 = home2.with_columns(pl.lit("home2").alias("type"))

    return Data(pl.concat([classroom, home, home2]))


def validate(ver: Version):
    data = _load()
    types = ["classroom", "home"] if ver == 1 else ["home"]
    ids = list(get_scores().keys())
    if ver == 1:
        ids.remove("t&s")
    ids.append("st")
    raws = range(0, 171)

    for t, i, r in itertools.product(types, ids, raws):
        row = data.get_row(t + str(ver), i, r)
        assert row.is_empty() is False
        for c in ["percentile", "t"]:
            assert row.select(c).item() > 0


typical = "Typical"


def _report(
    asmt: datetime.date,
    form: Form,
    filled: str,
    name: str | None,
    ver: Version,
    res: pl.DataFrame,
) -> str:
    asmt_fmt = time.format_date(asmt, False)
    spm = f"SPM {ver}"
    rep = str_builder.StrBuilder()
    if form == "Classroom":
        rep.append(f"Sensory Processing Measure ({spm}): Classroom Form")
        rep.append(
            f"Fragebogen zur sensorischen Verarbeitung ausgefüllt von {filled} des Kindes ({asmt_fmt})"
        )
    else:
        rep.append(f"Sensory Processing Measure ({spm}): Home Form")
        rep.append(
            f"Elternfragebogen zur sensorischen Verarbeitung ausgefüllt von {filled} des Kindes ({asmt_fmt})"
        )
        rep.append(
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

    def get_int(s: str) -> str:
        return res.filter(pl.col("id") == s).select("interpretive").item()

    for s in scores:
        if not s:
            rep.append()
            continue
        rep.append(
            f'{s[1]}: PR {res.filter(pl.col("id") == s[0]).select("percentile").item()} - "{get_int(s[0])}"'
        )

    if ver == 2:
        rep.append()
        if get_int("st") == typical:
            rep.append(
                f'{name} sensorisches Profil liegt im Bereich "Typical" und ist somit unauffällig.'
            )
        else:
            rep.append("Zusammenfassung der sensorischen Verarbeitung des Kindes:")
            rep.append()
            rep.append(
                f'{name} sensorisches Profil liegt im Bereich "Moderate Difficulties" (Gesamttestwert). Es zeigen sich Auffälligkeiten in mehreren sensorischen Systemen, welche sich in folgenden beobachtbaren Verhaltensweisen widerspiegeln:',
            )
            rep.append()
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
                rep.append(f"{l}: {summary_score(k)}")

            if get_int("pln") != typical or get_int("soc") != typical:
                rep.append()
                rep.append("Auswirkungen auf den Alltag:")
                rep.append()
                rep.append("Planung und Ideenfindung: " + summary_score("pln"))
                rep.append("Soziale Teilhabe: " + summary_score("soc"))

    return str(rep)


def process(
    asmt: datetime.date,
    form: Form,
    ver: Version,
    filled: str,
    name: str | None,
    raw: dict[str, int],
) -> tuple[pl.DataFrame, str]:
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

    def form_row(i: str, r: int):
        if ver1() and i == "t&s":
            return ["t&s", r, None, None, None, None]
        key = f"{form.lower()}{ver}"
        row = data.get_row(key, i, r)
        return [
            i,
            r,
            row.select("t").item(),
            per(row.select("percentile").item()),
            *inter(row.select("t").item()),
        ]

    res = pl.DataFrame(
        [form_row(i, r) for i, r in raw.items()],
        orient="row",
        schema=["id", "raw", "t", "percentile", "interpretive", "level"],
    )

    return res, _report(asmt, form, filled, name, ver, res)
