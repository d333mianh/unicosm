"""High-level assembly: profile + moment -> readings, synthesis, routine.

Kept separate from the CLI so it can be reused (tests, a future API/UI)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from . import store
from .context import build_context
from .core.timeutil import civil_date
from .models import Profile, SystemReading
from .routine.scheduler import RoutineBlock, build_routine
from .routine.timing import DayTiming
from .routine.timing import compute as compute_timing
from .synthesis import llm
from .synthesis.weave import Synthesis, synthesize
from .systems import all_readings


@dataclass
class DailyReport:
    profile: Profile
    now: datetime
    readings: list[SystemReading]
    synthesis: Synthesis
    woven: str | None
    routine: list[RoutineBlock]
    timing: DayTiming


def daily_report(profile: Profile, now: datetime | None = None,
                 use_llm: bool = False) -> DailyReport:
    ctx = build_context(profile, now)
    readings = all_readings(ctx)
    syn = synthesize(readings)
    woven = llm.enhance(readings, syn) if use_llm else None
    habits = store.list_habits(profile.name)
    done = store.completions_for_day(profile.name, civil_date(ctx.now))
    timing = compute_timing(ctx)
    routine = build_routine(ctx, habits, done, timing)
    return DailyReport(profile, ctx.now, readings, syn, woven, routine, timing)
