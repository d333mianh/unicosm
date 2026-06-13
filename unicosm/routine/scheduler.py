"""Assemble the day's routine: habits placed into their windows, with status."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..models import Habit
from .timing import DayTiming
from .tracker import current_streak
from .windows import Window, day_windows


@dataclass
class ScheduledHabit:
    habit: Habit
    done: bool
    streak: int


@dataclass
class RoutineBlock:
    window: Window
    start: datetime | None
    end: datetime | None
    habits: list[ScheduledHabit] = field(default_factory=list)
    is_now: bool = False
    timing_note: str = ""

    @property
    def time_label(self) -> str:
        if self.start is None or self.end is None:
            return "—"
        return f"{self.start:%H:%M}–{self.end:%H:%M}"


def _overlap(a0, a1, b0, b1) -> bool:
    return a0 < b1 and b0 < a1


def _timing_note(start, end, dt: DayTiming | None) -> str:
    """A daily accent for a window from the auspicious/inauspicious bands."""
    if dt is None or start is None or end is None or dt.sunrise is None:
        return ""
    for bad in dt.inauspicious:
        if _overlap(start, end, bad.start, bad.end):
            return f"⚠ overlaps {bad.label} — {bad.note}"
    if dt.abhijit and _overlap(start, end, dt.abhijit.start, dt.abhijit.end):
        return "✓ Abhijit muhurta — auspicious"
    mid = start + (end - start) / 2
    ch = dt.current_choghadiya(mid)
    if ch and ch.quality == "good":
        return f"✓ {ch.label} — {ch.note}"
    if ch and ch.quality == "bad":
        return f"~ {ch.label} — {ch.note}"
    return ""


def build_routine(ctx, habits: list[Habit], done_ids: set[int],
                  day_timing: DayTiming | None = None) -> list[RoutineBlock]:
    today = ctx.now.date()
    # group habits by window key (unknown/None -> anytime)
    by_window: dict[str, list[Habit]] = {}
    valid = {w.key for w, _, _ in day_windows(ctx)}
    for h in habits:
        key = h.window if h.window in valid else "anytime"
        by_window.setdefault(key, []).append(h)

    blocks: list[RoutineBlock] = []
    for window, start, end in day_windows(ctx):
        hs = [
            ScheduledHabit(
                habit=h, done=h.id in done_ids,
                streak=current_streak(h.id, today),
            )
            for h in by_window.get(window.key, [])
        ]
        is_now = bool(start and end and start <= ctx.now <= end)
        note = "" if window.key == "anytime" else _timing_note(start, end, day_timing)
        blocks.append(RoutineBlock(window, start, end, hs, is_now, note))
    return blocks
