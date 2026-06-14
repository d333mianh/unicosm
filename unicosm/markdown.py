"""Render a DailyReport as Obsidian-friendly Markdown.

The body is wrapped between markers so re-running replaces the block in a daily
note instead of duplicating it.
"""

from __future__ import annotations

from .engine import DailyReport
from .models import CADENCE_LABEL, CADENCE_ORDER, Cadence

MARK_START = "<!-- unicosm:start -->"
MARK_END = "<!-- unicosm:end -->"


def frontmatter(rep: DailyReport) -> str:
    mp = next((r for r in rep.readings if r.key == "moon_phase"), None)
    moon = mp.detail.get("phase", "") if mp else ""
    kw = ", ".join(rep.synthesis.keywords)
    return (
        "---\n"
        f"date: {rep.now:%Y-%m-%d}\n"
        f"unicosm_weather: \"{rep.synthesis.weather}\"\n"
        f"moon_phase: \"{moon}\"\n"
        f"unicosm_themes: [{kw}]\n"
        "---\n"
    )


def body(rep: DailyReport) -> str:
    s = rep.synthesis
    out: list[str] = [f"## ☉ Unicosm — {rep.now:%A, %d %B %Y}", ""]
    out.append(f"> *{s.weather}* — {s.headline}")
    out.append("")
    if s.keywords:
        out.append(f"**Themes:** {', '.join(s.keywords)}")
    for res in s.resonances:
        out.append(f"- ↻ {res}")
    for tn in s.tensions:
        out.append(f"- ⚖ {tn}")
    out.append("")

    if rep.woven:
        out += ["### Reading", "", rep.woven, ""]

    # layers grouped by cadence
    out.append("### Layers")
    by_cad: dict[Cadence, list] = {}
    for r in rep.readings:
        by_cad.setdefault(r.cadence, []).append(r)
    for cad in CADENCE_ORDER + [Cadence.BLUEPRINT]:
        items = by_cad.get(cad)
        if not items:
            continue
        out.append(f"- **{CADENCE_LABEL[cad]}**")
        for r in items:
            out.append(f"    - {r.summary}")
    out.append("")

    # timing
    dt = rep.timing
    if dt and dt.sunrise:
        out.append("### Today's timing")
        out.append(f"- Sun {dt.sunrise:%H:%M}–{dt.sunset:%H:%M} · "
                   f"Abhijit {dt.abhijit.time_label}")
        good = "  ".join(f"{b.start:%H:%M} {b.label.split()[-1]}"
                         for b in dt.good_windows())
        if good:
            out.append(f"- Favor: {good}")
        avoid = "  ".join(f"{b.start:%H:%M}–{b.end:%H:%M} {b.label.split()[0]}"
                          for b in dt.inauspicious)
        out.append(f"- Avoid: {avoid}")
        out.append("")

    # accents + routine
    if s.accents:
        out.append("### Accents")
        out += [f"- {a}" for a in s.accents]
        out.append("")
    rows = [b for b in rep.routine if b.habits]
    if rows:
        out.append("### Routine")
        for b in rows:
            note = f"  _{b.timing_note}_" if b.timing_note else ""
            out.append(f"- **{b.window.label}** ({b.time_label}){note}")
            for sh in b.habits:
                box = "x" if sh.done else " "
                streak = f" 🔥{sh.streak}" if sh.streak else ""
                out.append(f"    - [{box}] {sh.habit.name}{streak}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def block(rep: DailyReport) -> str:
    return f"{MARK_START}\n{body(rep)}{MARK_END}\n"
