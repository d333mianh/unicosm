"""Terminal rendering for the `today` reading and routine."""

from __future__ import annotations

import os
import sys

from .models import CADENCE_LABEL, CADENCE_ORDER, Cadence, SystemReading
from .routine.scheduler import RoutineBlock
from .synthesis.weave import Synthesis

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if _COLOR else s


def bold(s: str) -> str:
    return _c("1", s)


def dim(s: str) -> str:
    return _c("2", s)


def accent(s: str) -> str:
    return _c("36", s)


def header(profile, now) -> str:
    line1 = bold(f"☉ Unicosm — {profile.name}")
    line2 = f"{now:%A, %d %B %Y · %H:%M %Z}"
    line3 = dim(f"born {profile.birth_label}  ·  {profile.birth_lat:.2f}, {profile.birth_lon:.2f}")
    return f"{line1}\n  {line2}\n  {line3}"


def cosmic_state(syn: Synthesis, woven: str | None) -> str:
    out = [bold("\n  COSMIC STATE  ") + dim(f"({syn.weather})")]
    out.append(f"  {syn.headline}")
    if syn.keywords:
        out.append(dim(f"  themes: {', '.join(syn.keywords)}"))
    if woven:
        out.append("")
        for line in _wrap(woven, 76):
            out.append(f"  {line}")
    return "\n".join(out)


_LABEL_W = 18


def layers(readings: list[SystemReading]) -> str:
    by_cadence: dict[Cadence, list[SystemReading]] = {}
    for r in readings:
        by_cadence.setdefault(r.cadence, []).append(r)

    out = [bold("\n  LAYERS")]
    for cad in CADENCE_ORDER:
        items = by_cadence.get(cad)
        if not items:
            continue
        label = CADENCE_LABEL[cad]
        for i, r in enumerate(items):
            tag = accent(f"{label:<{_LABEL_W}}") if i == 0 else " " * _LABEL_W
            out.append(f"  {tag}{r.summary}")
    # blueprint last
    bp = by_cadence.get(Cadence.BLUEPRINT)
    if bp:
        for i, r in enumerate(bp):
            tag = accent(f"{'Blueprint':<{_LABEL_W}}") if i == 0 else " " * _LABEL_W
            out.append(f"  {tag}{r.summary}")
    return "\n".join(out)


def accents(syn: Synthesis) -> str:
    if not syn.accents:
        return ""
    out = [bold("\n  ACCENTS FOR TODAY")]
    for a in syn.accents:
        out.append(f"   • {a}")
    return "\n".join(out)


def routine(blocks: list[RoutineBlock], show_empty: bool) -> str:
    out = [bold("\n  ROUTINE")]
    any_rows = False
    for b in blocks:
        has = bool(b.habits)
        if not has and not show_empty:
            continue
        any_rows = True
        marker = accent(" ▶") if b.is_now else "  "
        time = f"{b.time_label:<13}"
        title = b.window.label
        head = f"{marker} {dim(time)} {bold(title)}  {dim(b.window.note)}"
        out.append(head)
        for sh in b.habits:
            box = "☑" if sh.done else "☐"
            streak = dim(f"  🔥{sh.streak}") if sh.streak else ""
            out.append(f"        {box} {sh.habit.name}  {dim(f'(#{sh.habit.id})')}{streak}")
    if not any_rows:
        out.append(dim("   (no habits yet — add one: unicosm habit add \"Meditate\" --window brahma_muhurta)"))
    return "\n".join(out)


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines
