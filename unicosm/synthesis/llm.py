"""Optional LLM enhancement.

If the `anthropic` package is installed and ANTHROPIC_API_KEY is set, weave the
structured readings into a richer single narrative. Always degrades gracefully:
any problem returns None and the deterministic synthesis stands.
"""

from __future__ import annotations

import json
import os

from ..models import SystemReading
from .weave import Synthesis

DEFAULT_MODEL = os.environ.get("UNICOSM_LLM_MODEL", "claude-opus-4-8")

_SYSTEM = (
    "You are the synthesis voice of Unicosm. You receive structured readings "
    "from many complementary guidance traditions, each already mapped to a "
    "cadence (hourly, daily, lunar month, season, year, decade, era). Weave "
    "them into ONE short, grounded, second-person reading (max ~180 words). "
    "Treat the systems as complementary lenses, never contradictory. Do not "
    "invent facts beyond the data. End with one concrete suggestion for today. "
    "Avoid fatalism; keep agency with the reader."
)


def enhance(readings: list[SystemReading], base: Synthesis) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None

    payload = {
        "weather": base.weather,
        "keywords": base.keywords,
        "readings": [
            {"cadence": r.cadence.value, "title": r.title,
             "summary": r.summary, "keywords": r.keywords}
            for r in readings
        ],
    }
    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=600,
            system=_SYSTEM,
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    except Exception:
        return None
