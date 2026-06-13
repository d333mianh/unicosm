"""Secular sky readings.

mechanics — daily Western mechanics: retrograde planets and whether the Moon is
void-of-course (makes no further major aspect before leaving its sign).
sky_data — grounding astronomy: day length + the next solar & lunar eclipses.
"""

from __future__ import annotations

import swisseph as swe

from ..core import astro, ephem
from ..models import Cadence, Layer, SystemReading

RETRO_BODIES = {
    "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS,
    "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
}
MOON_ASPECT_BODIES = {
    "Sun": swe.SUN, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
    "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
}
_ASPECTS = (0, 60, 90, 120, 180)


def _void_of_course(jd: float) -> tuple[bool, float]:
    """(is_voc, arc_to_next_aspect_deg). Approximation that ignores the slow
    planets' motion relative to the Moon."""
    moon = ephem.planet_lon(jd, swe.MOON)[0]
    arc_to_sign_end = 30 - (moon % 30)
    best = 360.0
    for ipl in MOON_ASPECT_BODIES.values():
        p = ephem.planet_lon(jd, ipl)[0]
        for a in _ASPECTS:
            for target in ((p + a) % 360, (p - a) % 360):
                fwd = (target - moon) % 360
                if 0 < fwd < best:
                    best = fwd
    return best > arc_to_sign_end, best


def _eclipse_date(fn, jd: float) -> str | None:
    try:
        _ret, tret = fn(jd, swe.FLG_MOSEPH, 0, False)
        y, m, d, _ = swe.revjul(tret[0], swe.GREG_CAL)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        return None


def sky_data(ctx) -> SystemReading:
    from ..core.timeutil import local_midnight
    jd0 = ephem.jd_ut(local_midnight(ctx.now))
    sr = ephem.next_sunrise(jd0, ctx.lat, ctx.lon)
    ss = ephem.next_sunset(jd0, ctx.lat, ctx.lon)
    if sr and ss:
        hours = (ss - sr) * 24
        daylen = f"{int(hours)}h{int((hours % 1) * 60):02d}m of daylight"
    else:
        daylen = "polar day/night"

    next_solar = _eclipse_date(swe.sol_eclipse_when_glob, ctx.jd_now)
    next_lunar = _eclipse_date(swe.lun_eclipse_when, ctx.jd_now)
    illum = ephem.moon_phase(ctx.jd_now)["illumination"]

    return SystemReading(
        key="sky_data",
        title="Sky data",
        cadence=Cadence.ERA,
        layer=Layer.COSMIC,
        summary=(
            f"{daylen}; Moon {illum*100:.0f}% lit. "
            f"Next eclipses — solar {next_solar}, lunar {next_lunar}."
        ),
        detail={"daylight": daylen, "moon_illumination": round(illum, 2),
                "next_solar_eclipse": next_solar, "next_lunar_eclipse": next_lunar},
        keywords=["ground", "sky"],
    )


def mechanics(ctx) -> SystemReading:
    jd = ctx.jd_now
    retro = [name for name, ipl in RETRO_BODIES.items()
             if ephem.planet_lon(jd, ipl)[1] < 0]
    voc, arc = _void_of_course(jd)
    moon_sign = ephem.sign_name(ephem.planet_lon(jd, swe.MOON)[0])

    retro_txt = (", ".join(retro) + " retrograde") if retro else "no planets retrograde"
    if voc:
        moon_txt = f"Moon void-of-course in {moon_sign} — let plans ride, don't initiate"
    else:
        moon_txt = f"Moon active in {moon_sign} (next aspect in ~{arc:.1f}°)"
    return SystemReading(
        key="sky_mechanics",
        title="Sky mechanics",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=f"{retro_txt}; {moon_txt}.",
        detail={"retrograde": retro or "none",
                "moon_void_of_course": voc, "moon_sign": moon_sign},
        keywords=["review" if retro else "proceed"],
        score=-0.15 if (retro or voc) else 0.1,
    )
