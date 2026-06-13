"""Shared astrology helpers: aspects and essential dignities."""

from __future__ import annotations

from . import ephem

# aspect angle -> (name, glyph)
ASPECTS = {
    0: ("conjunction", "☌"),
    60: ("sextile", "⚹"),
    90: ("square", "□"),
    120: ("trine", "△"),
    180: ("opposition", "☍"),
}
DEFAULT_ORB = 7.0
LUMINARY_ORB = 8.0

# Essential dignities.
RULER = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo", "Venus": "Pisces",
    "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra",
}
_OPPOSITE = {
    "Aries": "Libra", "Taurus": "Scorpio", "Gemini": "Sagittarius",
    "Cancer": "Capricorn", "Leo": "Aquarius", "Virgo": "Pisces",
    "Libra": "Aries", "Scorpio": "Taurus", "Sagittarius": "Gemini",
    "Capricorn": "Cancer", "Aquarius": "Leo", "Pisces": "Virgo",
}


def angle(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def aspect_between(lon_a: float, lon_b: float, luminary: bool = False
                   ) -> tuple[str, str, float] | None:
    """Return (aspect_name, glyph, orb) if `lon_a` and `lon_b` form a major
    aspect within orb, else None."""
    sep = angle(lon_a, lon_b)
    orb_max = LUMINARY_ORB if luminary else DEFAULT_ORB
    for exact, (name, glyph) in ASPECTS.items():
        orb = abs(sep - exact)
        if orb <= orb_max:
            return name, glyph, orb
    return None


def find_aspects(positions: dict[str, float], luminaries=("Sun", "Moon")
                 ) -> list[dict]:
    """All major aspects among the given bodies, tightest first."""
    names = list(positions)
    out: list[dict] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            lum = a in luminaries or b in luminaries
            hit = aspect_between(positions[a], positions[b], lum)
            if hit:
                name, glyph, orb = hit
                out.append({"a": a, "b": b, "aspect": name,
                            "glyph": glyph, "orb": round(orb, 1)})
    out.sort(key=lambda x: x["orb"])
    return out


def dignity(planet: str, lon: float) -> str | None:
    """Essential dignity of a planet at a longitude: domicile / exaltation /
    detriment / fall, or None if peregrine."""
    sign = ephem.sign_name(lon)
    if RULER.get(sign) == planet:
        return "domicile"
    if EXALTATION.get(planet) == sign:
        return "exaltation"
    if RULER.get(_OPPOSITE[sign]) == planet:
        return "detriment"
    if EXALTATION.get(planet) == _OPPOSITE[sign]:
        return "fall"
    return None
