import datetime

import pytest

from reportus.time import Delta, minus_delta, to_delta


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (
            datetime.date(year=2025, month=8, day=1),
            datetime.date(year=2025, month=10, day=19),
            Delta(0, 2, 18),
        ),
        (
            datetime.date(year=2024, month=8, day=1),
            datetime.date(year=2025, month=10, day=19),
            Delta(1, 2, 18),
        ),
        (
            datetime.date(year=2025, month=9, day=20),
            datetime.date(year=2025, month=10, day=19),
            Delta(0, 0, 29),
        ),
        (
            datetime.date(year=2024, month=9, day=20),
            datetime.date(year=2025, month=10, day=19),
            Delta(1, 0, 29),
        ),
        (
            datetime.date(year=2024, month=12, day=1),
            datetime.date(year=2025, month=10, day=19),
            Delta(0, 10, 18),
        ),
        (
            datetime.date(year=2024, month=12, day=20),
            datetime.date(year=2025, month=10, day=19),
            Delta(0, 9, 29),
        ),
        (
            datetime.date(year=2022, month=10, day=19),
            datetime.date(year=2025, month=10, day=19),
            Delta(3, 0),
        ),
    ],
)
def test_to_delta(start: datetime.date, end: datetime.date, expected: Delta):
    assert to_delta(start, end) == expected


@pytest.mark.parametrize(
    "date,delta,expected",
    [
        (
            datetime.date(year=2023, month=3, day=1),
            Delta(years=1, months=1, days=1),
            datetime.date(year=2022, month=1, day=31),
        ),
        (
            datetime.date(year=2019, month=1, day=1),
            Delta(years=-1),
            datetime.date(year=2020, month=1, day=1),
        ),
    ],
)
def test_minus_delta(date: datetime.date, delta: Delta, expected: datetime.date):
    assert minus_delta(date, delta) == expected
