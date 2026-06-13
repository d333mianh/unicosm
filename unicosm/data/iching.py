"""I Ching data — the 64 hexagrams in King Wen order.

Built from the canonical King Wen trigram matrix (rows = lower trigram, columns
= upper trigram). Binary is bottom-to-top, yang=1. Verified against anchors:
1 (☰☰), 2 (☷☷), 11/12 (Peace/Standstill), 29/30, 63/64.
"""

from __future__ import annotations

# Trigram line patterns, bottom-to-top (yang=1).
TRIGRAM_BITS = {
    "Qian": "111", "Zhen": "100", "Kan": "010", "Gen": "001",
    "Kun": "000", "Xun": "011", "Li": "101", "Dui": "110",
}
_ORDER = ["Qian", "Zhen", "Kan", "Gen", "Kun", "Xun", "Li", "Dui"]

# King Wen number by [lower trigram][upper trigram] (Wilhelm-Baynes table).
_KINGWEN = [
    # upper: Qian Zhen Kan Gen Kun Xun  Li  Dui
    [1, 34, 5, 26, 11, 9, 14, 43],     # lower Qian
    [25, 51, 3, 27, 24, 42, 21, 17],   # lower Zhen
    [6, 40, 29, 4, 7, 59, 64, 47],     # lower Kan
    [33, 62, 39, 52, 15, 53, 56, 31],  # lower Gen
    [12, 16, 8, 23, 2, 20, 35, 45],    # lower Kun
    [44, 32, 48, 18, 46, 57, 50, 28],  # lower Xun
    [13, 55, 63, 22, 36, 37, 30, 49],  # lower Li
    [10, 54, 60, 41, 19, 61, 38, 58],  # lower Dui
]

NAMES = {
    1: "The Creative", 2: "The Receptive", 3: "Difficulty at the Beginning",
    4: "Youthful Folly", 5: "Waiting", 6: "Conflict", 7: "The Army",
    8: "Holding Together", 9: "Small Taming", 10: "Treading", 11: "Peace",
    12: "Standstill", 13: "Fellowship", 14: "Great Possession", 15: "Modesty",
    16: "Enthusiasm", 17: "Following", 18: "Work on the Decayed", 19: "Approach",
    20: "Contemplation", 21: "Biting Through", 22: "Grace", 23: "Splitting Apart",
    24: "Return", 25: "Innocence", 26: "Great Taming", 27: "Nourishment",
    28: "Great Exceeding", 29: "The Abysmal (Water)", 30: "The Clinging (Fire)",
    31: "Influence", 32: "Duration", 33: "Retreat", 34: "Great Power",
    35: "Progress", 36: "Darkening of the Light", 37: "The Family",
    38: "Opposition", 39: "Obstruction", 40: "Deliverance", 41: "Decrease",
    42: "Increase", 43: "Breakthrough", 44: "Coming to Meet",
    45: "Gathering Together", 46: "Pushing Upward", 47: "Oppression",
    48: "The Well", 49: "Revolution", 50: "The Cauldron",
    51: "The Arousing (Thunder)", 52: "Keeping Still (Mountain)",
    53: "Development", 54: "The Marrying Maiden", 55: "Abundance",
    56: "The Wanderer", 57: "The Gentle (Wind)", 58: "The Joyous (Lake)",
    59: "Dispersion", 60: "Limitation", 61: "Inner Truth", 62: "Small Exceeding",
    63: "After Completion", 64: "Before Completion",
}


def _build_binary_map() -> dict[str, int]:
    out: dict[str, int] = {}
    for li, lower in enumerate(_ORDER):
        for ui, upper in enumerate(_ORDER):
            binary = TRIGRAM_BITS[lower] + TRIGRAM_BITS[upper]  # bottom-to-top
            out[binary] = _KINGWEN[li][ui]
    return out


BINARY_TO_NUMBER = _build_binary_map()
