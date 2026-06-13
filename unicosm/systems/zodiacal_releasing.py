"""Zodiacal Releasing — Hellenistic time-lords from the Lots.

From the Lot of Spirit (action/career), periods release sign by sign in
zodiacal order, each lasting its ruler's "Lesser Years". L1 counts in years,
L2 in months. We report the active L1 (the chapter) and L2 (the sub-period).

Conventions: 365.2425-day year, month = year/12. The advanced "loosing of the
bond" peak-jumps are not modeled in this pass — straight zodiacal progression.
"""

from __future__ import annotations

import swisseph as swe

from ..core import astro, ephem
from ..models import Cadence, Layer, SystemReading

PLANET_YEARS = {"Sun": 19, "Moon": 25, "Mercury": 20, "Venus": 8,
                "Mars": 15, "Jupiter": 12, "Saturn": 30}
YEAR_DAYS = 365.2425
MONTH_DAYS = YEAR_DAYS / 12

SIGN_THEME = {
    "Aries": "initiative and contest", "Taurus": "stability and resources",
    "Gemini": "learning and exchange", "Cancer": "home and feeling",
    "Leo": "leadership and creativity", "Virgo": "craft and analysis",
    "Libra": "relationship and balance", "Scorpio": "depth and transformation",
    "Sagittarius": "meaning and travel", "Capricorn": "ambition and structure",
    "Aquarius": "community and reform", "Pisces": "spirit and dissolution",
}


def _sign_years(sign: str) -> int:
    return PLANET_YEARS[astro.RULER[sign]]


def _jd_date(jd: float) -> str:
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def _active(start_idx: int, start_jd: float, unit_days: float, target_jd: float):
    """Walk sign periods (zodiacal) from start until the one containing target."""
    cur = start_jd
    idx = start_idx
    for _ in range(2000):
        sign = ephem.SIGNS[idx % 12]
        end = cur + _sign_years(sign) * unit_days
        if cur <= target_jd < end:
            return sign, cur, end
        cur, idx = end, idx + 1
    sign = ephem.SIGNS[start_idx % 12]
    return sign, start_jd, start_jd + _sign_years(sign) * unit_days


def reading(ctx) -> SystemReading:
    n = ctx.natal
    sun, moon, asc = n.planets["Sun"], n.planets["Moon"], n.asc
    is_day = n.house_of(sun) in (7, 8, 9, 10, 11, 12)
    if is_day:
        fortune = (asc + moon - sun) % 360
        spirit = (asc + sun - moon) % 360
    else:
        fortune = (asc + sun - moon) % 360
        spirit = (asc + moon - sun) % 360

    spirit_sign = ephem.sign_name(spirit)
    l1_sign, l1_start, l1_end = _active(ephem.sign_index(spirit), n.jd,
                                        YEAR_DAYS, ctx.jd_now)
    l2_sign, l2_start, l2_end = _active(ephem.SIGNS.index(l1_sign), l1_start,
                                        MONTH_DAYS, ctx.jd_now)

    return SystemReading(
        key="zodiacal_releasing",
        title="Zodiacal Releasing (Spirit)",
        cadence=Cadence.DECADE,
        layer=Layer.PERSONAL,
        summary=(
            f"ZR L1 {l1_sign} ({_jd_date(l1_start)}→{_jd_date(l1_end)}) — a chapter "
            f"of {SIGN_THEME[l1_sign]}; L2 {l2_sign} until {_jd_date(l2_end)}. "
            f"(Spirit in {spirit_sign}, sect {'day' if is_day else 'night'}.)"
        ),
        detail={
            "sect": "day" if is_day else "night",
            "lot_of_spirit": ephem.fmt_pos(spirit),
            "lot_of_fortune": ephem.fmt_pos(fortune),
            "L1": f"{l1_sign} ({_jd_date(l1_start)}→{_jd_date(l1_end)})",
            "L2": f"{l2_sign} (until {_jd_date(l2_end)})",
        },
        keywords=[SIGN_THEME[l1_sign].split(" and ")[0]],
    )
