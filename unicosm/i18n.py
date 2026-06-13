"""Minimal i18n.

English-first. Strings flow through ``t()``, which resolves against a per-locale
catalog (set $UNICOSM_LOCALE). Only UI chrome + cadence labels are translated so
far — system reading text is still English. The seam is real; filling catalogs
is incremental.
"""

from __future__ import annotations

import os

LOCALE = os.environ.get("UNICOSM_LOCALE", "en")

# locale -> {english string: translation}
CATALOGS: dict[str, dict[str, str]] = {
    "uk": {
        # section headers
        "COSMIC STATE": "КОСМІЧНИЙ СТАН",
        "LAYERS": "ШАРИ",
        "ACCENTS FOR TODAY": "АКЦЕНТИ НА СЬОГОДНІ",
        "TODAY'S TIMING": "ТАЙМІНГ ДНЯ",
        "ROUTINE": "РУТИНА",
        "BLUEPRINT": "КРЕСЛЕННЯ",
        # cadence labels
        "Blueprint": "Креслення",
        "This hour": "Ця година",
        "Today": "Сьогодні",
        "This lunar month": "Цей місячний місяць",
        "This season": "Цей сезон",
        "This year": "Цей рік",
        "This chapter": "Цей розділ",
        "This era": "Ця епоха",
        # a few chrome words
        "themes": "теми",
        "favor": "сприяє",
        "avoid": "уникати",
        "now": "зараз",
    },
}


def t(s: str) -> str:
    return CATALOGS.get(LOCALE, {}).get(s, s)
