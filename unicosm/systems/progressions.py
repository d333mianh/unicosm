"""Secondary progressions — the natal chart slowly evolving ('a day for a year').

Progressed Sun marks the maturing identity (~30 yrs per sign); the progressed
Moon's phase relative to the progressed Sun tracks the ~29.5-year progressed
lunation cycle — the inner chapters of a life.
"""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

TROPICAL_YEAR = 365.2422

PHASE_NOTE = {
    "New Moon": ("a new inner chapter seeding", ["begin", "seed"]),
    "Waxing Crescent": ("building the new direction", ["build", "commit"]),
    "First Quarter": ("acting through resistance", ["push", "decide"]),
    "Waxing Gibbous": ("refining toward a peak", ["refine", "adjust"]),
    "Full Moon": ("culmination and full awareness", ["fulfill", "see clearly"]),
    "Waning Gibbous": ("sharing what ripened", ["share", "teach"]),
    "Last Quarter": ("reorienting, a crisis of meaning", ["reorient", "question"]),
    "Waning Crescent": ("releasing, composting the cycle", ["release", "rest"]),
}


def reading(ctx) -> SystemReading:
    birth_jd = ctx.natal.jd
    age_years = (ctx.jd_now - birth_jd) / TROPICAL_YEAR
    prog_jd = birth_jd + age_years          # day-for-a-year

    mp = ephem.moon_phase(prog_jd)
    psun_sign = ephem.sign_name(mp["sun_lon"])
    pmoon_sign = ephem.sign_name(mp["moon_lon"])
    phase = mp["phase_name"]
    note, kw = PHASE_NOTE[phase]

    return SystemReading(
        key="progressions",
        title="Secondary progressions",
        cadence=Cadence.DECADE,
        layer=Layer.PERSONAL,
        summary=(
            f"Progressed Sun in {psun_sign}, progressed Moon in {pmoon_sign} — "
            f"{phase} of the ~29.5-yr progressed lunation cycle: {note}."
        ),
        detail={
            "progressed_sun": ephem.fmt_pos(mp["sun_lon"]),
            "progressed_moon": ephem.fmt_pos(mp["moon_lon"]),
            "lunation_phase": phase,
        },
        keywords=kw,
    )
