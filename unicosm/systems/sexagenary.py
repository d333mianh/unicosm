"""Sexagenary day pillar (60 jiazi) — the unbroken stem/branch day signature.

The engine under BaZi and the Tong Shu. Formula verified against the reference
date 2019-01-27 = jiazi (甲子). Stem (0=甲) = (JDN_noon - 1) mod 10;
Branch (0=子) = (JDN_noon + 1) mod 12.
"""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

STEMS = [
    ("Jiǎ", "甲", "Yang Wood"), ("Yǐ", "乙", "Yin Wood"),
    ("Bǐng", "丙", "Yang Fire"), ("Dīng", "丁", "Yin Fire"),
    ("Wù", "戊", "Yang Earth"), ("Jǐ", "己", "Yin Earth"),
    ("Gēng", "庚", "Yang Metal"), ("Xīn", "辛", "Yin Metal"),
    ("Rén", "壬", "Yang Water"), ("Guǐ", "癸", "Yin Water"),
]

BRANCHES = [
    ("Zǐ", "子", "Rat"), ("Chǒu", "丑", "Ox"), ("Yín", "寅", "Tiger"),
    ("Mǎo", "卯", "Rabbit"), ("Chén", "辰", "Dragon"), ("Sì", "巳", "Snake"),
    ("Wǔ", "午", "Horse"), ("Wèi", "未", "Goat"), ("Shēn", "申", "Monkey"),
    ("Yǒu", "酉", "Rooster"), ("Xū", "戌", "Dog"), ("Hài", "亥", "Pig"),
]

ELEMENT_KW = {
    "Wood": ["growth", "planning"], "Fire": ["expression", "visibility"],
    "Earth": ["grounding", "consolidation"], "Metal": ["refinement", "cutting"],
    "Water": ["flow", "reflection"],
}


def reading(ctx) -> SystemReading:
    d = ctx.now
    jdn = ephem.jdn_noon(d.year, d.month, d.day)
    s = STEMS[(jdn - 1) % 10]
    b = BRANCHES[(jdn + 1) % 12]
    index = (jdn - 11) % 60 + 1
    element = s[2].split()[1]  # Wood/Fire/Earth/Metal/Water
    kw = ELEMENT_KW[element]
    return SystemReading(
        key="sexagenary",
        title="Day pillar (sexagenary)",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=(
            f"{s[0]}-{b[0]} ({s[1]}{b[1]}), day {index}/60 — "
            f"a {s[2]} day in the year of cycles; the {b[2]}'s hours. "
            f"Element {element}: favor {kw[0]}."
        ),
        detail={
            "pillar": f"{s[0]} {b[0]}",
            "hanzi": f"{s[1]}{b[1]}",
            "stem_element": s[2],
            "branch_animal": b[2],
            "cycle_day": index,
        },
        keywords=kw,
    )
