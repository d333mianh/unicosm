"""Filesystem locations for Unicosm's local data."""

from __future__ import annotations

import os
from pathlib import Path


def data_dir() -> Path:
    """Directory holding the local database. Override with $UNICOSM_HOME."""
    override = os.environ.get("UNICOSM_HOME")
    base = Path(override) if override else Path.home() / ".unicosm"
    base.mkdir(parents=True, exist_ok=True)
    return base


def db_path() -> Path:
    return data_dir() / "unicosm.sqlite3"
