"""Shared helpers and reference data for systems."""

from __future__ import annotations

# Traditional (Hellenistic / classical) sign rulers.
SIGN_RULER = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Rough benefic/malefic tone for favorability hints (classical).
PLANET_TONE = {
    "Jupiter": 0.6, "Venus": 0.5, "Sun": 0.2, "Mercury": 0.1, "Moon": 0.1,
    "Mars": -0.4, "Saturn": -0.5,
}


def reduce_number(n: int, keep_master: bool = True) -> int:
    """Pythagorean digit reduction. Keeps master numbers 11/22/33 if asked."""
    while n > 9:
        if keep_master and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return n


def digit_sum(*parts: int, keep_master: bool = True) -> int:
    return reduce_number(sum(parts), keep_master=keep_master)


def article(word: str) -> str:
    """'a' or 'an' for the given word."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def ordinal(n: int) -> str:
    """1 -> '1st', 2 -> '2nd', 11 -> '11th', etc."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
