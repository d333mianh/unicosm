"""Vimshottari Dasha reference data.

The 120-year cycle of nine planetary lords, the 27 nakshatras (each ruled by a
lord in the same repeating order, starting Ashwini = Ketu), and short themes.
"""

from __future__ import annotations

# Dasha lords in their fixed cyclic order.
LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Mahadasha length in years (sums to 120).
YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

# Vimshottari uses a 365.25-day year by common convention.
YEAR_DAYS = 365.25

# 27 nakshatras in zodiacal order. Ruler = LORDS[index % 9].
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# lord -> (theme, [keywords])
THEMES = {
    "Ketu": ("detachment, research, spiritual turns and loose ends",
             ["detach", "seek meaning"]),
    "Venus": ("relationship, pleasure, art, comfort and value",
              ["relate", "beautify"]),
    "Sun": ("authority, vitality, recognition and clarity of self",
            ["lead", "clarify"]),
    "Moon": ("emotion, home, nurture and public life",
             ["nurture", "feel"]),
    "Mars": ("drive, courage, effort and contention",
             ["act", "assert"]),
    "Rahu": ("ambition, the unconventional, hunger and the foreign",
             ["expand", "experiment"]),
    "Jupiter": ("wisdom, growth, fortune and teaching",
                ["grow", "learn"]),
    "Saturn": ("discipline, patience, labor and karmic maturation",
               ["endure", "build"]),
    "Mercury": ("communication, intellect, commerce and learning",
                ["communicate", "analyze"]),
}
