"""Lunar phase — the shared lunar-month rhythm (cosmic weather)."""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

PHASE_GUIDANCE = {
    "New Moon": ("set intentions, begin quietly", ["intend", "seed", "begin"]),
    "Waxing Crescent": ("commit, take first steps", ["commit", "act"]),
    "First Quarter": ("push through resistance, decide", ["decide", "push"]),
    "Waxing Gibbous": ("refine, adjust, persevere", ["refine", "persist"]),
    "Full Moon": ("culminate, illuminate, release excess", ["culminate", "reveal"]),
    "Waning Gibbous": ("share, give back, digest", ["share", "teach"]),
    "Last Quarter": ("clear, forgive, let go", ["clear", "release"]),
    "Waning Crescent": ("rest, surrender, restore", ["rest", "surrender"]),
}


def reading(ctx) -> SystemReading:
    mp = ephem.moon_phase(ctx.jd_now)
    name = mp["phase_name"]
    guide, kw = PHASE_GUIDANCE[name]
    return SystemReading(
        key="moon_phase",
        title="Lunar phase",
        cadence=Cadence.LUNAR_MONTH,
        layer=Layer.COSMIC,
        summary=(
            f"{name} ({mp['illumination']*100:.0f}% lit), "
            f"Moon in {ephem.sign_name(mp['moon_lon'])} — time to {guide}."
        ),
        detail={
            "phase": name,
            "illumination": round(mp["illumination"], 3),
            "moon_sign": ephem.sign_name(mp["moon_lon"]),
            "waxing": mp["waxing"],
        },
        keywords=kw,
        score=0.2 if mp["waxing"] else -0.1,
    )
