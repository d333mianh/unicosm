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

    def sign(self, body: str) -> str:
        if body == "Asc":
            return ephem.sign_name(self.asc)
        return ephem.sign_name(self.planets[body])


def compute_natal(p: Profile) -> NatalChart:
    jd = ephem.jd_ut(p.birth_dt)
    planets = {name: ephem.planet_lon(jd, ipl)[0] for name, ipl in ephem.PLANETS.items()}
    asc = ephem.ascendant(jd, p.birth_lat, p.birth_lon)
    return NatalChart(planets=planets, asc=asc, jd=jd)


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
