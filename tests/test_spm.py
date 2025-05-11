import datetime

import polars as pl
import pytest

from reportus import spm


@pytest.mark.parametrize(("ver"), [1, 2])
def test_data(ver: spm.Version):
    spm.validate(ver)


@pytest.mark.parametrize(
    ("form", "ver", "raw", "ts"),
    [
        (
            "Classroom",
            1,
            {
                "soc": 27,
                "vis": 4,
                "hea": 15,
                "tou": 12,
                "t&s": 4,
                "bod": 10,
                "bal": 24,
                "pln": 28,
            },
            {
                "soc": 64,
                "vis": 40,
                "hea": 69,
                "tou": 63,
                "bod": 57,
                "bal": 72,
                "pln": 70,
                "st": 63,
            },
        ),
        (
            "Home",
            1,
            {
                "soc": 26,
                "vis": 14,
                "hea": 11,
                "tou": 18,
                "t&s": 8,
                "bod": 22,
                "bal": 18,
                "pln": 26,
            },
            {
                "soc": 66,
                "vis": 57,
                "hea": 59,
                "tou": 63,
                "bod": 67,
                "bal": 63,
                "pln": 72,
                "st": 63,
            },
        ),
        (
            "Home",
            2,
            {
                "soc": 26,
                "vis": 14,
                "hea": 11,
                "tou": 18,
                "t&s": 8,
                "bod": 22,
                "bal": 18,
                "pln": 26,
            },
            {
                "soc": 65,
                "vis": 55,
                "hea": 47,
                "tou": 63,
                "bod": 68,
                "bal": 66,
                "pln": 71,
                "st": 59,
            },
        ),
    ],
)
def test_spm(form: spm.Form, ver: spm.Version, raw: dict[str, int], ts: dict[str, int]):
    today = datetime.date.today()

    res, rep = spm.process(today, form, ver, "", "", raw)

    for i, t in ts.items():
        assert res.filter(pl.col("id") == i).select("t").item() == t

    assert len(rep) > 0
