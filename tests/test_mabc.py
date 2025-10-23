import polars as pl
import pytest

from reportus import mabc
from reportus.time import Delta


def test_data():
    mabc.validate()


@pytest.mark.parametrize(
    ("age", "raw", "comp_res", "agg_res"),
    [
        (
            Delta(years=6),
            {
                "hg11": 17,
                "hg12": 29,
                "hg2": None,
                "hg3": 0,
                "bf1": 4,
                "bf2": 0,
                "bl11": 9,
                "bl12": 7,
                "bl2": 20,
                "bl3": 1,
            },
            {
                "bf1": 5,
                "bf2": 1,
                "bl1": 7,
                "bl11": 6,
                "bl12": 8,
                "bl2": 11,
                "bl3": 1,
                "hg1": 6,
                "hg11": 11,
                "hg12": 1,
                "hg2": 1,
                "hg3": 11,
            },
            {
                "bf": 1,
                "bl": 6,
                "hg": 5,
                "total": 3,
            },
        ),
        (
            Delta(years=9),
            {
                "hg11": 28,
                "hg12": 25,
                "hg2": 25,
                "hg3": 1,
                "bf1": 9,
                "bf2": 7,
                "bl11": 30,
                "bl12": 9,
                "bl2": 7,
                "bl31": 5,
                "bl32": 4,
            },
            {
                "bf1": 12,
                "bf2": 11,
                "bl1": 12,
                "bl11": 13,
                "bl12": 10,
                "bl2": 1,
                "bl3": 8,
                "bl31": 11,
                "bl32": 6,
                "hg1": 11,
                "hg11": 8,
                "hg12": 14,
                "hg2": 9,
                "hg3": 6,
            },
            {
                "bf": 12,
                "bl": 6,
                "hg": 9,
                "total": 8,
            },
        ),
        (
            Delta(years=12),
            {
                "hg11": 17,
                "hg12": 23,
                "hg2": 36,
                "hg3": 4,
                "bf11": 6,
                "bf12": 5,
                "bf2": 9,
                "bl1": 18,
                "bl2": 13,
                "bl31": 4,
                "bl32": 3,
            },
            {
                "bf1": 8,
                "bf11": 7,
                "bf12": 9,
                "bf2": 16,
                "bl1": 9,
                "bl2": 11,
                "bl3": 2,
                "bl31": 1,
                "bl32": 3,
                "hg1": 9,
                "hg11": 11,
                "hg12": 8,
                "hg2": 10,
                "hg3": 6,
            },
            {
                "bf": 13,
                "bl": 6,
                "hg": 8,
                "total": 8,
            },
        ),
    ],
)
def test_mabc(
    age: Delta,
    raw: dict[str, int | None],
    comp_res: dict[str, int],
    agg_res: dict[str, int],
):
    comp, agg, rep = mabc.process(age, raw)

    for k, v in comp_res.items():
        assert comp.filter(pl.col("id") == k).select("standard").item() == v

    for k, v in agg_res.items():
        assert agg.filter(pl.col("id") == k).select("standard").item() == v

    assert len(rep) > 0
