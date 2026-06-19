"""Render a DailyReport into Telegram-ready HTML.

Telegram's HTML parse mode supports a small tag set (<b> <i> <code> <pre> <a>);
all dynamic text is escaped so a stray ``<`` in a place name can't break a
message. Messages are clipped to Telegram's 4096-character hard limit. Pure: no
network, no ANSI — the chat counterpart to the terminal `render` module.
"""

from __future__ import annotations

import html

from ..engine import DailyReport

MAX = 4096  # Telegram sendMessage hard limit (characters)


def esc(s: object) -> str:
    return html.escape(str(s), quote=False)


def _clip(text: str, limit: int = MAX) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _timing_now(rep: DailyReport) -> str | None:
    """A one-line 'right now' timing flag, mirroring notify.build_message."""
    dt = rep.timing
    if not dt or not dt.sunrise:
        return None
    bad = dt.active_inauspicious(rep.now)
    if bad:
        return f"⚠ {esc(bad.label)} until {bad.end:%H:%M}"
    cur = dt.current_choghadiya(rep.now)
    if cur and cur.quality == "good":
        return f"✓ good window now ({esc(cur.label.split()[-1])})"
    return None


def daily_message(rep: DailyReport) -> str:
    """The concise morning push (what `telegram send` dispatches)."""
    lines = [
        f"<b>☉ {esc(rep.profile.name)} · {rep.now:%a %d %b}</b>",
        "",
        esc(rep.synthesis.headline),
    ]
    if rep.synthesis.accents:
        lines.append("• " + esc(rep.synthesis.accents[0]))
    now = _timing_now(rep)
    if now:
        lines.append(now)
    return _clip("\n".join(lines))


def today_message(rep: DailyReport) -> str:
    """The full woven reading for /today."""
    s = rep.synthesis
    lines = [
        f"<b>☉ {esc(rep.profile.name)} — {rep.now:%A %d %B %Y · %H:%M}</b>",
        "",
        f"<b>Cosmic state</b> <i>({esc(s.weather)})</i>",
        esc(s.headline),
    ]
    if s.resonances:
        lines += ["", "<b>Echoed across systems</b>"]
        lines += ["↻ " + esc(r) for r in s.resonances[:3]]
    if s.accents:
        lines += ["", "<b>Accents for today</b>"]
        lines += ["• " + esc(a) for a in s.accents[:5]]
    dt = rep.timing
    if dt and dt.sunrise:
        lines += ["", "<b>Timing</b>",
                  f"🌅 {dt.sunrise:%H:%M}–{dt.sunset:%H:%M}"
                  + (f" · Abhijit {esc(dt.abhijit.time_label)}" if dt.abhijit else "")]
        if dt.inauspicious:
            avoid = ", ".join(f"{esc(b.label.split()[-1])} {esc(b.time_label)}"
                              for b in dt.inauspicious[:3])
            lines.append("avoid · " + avoid)
        now = _timing_now(rep)
        if now:
            lines.append(now)
    if rep.woven:
        lines += ["", "<b>✺ Reading</b>", esc(rep.woven)]
    return _clip("\n".join(lines))


def blueprint_message(rep: DailyReport) -> str:
    """The fixed birth signature for /blueprint."""
    lines = [f"<b>☉ {esc(rep.profile.name)} — blueprint</b>", ""]
    for r in rep.readings:
        if r.cadence.value == "blueprint":
            lines.append(f"<b>{esc(r.title)}</b>")
            lines.append(esc(r.summary))
            lines.append("")
    return _clip("\n".join(lines).rstrip())


def analysis_message(rep: DailyReport, warnings: list[str] | tuple[str, ...] = ()) -> str:
    """Reading another person's day (the /analyze flow)."""
    p = rep.profile
    s = rep.synthesis
    lines = [
        f"<b>🔮 {esc(p.name)}</b>",
        esc(f"born {p.birth_label} · {p.birth_lat:.2f}, {p.birth_lon:.2f}"),
        "",
        "<b>Signature</b>",
    ]
    bp = [r for r in rep.readings if r.cadence.value == "blueprint"]
    for r in bp[:6]:
        lines.append(f"• <b>{esc(r.title)}:</b> {esc(r.summary)}")
    lines += ["", f"<b>Their day</b> <i>({esc(s.weather)})</i>", esc(s.headline)]
    lines += ["• " + esc(a) for a in s.accents[:2]]
    if warnings:
        lines += ["", "<i>" + esc("note: " + "; ".join(warnings)) + "</i>"]
    return _clip("\n".join(lines))
