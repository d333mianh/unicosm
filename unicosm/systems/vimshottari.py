"""Vimshottari Dasha — nested planetary time-lords from the Moon's nakshatra.

The deepest personal-cycle engine: mahadasha -> antardasha -> pratyantardasha,
resolvable to the day. Emits the janma (birth) nakshatra (blueprint), the
current mahadasha (decade), and the current antardasha + pratyantar (year).
"""

from __future__ import annotations

from dataclasses import dataclass

import swisseph as swe

from ..core import ephem
from ..data.vimshottari import LORDS, NAKSHATRAS, THEMES, YEAR_DAYS, YEARS
from ..models import Cadence, Layer, SystemReading

NAK_SIZE = 360.0 / 27       # 13°20'


@dataclass
class Period:
    lord: str
    start_jd: float
    end_jd: float
    years: float


def _subperiods(start_lord_idx: int, start_jd: float, length_years: float) -> list[Period]:
    """The nine sub-periods of a period of `length_years`, beginning with the
    period's own lord, each scaled by its share of 120."""
    out: list[Period] = []
    cur = start_jd
    for k in range(9):
        lord = LORDS[(start_lord_idx + k) % 9]
        yrs = length_years * YEARS[lord] / 120.0
        end = cur + yrs * YEAR_DAYS
        out.append(Period(lord, cur, end, yrs))
        cur = end
    return out


def _active(periods: list[Period], jd: float) -> Period:
    for p in periods:
        if p.start_jd <= jd < p.end_jd:
            return p
    return periods[-1] if jd >= periods[-1].end_jd else periods[0]


def _jd_date(jd: float) -> str:
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def compute(birth_jd: float, now_jd: float) -> dict:
    ayan = ephem.ayanamsa(birth_jd)
    moon_trop = ephem.planet_lon(birth_jd, ephem.PLANETS["Moon"])[0]
    moon_sid = (moon_trop - ayan) % 360.0

    nak_idx = int(moon_sid // NAK_SIZE)
    within = moon_sid % NAK_SIZE
    frac = within / NAK_SIZE
    pada = int(within / (NAK_SIZE / 4)) + 1
    start_lord_idx = nak_idx % 9
    first_lord = LORDS[start_lord_idx]

    elapsed_years = frac * YEARS[first_lord]
    maha_cycle_start = birth_jd - elapsed_years * YEAR_DAYS

    mahas = _subperiods(start_lord_idx, maha_cycle_start, 120.0)
    maha = _active(mahas, now_jd)
    antars = _subperiods(LORDS.index(maha.lord), maha.start_jd, maha.years)
    antar = _active(antars, now_jd)
    pratys = _subperiods(LORDS.index(antar.lord), antar.start_jd, antar.years)
    praty = _active(pratys, now_jd)

    return {
        "nakshatra": NAKSHATRAS[nak_idx],
        "pada": pada,
        "nak_lord": first_lord,
        "maha": maha,
        "antar": antar,
        "praty": praty,
    }


# ---- readings -----------------------------------------------------------

def janma_nakshatra(ctx) -> SystemReading:
    c = compute(ctx.natal.jd, ctx.jd_now)
    theme, kw = THEMES[c["nak_lord"]]
    return SystemReading(
        key="janma_nakshatra",
        title="Janma nakshatra",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=(
            f"Moon in {c['nakshatra']} (pada {c['pada']}), ruled by {c['nak_lord']} — "
            f"your birth star colors the mind with {theme}."
        ),
        detail={"nakshatra": c["nakshatra"], "pada": c["pada"],
                "ruler": c["nak_lord"]},
        keywords=kw,
    )


def mahadasha(ctx) -> SystemReading:
    c = compute(ctx.natal.jd, ctx.jd_now)
    m = c["maha"]
    theme, kw = THEMES[m.lord]
    return SystemReading(
        key="vimshottari_maha",
        title="Mahadasha (Vimshottari)",
        cadence=Cadence.DECADE,
        layer=Layer.PERSONAL,
        summary=(
            f"{m.lord} mahadasha ({_jd_date(m.start_jd)} → {_jd_date(m.end_jd)}, "
            f"{m.years:.0f} yrs) — a long chapter of {theme}."
        ),
        detail={"lord": m.lord, "start": _jd_date(m.start_jd),
                "end": _jd_date(m.end_jd), "years": round(m.years, 1)},
        keywords=kw,
    )


def antardasha(ctx) -> SystemReading:
    c = compute(ctx.natal.jd, ctx.jd_now)
    m, a, p = c["maha"], c["antar"], c["praty"]
    a_theme, a_kw = THEMES[a.lord]
    return SystemReading(
        key="vimshottari_bhukti",
        title="Antardasha (Vimshottari)",
        cadence=Cadence.YEAR,
        layer=Layer.PERSONAL,
        summary=(
            f"{m.lord}–{a.lord} antardasha (until {_jd_date(a.end_jd)}); "
            f"pratyantar {p.lord} (until {_jd_date(p.end_jd)}). "
            f"Within the chapter, a sub-season of {a_theme}."
        ),
        detail={
            "mahadasha": m.lord,
            "antardasha": a.lord,
            "antardasha_until": _jd_date(a.end_jd),
            "pratyantardasha": p.lord,
            "pratyantardasha_until": _jd_date(p.end_jd),
        },
        keywords=a_kw,
    )
