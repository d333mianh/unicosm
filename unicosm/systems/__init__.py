"""System registry.

Each system is a callable ``reading(ctx) -> SystemReading | None``. Adding a new
tradition = drop a module here and append it to REGISTRY. This is the seam the
project grows along, step by step (see complementary-systems-v2.md).
"""

from __future__ import annotations

from ..context import DayContext
from ..models import SystemReading
from . import (
    astro_age,
    gene_keys,
    human_design,
    jupiter_cycle,
    moon_phase,
    numerology,
    panchang,
    planetary_hours,
    profections,
    progressions,
    returns,
    sexagenary,
    solar_term,
    tcm_organ,
    transits,
    vimshottari,
    western_natal,
    zodiacal_releasing,
)

# Order is loosely fastest-cadence-first; synthesis re-groups by cadence anyway.
REGISTRY = [
    western_natal.reading,
    western_natal.aspects,
    human_design.reading,
    gene_keys.reading,
    vimshottari.janma_nakshatra,
    numerology.life_path,
    planetary_hours.reading,
    tcm_organ.reading,
    panchang.timing,
    sexagenary.reading,
    panchang.reading,
    numerology.personal_day,
    human_design.transit,
    transits.reading,
    returns.lunar_return,
    moon_phase.reading,
    solar_term.reading,
    profections.reading,
    numerology.personal_year,
    returns.solar_return,
    vimshottari.antardasha,
    jupiter_cycle.reading,
    vimshottari.mahadasha,
    zodiacal_releasing.reading,
    progressions.reading,
    numerology.pinnacles,
    astro_age.reading,
]


def all_readings(ctx: DayContext) -> list[SystemReading]:
    out: list[SystemReading] = []
    for fn in REGISTRY:
        try:
            r = fn(ctx)
        except Exception as exc:  # a single failing system must not break the day
            out.append(_error_reading(fn, exc))
            continue
        if r is not None:
            out.append(r)
    return out


def _error_reading(fn, exc: Exception) -> SystemReading:
    from ..models import Cadence, Layer
    return SystemReading(
        key=getattr(fn, "__module__", "unknown"),
        title="(system error)",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=f"{fn.__module__} failed: {exc}",
        detail={"error": str(exc)},
    )
