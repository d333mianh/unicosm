"""Annual profections (Hellenistic) — the year's activated house and Lord.

Each year of life advances one whole sign from the natal Ascendant; the ruler
of that sign becomes the Lord of the Year, the planet whose condition colors
the chapter.
"""

from __future__ import annotations

from ..core import ephem
from ..core.timeutil import whole_years_since
from ..models import Cadence, Layer, SystemReading
from .base import SIGN_RULER, ordinal

HOUSE_TOPIC = {
    1: "self, body, vitality, fresh starts",
    2: "money, resources, what you value",
    3: "communication, learning, siblings, local life",
    4: "home, family, roots, inner foundations",
    5: "creativity, romance, children, play",
    6: "work, health, daily routine, service",
    7: "partnership, others, open relationships",
    8: "shared resources, depth, transformation",
    9: "travel, study, meaning, the wider world",
    10: "career, public role, reputation",
    11: "friends, community, hopes, alliances",
    12: "retreat, spirituality, rest, letting go",
}


def reading(ctx) -> SystemReading:
    age = whole_years_since(ctx.profile.birth_dt, ctx.now)
    asc_sign_idx = ephem.sign_index(ctx.natal.asc)
    house = (age % 12) + 1
    sign_idx = (asc_sign_idx + age) % 12
    sign = ephem.SIGNS[sign_idx]
    lord = SIGN_RULER[sign]
    topic = HOUSE_TOPIC[house]
    return SystemReading(
        key="profections",
        title="Annual profection",
        cadence=Cadence.YEAR,
        layer=Layer.PERSONAL,
        summary=(
            f"Age {age}: profected {ordinal(house)} house in {sign}, "
            f"Lord of the Year {lord}. The year emphasizes {topic}."
        ),
        detail={"age": age, "house": house, "sign": sign, "lord": lord, "topic": topic},
        keywords=[topic.split(",")[0].strip(), lord.lower()],
    )
