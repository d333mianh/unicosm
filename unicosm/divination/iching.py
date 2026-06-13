"""I Ching coin-oracle cast.

Three-coin method per line (heads=3, tails=2), bottom to top:
6 = old yin (changing), 7 = young yang, 8 = young yin, 9 = old yang (changing).
Changing lines transform the primary hexagram into the relating hexagram.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..data.iching import BINARY_TO_NUMBER, NAMES


@dataclass
class Cast:
    primary: int
    primary_name: str
    changing_lines: list[int]      # 1-based positions, bottom=1
    relating: int | None
    relating_name: str | None
    lines: list[int]               # the 6,7,8,9 values bottom-to-top


def cast(rng: random.Random | None = None) -> Cast:
    r = rng or random.Random()
    values = []
    for _ in range(6):
        coins = sum(3 if r.random() < 0.5 else 2 for _ in range(3))  # 6..9
        values.append(coins)

    primary_bits = "".join("1" if v in (7, 9) else "0" for v in values)
    primary = BINARY_TO_NUMBER[primary_bits]
    changing = [i + 1 for i, v in enumerate(values) if v in (6, 9)]

    relating = relating_name = None
    if changing:
        trans_bits = "".join(
            ("1" if v == 6 else "0" if v == 9 else b)
            for b, v in zip(primary_bits, values)
        )
        relating = BINARY_TO_NUMBER[trans_bits]
        relating_name = NAMES[relating]

    return Cast(primary, NAMES[primary], changing, relating, relating_name, values)
