"""Habit completion tracking and streaks."""

from __future__ import annotations

from datetime import date, timedelta

from .. import store


def current_streak(habit_id: int, today: date) -> int:
    """Consecutive completed days ending today (or yesterday — a streak stays
    'alive' until a full day is missed)."""
    days = set(store.completion_days(habit_id))
    cursor = today
    if cursor.isoformat() not in days:
        cursor = today - timedelta(days=1)
        if cursor.isoformat() not in days:
            return 0
    streak = 0
    while cursor.isoformat() in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def window_stats(habit_id: int, today: date, days: int = 30) -> dict:
    """Completion count + rate over the last `days`, and lifetime total."""
    all_days = store.completion_days(habit_id)
    cutoff = today - timedelta(days=days - 1)
    recent = sum(1 for d in all_days if cutoff <= date.fromisoformat(d) <= today)
    return {"recent": recent, "days": days, "rate": recent / days,
            "total": len(all_days)}


def longest_streak(habit_id: int) -> int:
    days = sorted(store.completion_days(habit_id))
    if not days:
        return 0
    best = run = 1
    prev = date.fromisoformat(days[0])
    for d in days[1:]:
        cur = date.fromisoformat(d)
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
        prev = cur
    return best
