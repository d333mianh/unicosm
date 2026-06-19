"""Turn a free-text chat message into an (ephemeral) birth Profile.

This is what lets a user read *another person's* day without saving anything:
they type something like ``Ada 1990-03-21 14:30 Kyiv`` and we build a Profile on
the fly. Offline and pure — city names resolve through the bundled gazetteer;
explicit ``lat lon Area/Zone`` coordinates are also accepted.

Grammar (forgiving, order-flexible around the date):

    [name] <YYYY-MM-DD> [HH:MM] <place>

* name   — anything before the date (optional; defaults to "Subject")
* time   — optional; missing time defaults to noon with a warning
* place  — a city name, or "lat lon Area/Zone" (e.g. 50.45 30.52 Europe/Kyiv)
"""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..data.cities import lookup
from ..models import Profile

DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
COORD_RE = re.compile(r"(-?\d{1,2}(?:\.\d+)?|-?1[0-7]\d(?:\.\d+)?|-?180)"
                      r"[\s,]+(-?\d{1,2}(?:\.\d+)?|-?1[0-7]\d(?:\.\d+)?|-?180)")
TZ_RE = re.compile(r"\b([A-Za-z_]+/[A-Za-z_]+(?:/[A-Za-z_]+)?)\b")


class ParseError(ValueError):
    """Raised with a chat-friendly message when birth data can't be parsed."""


def parse_birth(text: str, *, default_name: str = "Subject") -> tuple[Profile, list[str]]:
    raw = (text or "").strip()
    dm = DATE_RE.search(raw)
    if not dm:
        raise ParseError(
            "I need a birth date like 1990-03-21, e.g. "
            "<code>1990-03-21 14:30 Kyiv</code>"
        )

    name = raw[: dm.start()].strip(" \t,|:;-") or default_name
    rest = raw[dm.end():]

    warnings: list[str] = []
    tm = TIME_RE.search(rest)
    if tm:
        hh, mm = int(tm.group(1)), int(tm.group(2))
        place_s = (rest[: tm.start()] + " " + rest[tm.end():]).strip()
    else:
        hh, mm = 12, 0
        place_s = rest.strip()
        warnings.append(
            "no birth time given — used 12:00 noon; rising sign and Moon degree "
            "are approximate"
        )
    place_s = place_s.strip(" \t,|;")
    if not place_s:
        raise ParseError(
            "I also need a birth place — a city name (e.g. Kyiv) or "
            "'lat lon Area/Zone' (e.g. 50.45 30.52 Europe/Kyiv)"
        )

    lat, lon, tz = _resolve_place(place_s)

    try:
        zone = ZoneInfo(tz)
    except ZoneInfoNotFoundError as exc:
        raise ParseError(
            f"unknown timezone '{tz}' — use an IANA name like Europe/Kyiv"
        ) from exc
    try:
        d = datetime(int(dm.group(1)), int(dm.group(2)), int(dm.group(3)))
    except ValueError as exc:
        raise ParseError(f"'{dm.group(0)}' is not a valid date") from exc
    birth = d.replace(hour=hh, minute=mm, tzinfo=zone)

    profile = Profile(
        name=name, birth_dt=birth, birth_tz=tz,
        birth_lat=lat, birth_lon=lon,
        cur_tz=tz, cur_lat=lat, cur_lon=lon,
    )
    return profile, warnings


def _resolve_place(place_s: str) -> tuple[float, float, str]:
    """A city name, or explicit 'lat lon Area/Zone' coordinates."""
    tzm = TZ_RE.search(place_s)
    cm = COORD_RE.search(place_s)
    if cm and tzm:
        lat, lon = float(cm.group(1)), float(cm.group(2))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ParseError(f"coordinates out of range: {lat}, {lon}")
        return lat, lon, tzm.group(1)

    hit = lookup(place_s)
    if hit is None:
        raise ParseError(
            f"unknown place '{place_s}'. Try a major city name, or give "
            "'lat lon Area/Zone' (e.g. 50.45 30.52 Europe/Kyiv)"
        )
    return hit
