"""Rune draw — Elder Futhark, single or three-rune cast, with merkstave."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..data.runes import RUNES


@dataclass
class DrawnRune:
    name: str
    glyph: str
    meaning: str
    reversed_meaning: str
    merkstave: bool


def draw_runes(rng: random.Random | None = None, n: int = 1) -> list[DrawnRune]:
    r = rng or random.Random()
    picks = r.sample(RUNES, n)
    out: list[DrawnRune] = []
    for name, glyph, meaning, reversed_meaning, invertible in picks:
        merk = invertible and r.random() < 0.5
        out.append(DrawnRune(name, glyph, meaning, reversed_meaning, merk))
    return out
