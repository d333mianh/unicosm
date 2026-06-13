"""Panchang reference data — names for the five limbs (and Choghadiya)."""

from __future__ import annotations

# 15 tithi names; the 15th is Purnima (full) in the bright fortnight and
# Amavasya (new) in the dark fortnight.
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]

# 7 repeating "movable" karanas; Vishti (Bhadra) is inauspicious.
KARANA_MOVABLE = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
KARANA_FIXED_FIRST = "Kimstughna"
KARANA_FIXED_LAST = ["Shakuni", "Chatushpada", "Naga"]

# Weekday (Python Monday=0) -> (vara name, planetary lord).
VARA = {
    0: ("Somavara", "Moon"), 1: ("Mangalavara", "Mars"),
    2: ("Budhavara", "Mercury"), 3: ("Guruvara", "Jupiter"),
    4: ("Shukravara", "Venus"), 5: ("Shanivara", "Saturn"),
    6: ("Ravivara", "Sun"),
}

# ---- Choghadiya -----------------------------------------------------------
# Fixed cyclic order of the 7 choghadiya types.
CHOGHADIYA_CYCLE = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]

# First DAY choghadiya by weekday (Python Monday=0) -> index into the cycle.
CHOGHADIYA_DAY_START = {6: 0, 0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4}
# First NIGHT choghadiya by weekday.
CHOGHADIYA_NIGHT_START = {6: 5, 0: 1, 1: 4, 2: 0, 3: 3, 4: 6, 5: 2}

CHOGHADIYA_QUALITY = {
    "Amrit": ("good", "nectar — most auspicious"),
    "Shubh": ("good", "auspicious, good for ceremonies"),
    "Labh": ("good", "gain — good for work and study"),
    "Char": ("neutral", "movable — good for travel"),
    "Udveg": ("bad", "anxiety — avoid important starts"),
    "Rog": ("bad", "illness — avoid"),
    "Kaal": ("bad", "loss — avoid"),
}

# Rahu Kalam / Yamaganda / Gulika as the 1-based eighth-of-day part per weekday.
RAHU_PART = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
YAMA_PART = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
GULIKA_PART = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
