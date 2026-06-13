"""Pythagorean numerology — Life Path (blueprint), Personal Year, Personal Day.

Fully algorithmic, the canonical 'birth date x today' system.
"""

from __future__ import annotations

from ..models import Cadence, Layer, SystemReading
from .base import digit_sum, reduce_number

MEANING = {
    1: ("initiation", ["lead", "begin", "act"]),
    2: ("relationship", ["cooperate", "listen", "pair"]),
    3: ("expression", ["create", "speak", "play"]),
    4: ("structure", ["build", "order", "work"]),
    5: ("change", ["move", "adapt", "explore"]),
    6: ("responsibility", ["nurture", "tend", "harmonize"]),
    7: ("reflection", ["study", "rest", "go inward"]),
    8: ("power", ["execute", "manage", "claim"]),
    9: ("completion", ["release", "give", "finish"]),
    11: ("intuition", ["sense", "inspire", "attune"]),
    22: ("master-building", ["manifest", "architect", "scale"]),
    33: ("master-care", ["heal", "uplift", "serve widely"]),
}


def _digits(*nums: int) -> int:
    total = 0
    for x in nums:
        total += sum(int(d) for d in str(x))
    return total


def life_path(ctx) -> SystemReading:
    b = ctx.profile.birth_dt
    lp = reduce_number(_digits(b.year, b.month, b.day), keep_master=True)
    theme, kw = MEANING[lp]
    return SystemReading(
        key="numerology_life_path",
        title="Life Path number",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=f"Life Path {lp} — the path of {theme}.",
        detail={"life_path": lp, "theme": theme},
        keywords=kw,
    )


def personal_year(ctx) -> SystemReading:
    b = ctx.profile.birth_dt
    y = ctx.now.year
    # personal year uses birth month + birth day + current year
    py = reduce_number(_digits(b.month, b.day, y), keep_master=True)
    theme, kw = MEANING[py]
    return SystemReading(
        key="numerology_personal_year",
        title="Personal Year",
        cadence=Cadence.YEAR,
        layer=Layer.PERSONAL,
        summary=f"Personal Year {py} — a year of {theme}.",
        detail={"personal_year": py, "theme": theme},
        keywords=kw,
    )


def personal_day(ctx) -> SystemReading:
    b = ctx.profile.birth_dt
    now = ctx.now
    py = digit_sum(_digits(b.month, b.day, now.year))
    pm = reduce_number(py + _digits(now.month))
    pd = reduce_number(pm + _digits(now.day))
    theme, kw = MEANING[pd]
    return SystemReading(
        key="numerology_personal_day",
        title="Personal Day",
        cadence=Cadence.DAILY,
        layer=Layer.PERSONAL,
        summary=f"Personal Day {pd} — a day to {kw[0]}; the tone is {theme}.",
        detail={"personal_day": pd, "theme": theme, "actions": kw},
        keywords=kw,
    )
