import calendar
from dataclasses import dataclass
from datetime import date, timedelta


def format_date(dat: date, day: bool = True) -> str:
    return dat.strftime("%d.%m.%Y" if day else "%m.%Y")


@dataclass(frozen=True)
class Delta:
    years: int
    months: int = 0
    days: int = 0


def to_delta(start: date, end: date) -> Delta:
    year, month, day = end.year, end.month, end.day

    if day < start.day:
        month -= 1
        if month == 0:
            month = 12
            year -= 1
        day += calendar.monthrange(year, month)[1]

    if month < start.month:
        year -= 1
        month += 12

    return Delta(year - start.year, month - start.month, day - start.day)


def minus_delta(start: date, delta: Delta) -> date:
    total_months = (start.year * 12 + start.month - 1) - (
        delta.years * 12 + delta.months
    )
    year, month = divmod(total_months, 12)
    month += 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day) - timedelta(days=delta.days)
