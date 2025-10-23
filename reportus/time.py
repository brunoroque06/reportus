import dataclasses
import datetime

from dateutil.relativedelta import relativedelta


def format_date(d: datetime.date, inc_day: bool = True) -> str:
    if inc_day:
        return d.strftime("%d.%m.%Y")
    return d.strftime("%m.%Y")


@dataclasses.dataclass(frozen=True)
class Delta:
    years: int
    months: int = 0
    days: int = 0


def to_delta(start: datetime.date, end: datetime.date) -> Delta:
    delta = relativedelta(end, start)
    return Delta(delta.years, delta.months, delta.days)


def minus_delta(date: datetime.date, delta: Delta) -> datetime.date:
    rel = relativedelta(years=delta.years, months=delta.months, days=delta.days)
    return date - rel
