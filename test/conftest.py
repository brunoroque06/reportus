import datetime

import pytest

from src.time import format_date


@pytest.fixture
def date():
    d = datetime.date(year=2026, month=3, day=3)
    return d, format_date(d)
