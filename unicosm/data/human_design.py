"""Human Design reference data.

Gate wheel order and the 2°00' Aquarius (302°) anchor verified against the
published Rave Mandala degree table. Channels and gate→center mapping are the
standard 64-gate / 36-channel / 9-center bodygraph.
"""

from __future__ import annotations

# The 64 gates in zodiacal order around the wheel, starting at Gate 41 = 302°.
GATE_WHEEL = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
    27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
    31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
    28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60,
]

WHEEL_START_DEG = 302.0          # 2°00' Aquarius
GATE_ARC = 360.0 / 64            # 5.625°
LINE_ARC = GATE_ARC / 6          # 0.9375°

# The nine centers and the gates that belong to each.
CENTER_GATES = {
    "Head": [64, 61, 63],
    "Ajna": [47, 24, 4, 17, 43, 11],
    "Throat": [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
    "G": [7, 1, 13, 25, 46, 2, 15, 10],
    "Heart": [21, 40, 26, 51],
    "Spleen": [48, 57, 44, 50, 32, 28, 18],
    "Sacral": [5, 14, 29, 59, 9, 3, 42, 27, 34],
    "Solar Plexus": [36, 22, 37, 6, 49, 55, 30],
    "Root": [58, 38, 54, 53, 60, 52, 19, 39, 41],
}

GATE_CENTER = {g: c for c, gs in CENTER_GATES.items() for g in gs}

CENTER_LABEL = {
    "G": "G (Identity)", "Heart": "Heart (Ego/Will)",
    "Solar Plexus": "Solar Plexus (Emotion)",
}

# Pressure/awareness/motor classification used for type & authority.
MOTORS = {"Sacral", "Solar Plexus", "Heart", "Root"}

# The 36 channels as gate pairs.
CHANNELS = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31),
    (9, 52), (10, 20), (10, 34), (10, 57), (11, 56), (12, 22),
    (13, 33), (16, 48), (17, 62), (18, 58), (19, 49), (20, 34),
    (20, 57), (21, 45), (23, 43), (24, 61), (25, 51), (26, 44),
    (27, 50), (28, 38), (29, 46), (30, 41), (32, 54), (34, 57),
    (35, 36), (37, 40), (39, 55), (42, 53), (47, 64),
]

PROFILE_LINE = {
    1: "Investigator", 2: "Hermit", 3: "Martyr",
    4: "Opportunist", 5: "Heretic", 6: "Role Model",
}
