"""Western natal astrology — the fixed chart signature.

Blueprint layer (birth only). Luminaries + Ascendant headline, enriched with
house placements, essential dignities, the chart ruler, and the tightest natal
aspects (a second reading).
"""

from __future__ import annotations

from ..core import astro, ephem
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

    # essential dignities worth naming
    dignities = []
    for p in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        d = astro.dignity(p, n.planets[p])
        if d:
            dignities.append(f"{p} in {d}")

    chart_ruler = astro.RULER[asc]
    cr_lon = n.planets.get(chart_ruler)
    cr_place = (f"{ephem.sign_name(cr_lon)} (house {n.house_of(cr_lon)})"
                if cr_lon is not None else "—")

    detail = {
        "Sun": f"{ephem.fmt_pos(n.planets['Sun'])} · house {n.house_of(n.planets['Sun'])}",
        "Moon": f"{ephem.fmt_pos(n.planets['Moon'])} · house {n.house_of(n.planets['Moon'])}",
        "Ascendant": ephem.fmt_pos(n.asc),
        "Midheaven": ephem.fmt_pos(n.mc),
        "chart_ruler": f"{chart_ruler} in {cr_place}",
    }
    for p in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        detail[p] = f"{ephem.fmt_pos(n.planets[p])} · house {n.house_of(n.planets[p])}"
    if dignities:
        detail["dignities"] = ", ".join(dignities)

    return SystemReading(
        key="western_natal",
        title="Natal chart (Western)",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=summary,
        detail=detail,
        keywords=SUN_KW[sun] + SUN_KW[moon][:1],
    )


def aspects(ctx) -> SystemReading:
    n = ctx.natal
    found = astro.find_aspects(n.planets)
    top = found[:5]
    if top:
        parts = [f"{a['a']} {a['glyph']} {a['b']} ({a['orb']}°)" for a in top]
        summary = "Tightest natal aspects: " + "; ".join(parts) + "."
    else:
        summary = "No major natal aspects within orb among the classical seven."
    return SystemReading(
        key="natal_aspects",
        title="Natal aspects",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=summary,
        detail={f"{a['a']}-{a['b']}": f"{a['aspect']} (orb {a['orb']}°)" for a in found},
        keywords=["pattern"],
    )
