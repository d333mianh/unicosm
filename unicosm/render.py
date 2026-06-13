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
    for res in syn.resonances:
        out.append(f"  {accent('↻')} {res}")
    for tension in syn.tensions:
        out.append(f"  {accent('⚖')} {tension}")
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


def timing(dt, now) -> str:
    """The day's auspicious / inauspicious time-bands."""
    if dt is None or dt.sunrise is None:
        return ""
    out = [bold("\n  TODAY'S TIMING")]
    out.append(f"  {dim('sun')} {dt.sunrise:%H:%M}–{dt.sunset:%H:%M}"
               f"   {dim('Abhijit')} {dt.abhijit.time_label}")

    cur = dt.current_choghadiya(now)
    bad = dt.active_inauspicious(now)
    if bad:
        out.append(f"  {accent('now')} ⚠ {bad.label} until {bad.end:%H:%M} — {bad.note}")
    elif cur:
        glyph = {"good": "✓", "neutral": "·", "bad": "~"}[cur.quality]
        out.append(f"  {accent('now')} {glyph} {cur.label} ({cur.note})")

    good = [b for b in dt.good_windows() if b.end > now]
    if good:
        windows = "  ".join(f"{b.start:%H:%M} {b.label.split()[-1]}" for b in good[:4])
        out.append(f"  {dim('favor ')} {windows}")
    avoid = "  ".join(f"{b.start:%H:%M}–{b.end:%H:%M} {b.label.split()[0]}"
                      for b in dt.inauspicious)
    out.append(f"  {dim('avoid ')} {avoid}")
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
        if b.timing_note:
            out.append(f"        {dim(b.timing_note)}")
        for sh in b.habits:
            box = "☑" if sh.done else "☐"
            streak = dim(f"  🔥{sh.streak}") if sh.streak else ""
            out.append(f"        {box} {sh.habit.name}  {dim(f'(#{sh.habit.id})')}{streak}")
    if not any_rows:
        out.append(dim("   (no habits yet — add one: unicosm habit add \"Meditate\" --window brahma_muhurta)"))
    return "\n".join(out)


def draw(system: str, rng, spread: bool) -> tuple[str, str]:
    """Return (rendered_text, one_line_summary) for a divination draw."""
    if system == "iching":
        return _draw_iching(rng)
    if system == "tarot":
        return _draw_tarot(rng, spread)
    if system == "runes":
        return _draw_runes(rng, spread)
    return f"unknown system: {system}", system


def _draw_iching(rng) -> tuple[str, str]:
    from .divination.iching import cast
    c = cast(rng)
    glyph = chr(0x4DC0 + c.primary - 1)
    out = [bold("\n  ☯ I Ching"), f"  {glyph}  {c.primary}. {c.primary_name}"]
    for i in range(5, -1, -1):                 # top line first
        v = c.lines[i]
        yang = v in (7, 9)
        bar = "▅▅▅▅▅▅▅" if yang else "▅▅▅   ▅▅▅"
        mark = accent("  ✦") if v in (6, 9) else ""
        out.append(f"      {bar}{mark}")
    summary = f"{c.primary}. {c.primary_name}"
    if c.relating:
        rg = chr(0x4DC0 + c.relating - 1)
        chg = ", ".join(map(str, c.changing_lines))
        out.append(f"   {dim('→')} {rg}  {c.relating}. {c.relating_name}"
                   f"  {dim(f'(changing lines {chg})')}")
        summary += f" → {c.relating}. {c.relating_name}"
    else:
        out.append(dim("   (no changing lines — a stable answer)"))
    return "\n".join(out), summary


def _draw_tarot(rng, spread: bool) -> tuple[str, str]:
    from .divination.tarot import draw_cards
    cards = draw_cards(rng, 3 if spread else 1)
    labels = ["Past", "Present", "Future"] if spread else ["Card"]
    out = [bold("\n  🃏 Tarot")]
    for label, card in zip(labels, cards):
        orient = "reversed" if card.reversed else "upright"
        kw = card.reversed_kw if card.reversed else card.upright_kw
        out.append(f"  {accent(label)}: {bold(card.name)} ({orient}) — {kw}")
    summary = "; ".join(
        f"{c.name}{' (rev)' if c.reversed else ''}" for c in cards)
    return "\n".join(out), summary


def _draw_runes(rng, spread: bool) -> tuple[str, str]:
    from .divination.runes import draw_runes
    runes = draw_runes(rng, 3 if spread else 1)
    labels = ["Situation", "Action", "Outcome"] if spread else ["Rune"]
    out = [bold("\n  ᚱ Runes")]
    for label, rune in zip(labels, runes):
        if rune.merkstave:
            out.append(f"  {accent(label)}: {bold(rune.name)} {rune.glyph} "
                       f"(merkstave) — {rune.reversed_meaning}")
        else:
            out.append(f"  {accent(label)}: {bold(rune.name)} {rune.glyph} "
                       f"— {rune.meaning}")
    summary = "; ".join(
        f"{r.name}{' (merk)' if r.merkstave else ''}" for r in runes)
    return "\n".join(out), summary


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
