"""Western natal astrology — the fixed luminary + Ascendant signature.

Blueprint layer (birth only). The thin-slice version: Sun (core self),
Moon (inner/emotional nature), Ascendant (outward style). The headline of who
you are, before any cycle moves.
"""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading
from .base import article

SUN_KW = {
    "Aries": ["initiative", "courage"], "Taurus": ["steadiness", "sensuality"],
    "Gemini": ["curiosity", "exchange"], "Cancer": ["care", "rootedness"],
    "Leo": ["radiance", "creativity"], "Virgo": ["refinement", "service"],
    "Libra": ["balance", "relating"], "Scorpio": ["depth", "intensity"],
    "Sagittarius": ["vision", "freedom"], "Capricorn": ["discipline", "mastery"],
    "Aquarius": ["independence", "vision"], "Pisces": ["empathy", "imagination"],
}


def reading(ctx) -> SystemReading:
    n = ctx.natal
    sun, moon, asc = n.sign("Sun"), n.sign("Moon"), n.sign("Asc")
    drive = SUN_KW[sun][0]
    summary = (
        f"Sun in {sun}, Moon in {moon}, rising {asc} — "
        f"{article(drive)} {drive}-driven core with a {moon}-toned inner life, "
        f"meeting the world {asc}-style."
    )
    return SystemReading(
        key="western_natal",
        title="Natal chart (Western)",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=summary,
        detail={
            "Sun": ephem.fmt_pos(n.planets["Sun"]),
            "Moon": ephem.fmt_pos(n.planets["Moon"]),
            "Ascendant": ephem.fmt_pos(n.asc),
            **{p: ephem.fmt_pos(n.planets[p]) for p in
               ("Mercury", "Venus", "Mars", "Jupiter", "Saturn")},
        },
        keywords=SUN_KW[sun] + SUN_KW[moon][:1],
    )
