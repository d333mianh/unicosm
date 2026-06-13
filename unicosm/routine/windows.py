"""Day windows — named time-blocks the user can anchor habits to.

Some windows are astronomical (brahma muhurta, sunrise), some are clock-based
and aligned to the TCM organ clock. Each resolves to a concrete span for the
current day. This is the stable scaffold; the cosmic 'accents' are layered on
by the synthesis layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..core import ephem
from ..core.timeutil import local_midnight


@dataclass(frozen=True)
class Window:
    key: str
    label: str
    note: str


# Definitions in natural day order. Spans are computed in day_windows().
WINDOWS: list[Window] = [
    Window("brahma_muhurta", "Brahma muhurta", "meditation, prayer, inner practice"),
    Window("sunrise", "Sunrise", "movement, sunlight, breath"),
    Window("morning", "Morning focus", "deep work, study (Spleen qi peaks)"),
    Window("midday", "Midday", "connection, the main meal, lighter work (Heart)"),
    Window("afternoon", "Afternoon", "decisions, errands, output"),
    Window("evening", "Evening", "restore, light dinner, gentle movement (Kidney)"),
    Window("wind_down", "Wind-down", "settle, screens off, prepare for sleep"),
    Window("anytime", "Anytime", "flexible — fit it where it lands"),
]

WINDOWS_BY_KEY = {w.key: w for w in WINDOWS}


def _clock(date0: datetime, h1: int, h2: int) -> tuple[datetime, datetime]:
    return (date0.replace(hour=h1), date0.replace(hour=h2))


def day_windows(ctx) -> list[tuple[Window, datetime | None, datetime | None]]:
    """Resolve every window to (start, end) for ctx's day. Sun windows may be
    None at extreme latitudes when there is no sunrise/sunset."""
    tz = ctx.cur_tz
    date0 = local_midnight(ctx.now)
    jd0 = ephem.jd_ut(date0)

    sr = ephem.next_sunrise(jd0, ctx.lat, ctx.lon)
    ss = ephem.next_sunset(jd0, ctx.lat, ctx.lon)
    sunrise = ephem.jd_to_datetime(sr, tz) if sr else None
    sunset = ephem.jd_to_datetime(ss, tz) if ss else None
    end_of_day = date0 + timedelta(days=1)

    spans: dict[str, tuple[datetime | None, datetime | None]] = {}
    if sunrise:
        spans["brahma_muhurta"] = (sunrise - timedelta(minutes=96),
                                   sunrise - timedelta(minutes=48))
        spans["sunrise"] = (sunrise - timedelta(minutes=15),
                            sunrise + timedelta(minutes=45))
    else:
        spans["brahma_muhurta"] = (None, None)
        spans["sunrise"] = (None, None)
    spans["morning"] = _clock(date0, 9, 11)
    spans["midday"] = _clock(date0, 11, 13)
    spans["afternoon"] = _clock(date0, 13, 17)
    spans["evening"] = _clock(date0, 17, 19)
    spans["wind_down"] = _clock(date0, 21, 23)
    spans["anytime"] = (date0, end_of_day)

    return [(w, spans[w.key][0], spans[w.key][1]) for w in WINDOWS]
