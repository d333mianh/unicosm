"""Daily transits to the natal chart (Western).

Where the sky is *now* relative to your fixed chart: transiting planets making
major aspects to natal points, with applying/separating motion. The Moon line is
today's mood; the slow-planet lines are the active life-transits.
"""

from __future__ import annotations

import swisseph as swe

from ..core import astro, ephem
from ..models import Cadence, Layer, SystemReading

# Transiting bodies (incl. outer planets) and a significance weight (higher =
# slower/rarer = more significant for a life-transit).
TRANSIT_BODIES = {
    "Moon": (swe.MOON, 0), "Sun": (swe.SUN, 2), "Mercury": (swe.MERCURY, 1),
    "Venus": (swe.VENUS, 1), "Mars": (swe.MARS, 3), "Jupiter": (swe.JUPITER, 5),
    "Saturn": (swe.SATURN, 6), "Uranus": (swe.URANUS, 7),
    "Neptune": (swe.NEPTUNE, 7), "Pluto": (swe.PLUTO, 7),
}

TRANSIT_ORB = 3.0
MOON_ORB = 5.0


def _exact_aspect(sep: float, orb_max: float):
    for exact, (name, glyph) in astro.ASPECTS.items():
        orb = abs(sep - exact)
        if orb <= orb_max:
            return exact, name, glyph, orb
    return None


def _phase(t_lon: float, speed: float, n_lon: float, exact: float) -> str:
    sep_now = astro.angle(t_lon, n_lon)
    sep_next = astro.angle((t_lon + speed * 0.5) % 360, n_lon)
    return "applying" if abs(sep_next - exact) < abs(sep_now - exact) else "separating"


def reading(ctx) -> SystemReading:
    n = ctx.natal
    targets = {**n.planets, "Asc": n.asc, "MC": n.mc}

    slow: list[dict] = []
    moon: list[dict] = []
    for tname, (ipl, weight) in TRANSIT_BODIES.items():
        t_lon, speed = ephem.planet_lon(ctx.jd_now, ipl)
        orb_max = MOON_ORB if tname == "Moon" else TRANSIT_ORB
        for nname, n_lon in targets.items():
            if tname == nname:
                continue
            hit = _exact_aspect(astro.angle(t_lon, n_lon), orb_max)
            if not hit:
                continue
            exact, name, glyph, orb = hit
            rec = {"t": tname, "glyph": glyph, "n": nname, "aspect": name,
                   "orb": round(orb, 1), "weight": weight,
                   "phase": _phase(t_lon, speed, n_lon, exact)}
            (moon if tname == "Moon" else slow).append(rec)

    slow.sort(key=lambda x: (-x["weight"], x["orb"]))
    moon.sort(key=lambda x: x["orb"])

    lines = []
    for r in slow[:3]:
        lines.append(f"t.{r['t']} {r['glyph']} n.{r['n']} ({r['phase']}, {r['orb']}°)")
    if moon:
        m = moon[0]
        lines.append(f"Moon {m['glyph']} n.{m['n']} today")

    summary = ("Transits — " + "; ".join(lines) + "."
               if lines else "No tight transits to natal points right now.")
    return SystemReading(
        key="transits",
        title="Transits to natal",
        cadence=Cadence.DAILY,
        layer=Layer.PERSONAL,
        summary=summary,
        detail={
            "active": [f"t.{r['t']} {r['aspect']} n.{r['n']} "
                       f"({r['phase']}, orb {r['orb']}°)" for r in slow[:6]],
            "moon": [f"Moon {r['aspect']} n.{r['n']} (orb {r['orb']}°)" for r in moon[:3]],
        },
        keywords=["transit"],
    )
