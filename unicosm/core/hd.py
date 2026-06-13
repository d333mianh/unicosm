"""Human Design calculation core.

Maps ecliptic longitudes to gate/line on the Rave Mandala, finds the Design
moment (Sun 88° of arc before birth), and computes the 13 body activations for
either side (Personality = birth, Design = 88° prior).
"""

from __future__ import annotations

import swisseph as swe

from ..data.human_design import GATE_ARC, GATE_WHEEL, LINE_ARC, WHEEL_START_DEG
from . import ephem

# (label, swe id or None for derived). Order follows the standard HD listing.
HD_BODIES: list[tuple[str, int | None]] = [
    ("Sun", swe.SUN),
    ("Earth", None),            # Sun + 180°
    ("North Node", swe.TRUE_NODE),
    ("South Node", None),       # North Node + 180°
    ("Moon", swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS),
    ("Mars", swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN),
    ("Uranus", swe.URANUS),
    ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO),
]

_SUN_SPEED = 0.9856  # mean deg/day


def gate_line(lon: float) -> tuple[int, int]:
    """Ecliptic longitude (deg) -> (gate 1-64, line 1-6)."""
    off = (lon - WHEEL_START_DEG) % 360.0
    i = int(off // GATE_ARC)
    gate = GATE_WHEEL[i]
    within = off - i * GATE_ARC
    line = int(within // LINE_ARC) + 1
    return gate, line


def _lon(jd: float, ipl: int) -> float:
    return ephem.planet_lon(jd, ipl)[0]


def design_jd(birth_jd: float) -> float:
    """Julian Day when the Sun was 88° of arc before its birth longitude."""
    target = (_lon(birth_jd, swe.SUN) - 88.0) % 360.0
    g = birth_jd - 88.0
    for _ in range(12):
        diff = ((_lon(g, swe.SUN) - target + 180) % 360) - 180
        g -= diff / _SUN_SPEED
    return g


def activations(jd: float) -> dict[str, tuple[float, int, int]]:
    """body -> (longitude, gate, line) for all 13 HD bodies at jd."""
    sun = _lon(jd, swe.SUN)
    north = _lon(jd, swe.TRUE_NODE)
    out: dict[str, tuple[float, int, int]] = {}
    for name, ipl in HD_BODIES:
        if name == "Earth":
            lon = (sun + 180) % 360
        elif name == "South Node":
            lon = (north + 180) % 360
        else:
            lon = _lon(jd, ipl)
        out[name] = (lon, *gate_line(lon))
    return out
