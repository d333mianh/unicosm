"""Timezone and calendar helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def now_in(tz: str) -> datetime:
    return datetime.now(ZoneInfo(tz))


def in_tz(dt: datetime, tz: str) -> datetime:
    return dt.astimezone(ZoneInfo(tz))


def local_midnight(dt: datetime) -> datetime:
    """00:00 of the civil day containing `dt`, same timezone."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def civil_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def days_between_dates(a: datetime, b: datetime) -> int:
    """Whole civil days from a's date to b's date (b - a)."""
    return (b.date() - a.date()).days


def whole_years_since(birth: datetime, now: datetime) -> int:
    """Completed years lived (age in whole years), by civil date."""
    bd = birth.date()
    nd = now.date()
    years = nd.year - bd.year
    # subtract one if this year's birthday hasn't happened yet
    if (nd.month, nd.day) < (bd.month, bd.day):
        years -= 1
    return max(years, 0)


def add_minutes(dt: datetime, minutes: float) -> datetime:
    return dt + timedelta(minutes=minutes)
