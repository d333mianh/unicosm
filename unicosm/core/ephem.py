"""Swiss Ephemeris wrapper.

We use the Moshier ephemeris (FLG_MOSEPH) so no external data files are needed
— accurate to a few arcseconds over the historical range, which is far beyond
what any of these traditions require.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import swisseph as swe

_CALC_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
_RISE_FLAGS = swe.FLG_MOSEPH

# Planet identifiers used across the engine.
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_GLYPH = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒",
    "Pisces": "♓",
}


def jd_ut(dt: datetime) -> float:
    """Julian Day (UT) for a timezone-aware datetime."""
    u = dt.astimezone(timezone.utc)
    hour = u.hour + u.minute / 60 + u.second / 3600 + u.microsecond / 3.6e9
    return swe.julday(u.year, u.month, u.day, hour, swe.GREG_CAL)


def jdn_noon(year: int, month: int, day: int) -> int:
    """Integer Julian Day Number at noon of a Gregorian civil date.

    Used by the sexagenary day-pillar formula (verified against
    2019-01-27 -> jiazi).
    """
    return int(swe.julday(year, month, day, 12.0, swe.GREG_CAL))


def planet_lon(jd: float, ipl: int) -> tuple[float, float]:
    """Tropical ecliptic longitude (deg) and longitude speed (deg/day)."""
    xx, _ = swe.calc_ut(jd, ipl, _CALC_FLAGS)
    return xx[0] % 360.0, xx[3]


def ascendant(jd: float, lat: float, lon: float) -> float:
    """Tropical Ascendant longitude (deg). Placidus houses."""
    _cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    return ascmc[0] % 360.0


def houses(jd: float, lat: float, lon: float) -> tuple[tuple[float, ...], float, float]:
    """(12 house cusps, Ascendant, Midheaven), all tropical degrees. Placidus."""
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    return tuple(c % 360.0 for c in cusps[:12]), ascmc[0] % 360.0, ascmc[1] % 360.0


def ayanamsa(jd: float) -> float:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa_ut(jd)


# ---- zodiac helpers -----------------------------------------------------

def sign_index(lon: float) -> int:
    return int(lon % 360 // 30)


def sign_name(lon: float) -> str:
    return SIGNS[sign_index(lon)]


def deg_in_sign(lon: float) -> float:
    return lon % 30.0


def fmt_pos(lon: float) -> str:
    s = sign_name(lon)
    d = deg_in_sign(lon)
    return f"{int(d)}°{SIGN_GLYPH[s]} {s}"


# ---- lunar phase --------------------------------------------------------

PHASE_NAMES = [
    "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
    "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
]


def moon_phase(jd: float) -> dict:
    sun, _ = planet_lon(jd, swe.SUN)
    moon, _ = planet_lon(jd, swe.MOON)
    elong = (moon - sun) % 360.0
    illum = (1 - math.cos(math.radians(elong))) / 2
    idx = int((elong + 22.5) // 45) % 8
    return {
        "elongation": elong,
        "illumination": illum,
        "phase_index": idx,
        "phase_name": PHASE_NAMES[idx],
        "waxing": elong < 180.0,
        "sun_lon": sun,
        "moon_lon": moon,
    }


# ---- rise / set ---------------------------------------------------------

def _rise_or_set(jd_start: float, lat: float, lon: float, rising: bool) -> float | None:
    flag = swe.CALC_RISE if rising else swe.CALC_SET
    res, tret = swe.rise_trans(jd_start, swe.SUN, flag, (lon, lat, 0.0), 0.0, 0.0, _RISE_FLAGS)
    if res < 0:
        return None  # circumpolar: sun does not rise/set that day
    return tret[0]


def next_sunrise(jd_start: float, lat: float, lon: float) -> float | None:
    return _rise_or_set(jd_start, lat, lon, rising=True)


def next_sunset(jd_start: float, lat: float, lon: float) -> float | None:
    return _rise_or_set(jd_start, lat, lon, rising=False)


def jd_to_datetime(jd: float, tz) -> datetime:
    """Convert a UT Julian Day back to an aware datetime in tz."""
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int(round((((h - hh) * 60) - mm) * 60))
    # normalize seconds overflow
    base = datetime(y, m, d, hh, mm, 0, tzinfo=timezone.utc)
    from datetime import timedelta
    base = base + timedelta(seconds=ss)
    return base.astimezone(tz)
