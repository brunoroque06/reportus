import calendar
import dataclasses
import datetime


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


def minus_delta(date: datetime.date, delta: Delta) -> datetime.date:
    total_months = (date.year * 12 + date.month - 1) - (delta.years * 12 + delta.months)
    year, month = divmod(total_months, 12)
    month += 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day) - datetime.timedelta(days=delta.days)
