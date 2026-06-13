"""Jupiter cycle — the ~12-year personal 'chapter' (decade-scale layer).

Where transiting Jupiter sits relative to your natal Jupiter marks the phase of
your current ~11.86-year growth cycle; the sign it transits names the arena of
expansion this year-plus.
"""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

SIGN_ARENA = {
    "Aries": "self and new ventures", "Taurus": "resources and stability",
    "Gemini": "learning and connection", "Cancer": "home and belonging",
    "Leo": "creativity and visibility", "Virgo": "craft and health",
    "Libra": "partnership and fairness", "Scorpio": "depth and shared power",
    "Sagittarius": "meaning and horizons", "Capricorn": "ambition and structure",
    "Aquarius": "community and vision", "Pisces": "spirit and surrender",
}

JUPITER_PERIOD_YEARS = 11.862


def reading(ctx) -> SystemReading:
    natal = ctx.natal.planets["Jupiter"]
    transit, _ = ephem.planet_lon(ctx.jd_now, ephem.PLANETS["Jupiter"])
    diff = (transit - natal) % 360
    frac = diff / 360
    years_in = frac * JUPITER_PERIOD_YEARS
    sign = ephem.sign_name(transit)
    arena = SIGN_ARENA[sign]
    return SystemReading(
        key="jupiter_cycle",
        title="Jupiter chapter",
        cadence=Cadence.DECADE,
        layer=Layer.PERSONAL,
        summary=(
            f"Jupiter in {sign} — growth through {arena}. "
            f"You are {years_in:.1f} yrs into your ~12-yr Jupiter cycle "
            f"({frac*100:.0f}%)."
        ),
        detail={"transit_sign": sign, "arena": arena,
                "years_into_cycle": round(years_in, 1),
                "cycle_fraction": round(frac, 2)},
        keywords=["expand", arena.split(" and ")[0]],
        score=0.3,
    )
