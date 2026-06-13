"""Optional LLM enhancement.

If the `anthropic` package is installed and ANTHROPIC_API_KEY is set, weave the
structured readings — plus the deterministic resonances, tensions and per-cadence
favorability — into one richer narrative. Responses are cached on disk by input
hash so the same day/inputs don't re-bill. Always degrades to None on any
problem; the deterministic synthesis still stands.
"""

from __future__ import annotations

import hashlib
import json
import os

from ..config import data_dir
from ..models import SystemReading
from .weave import Synthesis

DEFAULT_MODEL = os.environ.get("UNICOSM_LLM_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.environ.get("UNICOSM_LLM_MAX_TOKENS", "600"))

_SYSTEM = (
    "You are the synthesis voice of Unicosm. You receive structured readings from "
    "many complementary guidance traditions, each mapped to a cadence (hourly, "
    "daily, lunar month, season, year, decade, era), plus pre-computed resonances "
    "(themes several systems echo) and tensions (where the day both supports and "
    "cautions). Weave them into ONE short, grounded, second-person reading (max "
    "~180 words). Lead with what the traditions agree on (the resonances). Treat "
    "the systems as complementary lenses, never contradictory; when a tension "
    "exists, hold both sides honestly. Don't invent facts beyond the data. End "
    "with one concrete suggestion for today. Avoid fatalism; keep agency with the "
    "reader."
)


def _payload(readings: list[SystemReading], base: Synthesis) -> dict:
    return {
        "weather": base.weather,
        "resonances": base.resonances,
        "tensions": base.tensions,
        "cadence_weather": base.cadence_weather,
        "readings": [
            {"cadence": r.cadence.value, "title": r.title,
             "summary": r.summary, "keywords": r.keywords}
            for r in readings
        ],
    }


def _cache_path(payload: dict) -> "os.PathLike":
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256((DEFAULT_MODEL + blob).encode()).hexdigest()[:32]
    cache = data_dir() / "llm_cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache / f"{digest}.txt"


def enhance(readings: list[SystemReading], base: Synthesis) -> str | None:
    payload = _payload(readings, base)
    path = _cache_path(payload)
    if path.exists():
        return path.read_text(encoding="utf-8")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=MAX_TOKENS,
            system=_SYSTEM,
            messages=[{"role": "user",
                       "content": json.dumps(payload, ensure_ascii=False)}],
        )
        text = "".join(b.text for b in msg.content
                       if getattr(b, "type", "") == "text").strip()
        if text:
            path.write_text(text, encoding="utf-8")
        return text or None
    except Exception:
        return None
