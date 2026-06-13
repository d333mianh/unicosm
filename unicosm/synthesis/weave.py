"""Deterministic synthesis.

Always available, offline, reproducible. Produces a headline 'cosmic state', a
qualitative favorability, a theme cloud, and a short list of actionable accents
that layer on top of the user's stable routine. An LLM may optionally rewrite
the prose (see synthesis.llm), but never the underlying structured facts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from ..models import SystemReading


@dataclass
class Synthesis:
    headline: str
    weather: str
    accents: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


def _by_key(readings: list[SystemReading]) -> dict[str, SystemReading]:
    return {r.key: r for r in readings}


def _weather(readings: list[SystemReading]) -> str:
    scores = [r.score for r in readings if r.score is not None]
    if not scores:
        return "mixed"
    avg = sum(scores) / len(scores)
    if avg > 0.3:
        return "supportive — momentum is with you"
    if avg > 0.05:
        return "mildly favorable — proceed with intention"
    if avg > -0.05:
        return "neutral and mixed — let context decide"
    return "inward and cautious — conserve, don't force"


def _keywords(readings: list[SystemReading], n: int = 6) -> list[str]:
    c: Counter[str] = Counter()
    for r in readings:
        c.update(r.keywords)
    return [w for w, _ in c.most_common(n)]


def synthesize(readings: list[SystemReading]) -> Synthesis:
    r = _by_key(readings)
    sx = r.get("sexagenary")
    mp = r.get("moon_phase")
    pd = r.get("numerology_personal_day")
    ph = r.get("planetary_hours")
    st = r.get("solar_term")
    prof = r.get("profections")
    pt = r.get("panchang_timing")

    # Headline weaves the daily signature + lunar mood + personal-day intent.
    parts: list[str] = []
    if sx:
        parts.append(f"{sx.detail.get('stem_element', 'a day')} day")
    if mp:
        parts.append(f"under a {mp.detail['phase'].lower()}")
    head = " ".join(parts).capitalize() if parts else "Today"
    if pd:
        head += (f": Personal Day {pd.detail['personal_day']} "
                 f"({pd.detail['theme']})")
    if mp and not mp.detail.get("waxing", True):
        head += " — the Moon counsels restoration toward evening"
    head += "."

    accents: list[str] = []
    if pd:
        acts = pd.detail.get("actions", [])
        if acts:
            accents.append(f"Lean into: {', '.join(acts[:2])} (Personal Day "
                           f"{pd.detail['personal_day']}).")
    if mp:
        verb = "build toward your aim" if mp.detail.get("waxing") else "clear and release"
        accents.append(f"{mp.detail['phase']}: a good day to {verb}.")
    if ph:
        kw = ph.keywords[:2]
        if kw:
            accents.append(f"Right now — hour of {ph.detail.get('ruler')}: "
                           f"window for {', '.join(kw)}.")
    if st:
        accents.append(f"Season ({st.detail['term']}): {st.keywords[0]} with the qi.")
    if prof:
        accents.append(f"Year's theme — keep {prof.detail['topic'].split(',')[0]} "
                       f"in view (Lord: {prof.detail['lord']}).")
    if pt and pt.detail.get("inauspicious_now"):
        accents.append(f"Timing — {pt.detail['inauspicious_now']} now; "
                       f"hold big starts (Abhijit at {pt.detail.get('abhijit', '')}).")

    return Synthesis(
        headline=head,
        weather=_weather(readings),
        accents=accents,
        keywords=_keywords(readings),
    )
