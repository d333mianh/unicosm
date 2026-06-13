"""24 Solar Terms (jieqi) — the seasonal layer.

The Sun's tropical longitude in 15° steps. Term 0 = Lìchūn (Start of Spring)
at 315°. Seasonal micro-guidance for energy, food, and activity.
"""

from __future__ import annotations

from ..core import ephem
from ..models import Cadence, Layer, SystemReading

# (pinyin, english) in order starting at 315° = Lichun.
TERMS = [
    ("Lìchūn", "Start of Spring"), ("Yǔshuǐ", "Rain Water"),
    ("Jīngzhé", "Awakening of Insects"), ("Chūnfēn", "Spring Equinox"),
    ("Qīngmíng", "Pure Brightness"), ("Gǔyǔ", "Grain Rain"),
    ("Lìxià", "Start of Summer"), ("Xiǎomǎn", "Grain Buds"),
    ("Mángzhòng", "Grain in Ear"), ("Xiàzhì", "Summer Solstice"),
    ("Xiǎoshǔ", "Minor Heat"), ("Dàshǔ", "Major Heat"),
    ("Lìqiū", "Start of Autumn"), ("Chùshǔ", "End of Heat"),
    ("Báilù", "White Dew"), ("Qiūfēn", "Autumn Equinox"),
    ("Hánlù", "Cold Dew"), ("Shuāngjiàng", "Frost's Descent"),
    ("Lìdōng", "Start of Winter"), ("Xiǎoxuě", "Minor Snow"),
    ("Dàxuě", "Major Snow"), ("Dōngzhì", "Winter Solstice"),
    ("Xiǎohán", "Minor Cold"), ("Dàhán", "Major Cold"),
]

SEASON_KW = {
    "spring": ["sprout", "begin outward"], "summer": ["expand", "express"],
    "autumn": ["harvest", "consolidate"], "winter": ["conserve", "go inward"],
}


def _season(idx: int) -> str:
    return ["spring", "spring", "spring", "spring", "spring", "spring",
            "summer", "summer", "summer", "summer", "summer", "summer",
            "autumn", "autumn", "autumn", "autumn", "autumn", "autumn",
            "winter", "winter", "winter", "winter", "winter", "winter"][idx]


def reading(ctx) -> SystemReading:
    sun_lon, _ = ephem.planet_lon(ctx.jd_now, ephem.PLANETS["Sun"])
    idx = int(((sun_lon - 315) % 360) // 15)
    pinyin, english = TERMS[idx]
    season = _season(idx)
    progress = (((sun_lon - 315) % 360) % 15) / 15
    kw = SEASON_KW[season]
    return SystemReading(
        key="solar_term",
        title="Solar term (jieqi)",
        cadence=Cadence.SEASON,
        layer=Layer.COSMIC,
        summary=(
            f"{english} ({pinyin}), {progress*100:.0f}% through — "
            f"deep {season}; the qi asks you to {kw[0]}."
        ),
        detail={"term": english, "pinyin": pinyin, "season": season,
                "progress": round(progress, 2)},
        keywords=kw,
    )
