"""Maria Thun biodynamic day — the Moon's sidereal constellation maps to an
element and a plant-part day (root / leaf / flower / fruit). Gardening guidance."""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

# element by tropical/sidereal sign (we use sidereal, the biodynamic convention)
ELEMENT = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

DAY_TYPE = {
    "Fire": ("Fruit/Seed day", "sow & harvest fruiting and seed crops"),
    "Earth": ("Root day", "plant & tend root crops; work the soil"),
    "Air": ("Flower day", "sow & cut flowers; tend flowering plants"),
    "Water": ("Leaf day", "plant leafy greens; water and feed foliage"),
}


def reading(ctx) -> SystemReading:
    ayan = ephem.ayanamsa(ctx.jd_now)
    moon = ephem.planet_lon(ctx.jd_now, ephem.PLANETS["Moon"])[0]
    sidereal_sign = ephem.sign_name((moon - ayan) % 360)
    element = ELEMENT[sidereal_sign]
    day_type, task = DAY_TYPE[element]
    return SystemReading(
        key="biodynamic",
        title="Biodynamic day (Maria Thun)",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=(
            f"{day_type} — Moon in sidereal {sidereal_sign} ({element}): {task}."
        ),
        detail={"day_type": day_type, "moon_sidereal_sign": sidereal_sign,
                "element": element},
        keywords=[day_type.split("/")[0].split()[0].lower(), "tend"],
    )
