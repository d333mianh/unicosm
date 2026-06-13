"""DayContext — everything a system needs for one reading, computed once."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from . import core
from .core import ephem
from .core.timeutil import now_in
from .models import Profile


@dataclass
class NatalChart:
    """Fixed birth positions (tropical)."""

    planets: dict[str, float]   # name -> ecliptic longitude
    asc: float
    jd: float
    cusps: tuple[float, ...] = ()   # 12 house cusps (Placidus)
    mc: float = 0.0                 # Midheaven

    def sign(self, body: str) -> str:
        if body == "Asc":
            return ephem.sign_name(self.asc)
        if body == "MC":
            return ephem.sign_name(self.mc)
        return ephem.sign_name(self.planets[body])

    def house_of(self, lon: float) -> int:
        """House (1-12) containing the given longitude, by the natal cusps."""
        if not self.cusps:
            return 0
        ring = list(self.cusps) + [self.cusps[0]]
        for i in range(12):
            a, b = ring[i], ring[i + 1]
            if a <= b:
                if a <= lon < b:
                    return i + 1
            elif lon >= a or lon < b:   # cusp wraps past 360°
                return i + 1
        return 12


def compute_natal(p: Profile) -> NatalChart:
    jd = ephem.jd_ut(p.birth_dt)
    planets = {name: ephem.planet_lon(jd, ipl)[0] for name, ipl in ephem.PLANETS.items()}
    cusps, asc, mc = ephem.houses(jd, p.birth_lat, p.birth_lon)
    return NatalChart(planets=planets, asc=asc, jd=jd, cusps=cusps, mc=mc)


@dataclass
class DayContext:
    profile: Profile
    now: datetime               # aware, in current tz
    natal: NatalChart
    jd_now: float = field(init=False)

    def __post_init__(self) -> None:
        self.jd_now = ephem.jd_ut(self.now)

    @property
    def cur_tz(self) -> ZoneInfo:
        return ZoneInfo(self.profile.cur_tz)

    @property
    def lat(self) -> float:
        return self.profile.cur_lat

    @property
    def lon(self) -> float:
        return self.profile.cur_lon


def build_context(profile: Profile, now: datetime | None = None) -> DayContext:
    when = now or now_in(profile.cur_tz)
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(profile.cur_tz))
    return DayContext(profile=profile, now=when, natal=compute_natal(profile))
