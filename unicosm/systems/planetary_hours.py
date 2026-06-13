"""Planetary hours — the hourly layer (Western/Hellenistic).

The day (sunrise→sunset) and night (sunset→sunrise) are each split into 12
unequal hours. The first hour after sunrise is ruled by the planet of the
weekday; subsequent hours follow the Chaldean order.
"""

from __future__ import annotations

from datetime import timedelta

from ..core import ephem
from ..core.timeutil import local_midnight
from ..models import Cadence, Layer, SystemReading

CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Python weekday(): Monday=0 .. Sunday=6
DAY_RULER = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
             4: "Venus", 5: "Saturn", 6: "Sun"}

PLANET_KW = {
    "Saturn": ["structure", "discipline", "endings"],
    "Jupiter": ["growth", "opportunity", "generosity"],
    "Mars": ["action", "courage", "drive"],
    "Sun": ["vitality", "leadership", "visibility"],
    "Venus": ["love", "art", "harmony"],
    "Mercury": ["communication", "learning", "trade"],
    "Moon": ["feeling", "home", "flow"],
}

PLANET_TONE = {"Jupiter": 0.6, "Venus": 0.5, "Sun": 0.2, "Mercury": 0.1,
               "Moon": 0.1, "Mars": -0.3, "Saturn": -0.4}


def reading(ctx) -> SystemReading | None:
    lat, lon, tz = ctx.lat, ctx.lon, ctx.cur_tz
    jd0 = ephem.jd_ut(local_midnight(ctx.now))
    jd_now = ctx.jd_now

    sunrise = ephem.next_sunrise(jd0, lat, lon)
    sunset = ephem.next_sunset(jd0, lat, lon)
    if sunrise is None or sunset is None:
        return SystemReading(
            key="planetary_hours", title="Planetary hour",
            cadence=Cadence.HOURLY, layer=Layer.COSMIC,
            summary="No planetary hours today (polar day or night).",
            detail={"note": "circumpolar"}, keywords=[],
        )

    if jd_now < sunrise:
        # night before today's sunrise -> began at yesterday's sunset
        prev = ephem.next_sunset(jd0 - 1, lat, lon)
        start_jd, end_jd, offset = prev, sunrise, 12
        ruler_wd = (ctx.now.date() - timedelta(days=1)).weekday()
    elif jd_now < sunset:
        start_jd, end_jd, offset = sunrise, sunset, 0
        ruler_wd = ctx.now.date().weekday()
    else:
        nxt = ephem.next_sunrise(jd0 + 1, lat, lon)
        start_jd, end_jd, offset = sunset, nxt, 12
        ruler_wd = ctx.now.date().weekday()

    seg_len = (end_jd - start_jd) / 12
    seg = min(int((jd_now - start_jd) / seg_len), 11)
    hour_no = offset + seg + 1
    start_idx = CHALDEAN.index(DAY_RULER[ruler_wd])
    ruler = CHALDEAN[(start_idx + offset + seg) % 7]

    h_start = ephem.jd_to_datetime(start_jd + seg * seg_len, tz)
    h_end = ephem.jd_to_datetime(start_jd + (seg + 1) * seg_len, tz)
    kw = PLANET_KW[ruler]
    return SystemReading(
        key="planetary_hours",
        title="Planetary hour",
        cadence=Cadence.HOURLY,
        layer=Layer.COSMIC,
        summary=(
            f"Hour of {ruler} ({h_start:%H:%M}–{h_end:%H:%M}) — "
            f"favors {kw[0]} and {kw[1]}."
        ),
        detail={
            "ruler": ruler,
            "hour_number": hour_no,
            "phase": "day" if offset == 0 else "night",
            "from": h_start.strftime("%H:%M"),
            "to": h_end.strftime("%H:%M"),
        },
        keywords=kw,
        score=PLANET_TONE[ruler],
    )
