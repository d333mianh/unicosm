"""Astrological age — the ~2,160-year era layer.

The vernal point precesses backward through the sidereal zodiac. Using the
Lahiri ayanamsa and equal 30° sidereal signs, we locate which constellation the
spring equinox currently falls in. Slow-moving context for everyone alive now.
"""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

AGE_THEME = {
    "Pisces": "faith, dissolution, the unseen — an age of belief and image",
    "Aquarius": "networks, technology, the collective — an age of systems and ideals",
    "Aries": "the individual and the new — an age of pioneers",
}


def reading(ctx) -> SystemReading:
    ayan = ephem.ayanamsa(ctx.jd_now)
    sidereal_vernal = (360 - ayan) % 360
    sign = ephem.SIGNS[int(sidereal_vernal // 30)]
    deg = sidereal_vernal % 30
    # how close to the next (precession runs toward lower longitude / prior sign)
    to_next = deg  # degrees of this sign remaining before the vernal point exits
    theme = AGE_THEME.get(sign, "a long civilizational arc")
    return SystemReading(
        key="astro_age",
        title="Astrological age",
        cadence=Cadence.ERA,
        layer=Layer.COSMIC,
        summary=(
            f"Age of {sign} ({deg:.1f}° in, ~{to_next*72:.0f} yrs to the cusp) — "
            f"{theme}."
        ),
        detail={"age": sign, "degrees_in": round(deg, 1),
                "ayanamsa": round(ayan, 2)},
        keywords=[sign.lower(), "era"],
    )
