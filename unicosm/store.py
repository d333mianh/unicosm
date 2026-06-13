"""SQLite persistence: profiles, habits, and habit completions.

Deliberately stdlib-only (sqlite3). One database file under config.data_dir().
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import db_path
from .models import Habit, Profile

_SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    name      TEXT PRIMARY KEY,
    birth_iso TEXT NOT NULL,      -- ISO 8601 with offset
    birth_tz  TEXT NOT NULL,
    birth_lat REAL NOT NULL,
    birth_lon REAL NOT NULL,
    cur_tz    TEXT NOT NULL,
    cur_lat   REAL NOT NULL,
    cur_lon   REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS habit (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    profile TEXT NOT NULL,
    name    TEXT NOT NULL,
    window  TEXT,
    cadence TEXT NOT NULL DEFAULT 'daily',
    active  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS completion (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    day      TEXT NOT NULL,       -- local civil date YYYY-MM-DD
    ts       TEXT NOT NULL,       -- when logged
    UNIQUE(habit_id, day)
);

CREATE TABLE IF NOT EXISTS draw (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    profile  TEXT NOT NULL,
    system   TEXT NOT NULL,       -- iching | tarot | runes
    ts       TEXT NOT NULL,
    summary  TEXT NOT NULL,
    question TEXT
);

CREATE TABLE IF NOT EXISTS checkin (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    profile  TEXT NOT NULL,
    day      TEXT NOT NULL,       -- local civil date
    ts       TEXT NOT NULL,
    mood     INTEGER,             -- 1..5
    energy   INTEGER,             -- 1..5
    note     TEXT,
    snapshot TEXT,                -- the day's cosmic-state headline/weather
    UNIQUE(profile, day)
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


# ---- profiles -----------------------------------------------------------

def save_profile(p: Profile, make_active: bool = True) -> None:
    with connect() as conn:
        if make_active:
            conn.execute("UPDATE profile SET is_active = 0")
        conn.execute(
            """INSERT INTO profile
               (name, birth_iso, birth_tz, birth_lat, birth_lon,
                cur_tz, cur_lat, cur_lon, is_active)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(name) DO UPDATE SET
                 birth_iso=excluded.birth_iso, birth_tz=excluded.birth_tz,
                 birth_lat=excluded.birth_lat, birth_lon=excluded.birth_lon,
                 cur_tz=excluded.cur_tz, cur_lat=excluded.cur_lat,
                 cur_lon=excluded.cur_lon, is_active=excluded.is_active""",
            (p.name, p.birth_dt.isoformat(), p.birth_tz, p.birth_lat, p.birth_lon,
             p.cur_tz, p.cur_lat, p.cur_lon, 1 if make_active else 0),
        )


def _row_to_profile(r: sqlite3.Row) -> Profile:
    dt = datetime.fromisoformat(r["birth_iso"])
    # Re-anchor to the named tz so DST/offset is authoritative.
    dt = dt.replace(tzinfo=ZoneInfo(r["birth_tz"]))
    return Profile(
        name=r["name"], birth_dt=dt, birth_tz=r["birth_tz"],
        birth_lat=r["birth_lat"], birth_lon=r["birth_lon"],
        cur_tz=r["cur_tz"], cur_lat=r["cur_lat"], cur_lon=r["cur_lon"],
    )


def active_profile() -> Profile | None:
    with connect() as conn:
        r = conn.execute(
            "SELECT * FROM profile WHERE is_active = 1 LIMIT 1"
        ).fetchone()
        if r is None:
            r = conn.execute("SELECT * FROM profile LIMIT 1").fetchone()
        return _row_to_profile(r) if r else None


def get_profile(name: str) -> Profile | None:
    with connect() as conn:
        r = conn.execute("SELECT * FROM profile WHERE name = ?", (name,)).fetchone()
        return _row_to_profile(r) if r else None


def set_active(name: str) -> bool:
    with connect() as conn:
        if not conn.execute("SELECT 1 FROM profile WHERE name = ?", (name,)).fetchone():
            return False
        conn.execute("UPDATE profile SET is_active = 0")
        conn.execute("UPDATE profile SET is_active = 1 WHERE name = ?", (name,))
        return True


def delete_profile(name: str) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM profile WHERE name = ?", (name,))
        return cur.rowcount > 0


def list_profiles() -> list[str]:
    with connect() as conn:
        return [r["name"] for r in conn.execute("SELECT name FROM profile ORDER BY name")]


# ---- habits -------------------------------------------------------------

def add_habit(profile: str, name: str, window: str | None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO habit (profile, name, window) VALUES (?,?,?)",
            (profile, name, window),
        )
        return int(cur.lastrowid)


def list_habits(profile: str, active_only: bool = True) -> list[Habit]:
    q = "SELECT * FROM habit WHERE profile = ?"
    if active_only:
        q += " AND active = 1"
    q += " ORDER BY id"
    with connect() as conn:
        return [
            Habit(id=r["id"], name=r["name"], window=r["window"],
                  cadence=r["cadence"], active=bool(r["active"]))
            for r in conn.execute(q, (profile,))
        ]


def remove_habit(habit_id: int) -> None:
    with connect() as conn:
        conn.execute("UPDATE habit SET active = 0 WHERE id = ?", (habit_id,))


# ---- completions --------------------------------------------------------

def log_completion(habit_id: int, day: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO completion (habit_id, day, ts) VALUES (?,?,?)",
            (habit_id, day, datetime.now().isoformat()),
        )


def completions_for_day(profile: str, day: str) -> set[int]:
    with connect() as conn:
        rows = conn.execute(
            """SELECT c.habit_id FROM completion c
               JOIN habit h ON h.id = c.habit_id
               WHERE h.profile = ? AND c.day = ?""",
            (profile, day),
        )
        return {r["habit_id"] for r in rows}


def log_draw(profile: str, system: str, summary: str, question: str | None = None) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO draw (profile, system, ts, summary, question) VALUES (?,?,?,?,?)",
            (profile, system, datetime.now().isoformat(timespec="seconds"), summary, question),
        )


def recent_draws(profile: str, limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT system, ts, summary, question FROM draw WHERE profile = ? "
            "ORDER BY id DESC LIMIT ?",
            (profile, limit),
        )
        return [dict(r) for r in rows]


def save_checkin(profile: str, day: str, mood: int | None, energy: int | None,
                 note: str | None, snapshot: str | None) -> None:
    with connect() as conn:
        conn.execute(
            """INSERT INTO checkin (profile, day, ts, mood, energy, note, snapshot)
               VALUES (?,?,?,?,?,?,?)
               ON CONFLICT(profile, day) DO UPDATE SET
                 ts=excluded.ts, mood=excluded.mood, energy=excluded.energy,
                 note=excluded.note, snapshot=excluded.snapshot""",
            (profile, day, datetime.now().isoformat(timespec="seconds"),
             mood, energy, note, snapshot),
        )


def recent_checkins(profile: str, limit: int = 14) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT day, mood, energy, note, snapshot FROM checkin "
            "WHERE profile = ? ORDER BY day DESC LIMIT ?",
            (profile, limit),
        )
        return [dict(r) for r in rows]


def completion_days(habit_id: int) -> list[str]:
    with connect() as conn:
        return [
            r["day"] for r in conn.execute(
                "SELECT day FROM completion WHERE habit_id = ? ORDER BY day DESC",
                (habit_id,),
            )
        ]
