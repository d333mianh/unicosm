"""Day timing bands — Rahu Kalam, Yamaganda, Gulika, Abhijit, and Choghadiya.

All derived from sunrise/sunset + weekday. These are the auspicious/inauspicious
windows the routine layer uses to pick (and avoid) times of day.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..core import ephem
from ..core.timeutil import local_midnight
from ..data.panchang import (
    CHOGHADIYA_CYCLE,
    CHOGHADIYA_DAY_START,
    CHOGHADIYA_NIGHT_START,
    CHOGHADIYA_QUALITY,
    GULIKA_PART,
    RAHU_PART,
    YAMA_PART,
)


@dataclass
class Band:
    label: str
    start: datetime
    end: datetime
    quality: str = "neutral"     # good | neutral | bad
    note: str = ""

    def contains(self, t: datetime) -> bool:
        return self.start <= t < self.end

    @property
    def time_label(self) -> str:
        return f"{self.start:%H:%M}–{self.end:%H:%M}"


@dataclass
class DayTiming:
    sunrise: datetime | None
    sunset: datetime | None
    inauspicious: list[Band] = field(default_factory=list)   # rahu/yama/gulika
    abhijit: Band | None = None
    day_choghadiya: list[Band] = field(default_factory=list)
    night_choghadiya: list[Band] = field(default_factory=list)

    def all_choghadiya(self) -> list[Band]:
        return self.day_choghadiya + self.night_choghadiya

    def current_choghadiya(self, t: datetime) -> Band | None:
        for b in self.all_choghadiya():
            if b.contains(t):
                return b
        return None

    def active_inauspicious(self, t: datetime) -> Band | None:
        for b in self.inauspicious:
            if b.contains(t):
                return b
        return None

    def good_windows(self) -> list[Band]:
        return [b for b in self.day_choghadiya if b.quality == "good"]


def _choghadiya_bands(start: datetime, end: datetime, start_idx: int) -> list[Band]:
    span = (end - start) / 8
    bands: list[Band] = []
    for i in range(8):
        name = CHOGHADIYA_CYCLE[(start_idx + i) % 7]
        quality, note = CHOGHADIYA_QUALITY[name]
        s = start + span * i
        bands.append(Band(f"Choghadiya {name}", s, s + span, quality, note))
    return bands


def compute(ctx) -> DayTiming:
    lat, lon, tz = ctx.lat, ctx.lon, ctx.cur_tz
    jd0 = ephem.jd_ut(local_midnight(ctx.now))
    sr = ephem.next_sunrise(jd0, lat, lon)
    ss = ephem.next_sunset(jd0, lat, lon)
    if sr is None or ss is None:
        return DayTiming(sunrise=None, sunset=None)

    sunrise = ephem.jd_to_datetime(sr, tz)
    sunset = ephem.jd_to_datetime(ss, tz)
    nxt = ephem.next_sunrise(jd0 + 1, lat, lon)
    next_sunrise = ephem.jd_to_datetime(nxt, tz) if nxt else sunset + timedelta(hours=10)

    wd = ctx.now.weekday()
    part = (sunset - sunrise) / 8

    def part_band(label: str, n: int, quality: str, note: str) -> Band:
        s = sunrise + part * (n - 1)
        return Band(label, s, s + part, quality, note)

    inauspicious = [
        part_band("Rahu Kalam", RAHU_PART[wd], "bad", "avoid new beginnings"),
        part_band("Yamaganda", YAMA_PART[wd], "bad", "avoid important work"),
        part_band("Gulika Kalam", GULIKA_PART[wd], "bad", "weak for new starts"),
    ]

    muhurta = (sunset - sunrise) / 15
    abhijit = Band("Abhijit muhurta", sunrise + muhurta * 7, sunrise + muhurta * 8,
                   "good", "midday victory window — auspicious for most acts")

    day_ch = _choghadiya_bands(sunrise, sunset, CHOGHADIYA_DAY_START[wd])
    night_ch = _choghadiya_bands(sunset, next_sunrise, CHOGHADIYA_NIGHT_START[wd])

    return DayTiming(sunrise, sunset, inauspicious, abhijit, day_ch, night_ch)
