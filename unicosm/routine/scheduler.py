"""Assemble the day's routine: habits placed into their windows, with status."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..models import Habit
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

    @property
    def time_label(self) -> str:
        if self.start is None or self.end is None:
            return "—"
        return f"{self.start:%H:%M}–{self.end:%H:%M}"


def build_routine(ctx, habits: list[Habit], done_ids: set[int]) -> list[RoutineBlock]:
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
        blocks.append(RoutineBlock(window, start, end, hs, is_now))
    return blocks
