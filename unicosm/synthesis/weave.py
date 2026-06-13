"""Deterministic synthesis.

Always available, offline, reproducible. Treats the many systems as
complementary lenses: it detects *resonances* (themes several traditions echo
independently — the heart of the 'complementary' idea), surfaces genuine
*tensions* (where the day supports and cautions at once), grades favorability per
cadence, and lists actionable accents on top of the user's routine.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from ..models import CADENCE_LABEL, Cadence, SystemReading


@dataclass
class Synthesis:
    headline: str
    weather: str
    accents: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    resonances: list[str] = field(default_factory=list)
    tensions: list[str] = field(default_factory=list)
    cadence_weather: dict[str, str] = field(default_factory=dict)


def _by_key(readings: list[SystemReading]) -> dict[str, SystemReading]:
    return {r.key: r for r in readings}


def _weather_label(avg: float) -> str:
    if avg > 0.3:
        return "supportive — momentum is with you"
    if avg > 0.05:
        return "mildly favorable — proceed with intention"
    if avg > -0.05:
        return "neutral and mixed — let context decide"
    return "inward and cautious — conserve, don't force"


def _weather(readings: list[SystemReading]) -> str:
    scores = [r.score for r in readings if r.score is not None]
    return _weather_label(sum(scores) / len(scores)) if scores else "mixed"


def _cadence_weather(readings: list[SystemReading]) -> dict[str, str]:
    buckets: dict[Cadence, list[float]] = defaultdict(list)
    for r in readings:
        if r.score is not None:
            buckets[r.cadence].append(r.score)
    out: dict[str, str] = {}
    for cad, scores in buckets.items():
        avg = sum(scores) / len(scores)
        tone = "supportive" if avg > 0.1 else "cautious" if avg < -0.1 else "mixed"
        out[CADENCE_LABEL[cad]] = tone
    return out


def _resonances(readings: list[SystemReading]) -> list[str]:
    """Themes independently echoed by 3+ systems."""
    where: dict[str, list[str]] = defaultdict(list)
    for r in readings:
        for kw in r.keywords:
            where[kw].append(r.title)
    out = []
    for kw, titles in sorted(where.items(), key=lambda x: -len(x[1])):
        if len(titles) >= 3:
            out.append(f"{kw} — echoed by {len(titles)} systems")
    return out[:4]


def _tensions(readings: list[SystemReading]) -> list[str]:
    pos = [r for r in readings if r.score is not None and r.score > 0.3]
    neg = [r for r in readings if r.score is not None and r.score < -0.3]
    if pos and neg:
        p = max(pos, key=lambda r: r.score)
        n = min(neg, key=lambda r: r.score)
        return [f"{p.title} opens while {n.title} cautions — hold both"]
    return []


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
    resonances = _resonances(readings)

    parts: list[str] = []
    if sx:
        parts.append(f"{sx.detail.get('stem_element', 'a day')} day")
    if mp:
        parts.append(f"under a {mp.detail['phase'].lower()}")
    head = " ".join(parts).capitalize() if parts else "Today"
    if pd:
        head += f": Personal Day {pd.detail['personal_day']} ({pd.detail['theme']})"
    if resonances:
        head += f" — many systems echo {resonances[0].split(' — ')[0]}"
    elif mp and not mp.detail.get("waxing", True):
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
    if ph and ph.keywords[:2]:
        accents.append(f"Right now — hour of {ph.detail.get('ruler')}: "
                       f"window for {', '.join(ph.keywords[:2])}.")
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
        resonances=resonances,
        tensions=_tensions(readings),
        cadence_weather=_cadence_weather(readings),
    )
