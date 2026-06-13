"""Panchang — the five limbs of the Vedic almanac (cosmic weather, daily).

Tithi (lunar day), Nakshatra (Moon's mansion), Yoga (Sun+Moon), Karana
(half-tithi), and Vara (weekday lord). Sidereal quantities use the Lahiri
ayanamsa; tithi/karana use the Sun–Moon elongation (ayanamsa-independent).
"""

from __future__ import annotations

from ..core import ephem
from ..data.panchang import (
    KARANA_FIXED_FIRST,
    KARANA_FIXED_LAST,
    KARANA_MOVABLE,
    TITHI_NAMES,
    VARA,
    YOGA_NAMES,
)
from ..data.vimshottari import NAKSHATRAS
from ..models import Cadence, Layer, SystemReading

NAK_SIZE = 360.0 / 27


def _tithi(elong: float) -> dict:
    num = int(elong // 12) + 1                 # 1..30
    if num <= 15:
        paksha, idx = "Shukla (waxing)", num
        name = TITHI_NAMES[idx - 1]
    else:
        paksha, idx = "Krishna (waning)", num - 15
        name = "Amavasya" if idx == 15 else TITHI_NAMES[idx - 1]
    return {"num": num, "name": name, "paksha": paksha}


def _karana(elong: float) -> str:
    idx = int(elong // 6)                       # 0..59
    if idx == 0:
        return KARANA_FIXED_FIRST
    if idx <= 56:
        return KARANA_MOVABLE[(idx - 1) % 7]
    return KARANA_FIXED_LAST[idx - 57]


def compute(ctx) -> dict:
    jd = ctx.jd_now
    ayan = ephem.ayanamsa(jd)
    sun = ephem.planet_lon(jd, ephem.PLANETS["Sun"])[0]
    moon = ephem.planet_lon(jd, ephem.PLANETS["Moon"])[0]
    elong = (moon - sun) % 360.0

    tithi = _tithi(elong)
    moon_sid = (moon - ayan) % 360.0
    nak_idx = int(moon_sid // NAK_SIZE)
    pada = int((moon_sid % NAK_SIZE) / (NAK_SIZE / 4)) + 1
    yoga_idx = int(((sun + moon - 2 * ayan) % 360) // NAK_SIZE)
    karana = _karana(elong)
    vara_name, vara_lord = VARA[ctx.now.weekday()]

    return {
        "tithi": tithi,
        "nakshatra": NAKSHATRAS[nak_idx],
        "pada": pada,
        "yoga": YOGA_NAMES[yoga_idx],
        "karana": karana,
        "vara": vara_name,
        "vara_lord": vara_lord,
    }


def reading(ctx) -> SystemReading:
    p = compute(ctx)
    t = p["tithi"]
    notes = []
    if t["name"] == "Ekadashi":
        notes.append("Ekadashi — a traditional fasting/observance day")
    if t["name"] == "Purnima":
        notes.append("Purnima — full moon")
    if t["name"] == "Amavasya":
        notes.append("Amavasya — new moon")
    if p["karana"] == "Vishti":
        notes.append("Vishti (Bhadra) karana — inauspicious for new ventures")
    note = f" · {'; '.join(notes)}" if notes else ""

    return SystemReading(
        key="panchang",
        title="Panchang (five limbs)",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=(
            f"{p['vara']} · {t['paksha'].split()[0]} {t['name']} tithi · "
            f"{p['nakshatra']} nakshatra · {p['yoga']} yoga · {p['karana']} karana{note}."
        ),
        detail={
            "tithi": f"{t['name']} ({t['paksha']})",
            "nakshatra": f"{p['nakshatra']} (pada {p['pada']})",
            "yoga": p["yoga"],
            "karana": p["karana"],
            "vara": f"{p['vara']} (lord {p['vara_lord']})",
        },
        keywords=["observe", "time well"],
    )
