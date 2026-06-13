"""Core data models shared across the engine.

Two organizing axes (from complementary-systems-v2.md):

* **Functional layer** — where the system draws its input from:
  blueprint (birth only), personal (birth x today), cosmic (today only),
  ondemand (user-initiated divination).
* **Cadence** — the rhythm a system speaks on. Each system occupies a
  different cadence slot, which is *why* they complement rather than contradict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Cadence(str, Enum):
    BLUEPRINT = "blueprint"      # fixed, does not move with time
    HOURLY = "hourly"
    DAILY = "daily"
    LUNAR_MONTH = "lunar_month"
    SEASON = "season"
    YEAR = "year"
    DECADE = "decade"
    ERA = "era"


# Display order for the moving layers (blueprint is rendered on its own).
CADENCE_ORDER: list[Cadence] = [
    Cadence.HOURLY,
    Cadence.DAILY,
    Cadence.LUNAR_MONTH,
    Cadence.SEASON,
    Cadence.YEAR,
    Cadence.DECADE,
    Cadence.ERA,
]

CADENCE_LABEL: dict[Cadence, str] = {
    Cadence.BLUEPRINT: "Blueprint",
    Cadence.HOURLY: "This hour",
    Cadence.DAILY: "Today",
    Cadence.LUNAR_MONTH: "This lunar month",
    Cadence.SEASON: "This season",
    Cadence.YEAR: "This year",
    Cadence.DECADE: "This chapter",
    Cadence.ERA: "This era",
}


class Layer(str, Enum):
    BLUEPRINT = "blueprint"
    PERSONAL = "personal"
    COSMIC = "cosmic"
    ONDEMAND = "ondemand"


@dataclass
class SystemReading:
    """The structured output of one system for one moment.

    `summary` is a single deterministic plain-language line. `detail` holds the
    raw structured values. `keywords` are the themes the synthesis layer weaves
    together. `score` is an optional favorability for the moment in [-1, 1].
    """

    key: str
    title: str
    cadence: Cadence
    layer: Layer
    summary: str
    detail: dict = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    score: float | None = None


@dataclass
class Profile:
    """A person. Birth data is fixed; current location can differ from birth."""

    name: str
    birth_dt: datetime          # timezone-aware, in birth_tz
    birth_lat: float
    birth_lon: float
    birth_tz: str
    cur_lat: float
    cur_lon: float
    cur_tz: str

    @property
    def birth_label(self) -> str:
        return self.birth_dt.strftime("%Y-%m-%d %H:%M %Z")


@dataclass
class Habit:
    """A user-defined practice the engine times into the day and tracks."""

    id: int
    name: str
    # preferred window key (see routine.windows), or None = engine picks/anytime
    window: str | None
    # target cadence of repetition, currently informational
    cadence: str = "daily"
    active: bool = True
