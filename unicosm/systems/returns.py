"""Solar & lunar return charts.

The solar return (Sun back to its natal degree, ~yearly) sets the tone of the
year; the lunar return (Moon back to its natal degree, ~monthly) sets the tone
of the lunar month. The return chart's rising sign is the headline.
"""

from __future__ import annotations

import swisseph as swe

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

RISING_FLAVOR = {
    "Aries": "assertive, fast starts", "Taurus": "steady, building",
    "Gemini": "curious, communicative", "Cancer": "tender, home-focused",
    "Leo": "expressive, visible", "Virgo": "precise, improving",
    "Libra": "relational, balancing", "Scorpio": "intense, transformative",
    "Sagittarius": "expansive, adventurous", "Capricorn": "ambitious, disciplined",
    "Aquarius": "independent, future-facing", "Pisces": "dreamy, compassionate",
}


def _jd_date(jd: float) -> str:
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def _last_return(target: float, now_jd: float, ipl: int, speed: float) -> float:
    """Most recent jd <= now where the body was at the target longitude."""
    lon_now = ephem.planet_lon(now_jd, ipl)[0]
    deg_since = (lon_now - target) % 360
    g = now_jd - deg_since / speed
    for _ in range(10):
        diff = ((ephem.planet_lon(g, ipl)[0] - target + 180) % 360) - 180
        g -= diff / speed
    return g


def solar_return(ctx) -> SystemReading:
    natal_sun = ctx.natal.planets["Sun"]
    sr_jd = _last_return(natal_sun, ctx.jd_now, ephem.PLANETS["Sun"], 0.9856)
    asc = ephem.ascendant(sr_jd, ctx.lat, ctx.lon)
    asc_sign = ephem.sign_name(asc)
    sr_moon = ephem.sign_name(ephem.planet_lon(sr_jd, ephem.PLANETS["Moon"])[0])
    return SystemReading(
        key="solar_return",
        title="Solar return",
        cadence=Cadence.YEAR,
        layer=Layer.PERSONAL,
        summary=(
            f"Solar return {_jd_date(sr_jd)}: rising {asc_sign} "
            f"({RISING_FLAVOR[asc_sign]}), SR Moon in {sr_moon} — the keynote "
            f"of your current solar year."
        ),
        detail={"date": _jd_date(sr_jd), "ascendant": ephem.fmt_pos(asc),
                "moon_sign": sr_moon},
        keywords=[RISING_FLAVOR[asc_sign].split(",")[0]],
    )


def lunar_return(ctx) -> SystemReading:
    natal_moon = ctx.natal.planets["Moon"]
    lr_jd = _last_return(natal_moon, ctx.jd_now, ephem.PLANETS["Moon"], 13.176)
    asc = ephem.ascendant(lr_jd, ctx.lat, ctx.lon)
    asc_sign = ephem.sign_name(asc)
    return SystemReading(
        key="lunar_return",
        title="Lunar return",
        cadence=Cadence.LUNAR_MONTH,
        layer=Layer.PERSONAL,
        summary=(
            f"Lunar return {_jd_date(lr_jd)}: rising {asc_sign} "
            f"({RISING_FLAVOR[asc_sign]}) — the tone of this lunar month for you."
        ),
        detail={"date": _jd_date(lr_jd), "ascendant": ephem.fmt_pos(asc)},
        keywords=[RISING_FLAVOR[asc_sign].split(",")[0]],
    )
