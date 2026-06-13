"""Minimal i18n seam.

English-first. Strings flow through ``t()`` so a catalog/locale layer can be
added later without touching call sites. For now it is an identity function.
"""

from __future__ import annotations

import os

LOCALE = os.environ.get("UNICOSM_LOCALE", "en")


def t(s: str) -> str:
    return s
