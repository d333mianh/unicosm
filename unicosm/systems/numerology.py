"""Pythagorean numerology — Life Path (blueprint), Personal Year, Personal Day.

Fully algorithmic, the canonical 'birth date x today' system.
"""

from __future__ import annotations

from ..core.timeutil import whole_years_since
from ..models import Cadence, Layer, SystemReading
from .base import digit_sum, ordinal, reduce_number

CHALLENGE_THEME = {
    0: "balance every challenge — the power of conscious choice",
    1: "stand in your own will without domination",
    2: "cooperate without losing yourself to oversensitivity",
    3: "express freely past self-criticism",
    4: "build discipline without rigidity",
    5: "use freedom without recklessness",
    6: "serve responsibly without martyrdom",
    7: "stay open and trusting rather than isolated",
    8: "hold power and money in right relationship",
}

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


def pinnacles(ctx) -> SystemReading:
    """Four life-stage pinnacles + challenges, with the current one by age."""
    b = ctx.profile.birth_dt
    m = reduce_number(_digits(b.month), keep_master=False)
    d = reduce_number(_digits(b.day), keep_master=False)
    y = reduce_number(_digits(b.year), keep_master=False)
    lp = reduce_number(_digits(b.year, b.month, b.day), keep_master=False)

    p1 = reduce_number(m + d)
    p2 = reduce_number(d + y)
    p3 = reduce_number(reduce_number(p1, keep_master=False)
                       + reduce_number(p2, keep_master=False))
    p4 = reduce_number(m + y)
    pins = [p1, p2, p3, p4]
    chals = [abs(m - d), abs(d - y), abs(abs(m - d) - abs(d - y)), abs(m - y)]

    end1 = 36 - lp
    bounds = [(0, end1), (end1 + 1, end1 + 9), (end1 + 10, end1 + 18),
              (end1 + 19, 120)]
    age = whole_years_since(b, ctx.now)
    idx = next((i for i, (lo, hi) in enumerate(bounds) if lo <= age <= hi), 3)

    pin, chal = pins[idx], chals[idx]
    theme, kw = MEANING[pin]
    lo, hi = bounds[idx]
    span = f"ages {lo}–{hi}" if idx < 3 else f"ages {lo}+"
    return SystemReading(
        key="numerology_pinnacles",
        title="Numerology pinnacle",
        cadence=Cadence.DECADE,
        layer=Layer.PERSONAL,
        summary=(
            f"{ordinal(idx + 1)} Pinnacle {pin} ({theme}), {span} — "
            f"with Challenge {chal}: {CHALLENGE_THEME[chal]}."
        ),
        detail={"pinnacle": pin, "pinnacle_theme": theme, "challenge": chal,
                "challenge_theme": CHALLENGE_THEME[chal], "span": span,
                "all_pinnacles": pins, "all_challenges": chals},
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
