"""BaZi (Four Pillars) + Tong Shu Day Officer.

BaZi: year/month/day/hour stem-branch from birth (solar-term month boundaries,
five-tigers month-stem and five-rats hour-stem rules), the Day Master, and an
element tally — a Blueprint reading. Day Officer: the Jian Chu 12-officer cycle
labeling today's quality — a daily cosmic reading. Reuses the sexagenary stems.
"""

from __future__ import annotations

from collections import Counter

from ..core import ephem
from ..models import Cadence, Layer, SystemReading
from .sexagenary import BRANCHES, STEMS

# Main element of each earthly branch (Zi..Hai).
BRANCH_ELEMENT = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire",
                  "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]

# 12 Day Officers (Jian Chu), 0 = Jian (day branch == month branch).
OFFICERS = [
    ("Jian", "Establish", "begin ventures, set intentions"),
    ("Chu", "Remove", "clear out, cleanse, end things"),
    ("Man", "Full", "abundance; good for gathering, risky for medicine"),
    ("Ping", "Balance", "routine, level work, agreements"),
    ("Ding", "Stable", "settle, commit, build foundations"),
    ("Zhi", "Initiate", "hold steady; not for big change"),
    ("Po", "Destruction", "demolition only; avoid important starts"),
    ("Wei", "Danger", "caution; avoid risk and travel"),
    ("Cheng", "Success", "accomplish, launch, marry — very auspicious"),
    ("Shou", "Receive", "acquire, collect, learn"),
    ("Kai", "Open", "openings, beginnings, ceremonies"),
    ("Bi", "Close", "close, store, conclude; avoid openings"),
]


def _month_index(sun_lon: float) -> int:
    """0 at Lichun (315°), counting solar months of 30°."""
    return int(((sun_lon - 315) % 360) // 30)


def compute_bazi(ctx) -> dict:
    b = ctx.profile.birth_dt
    jd = ctx.natal.jd
    sun_lon = ephem.planet_lon(jd, ephem.PLANETS["Sun"])[0]

    # year pillar (Lichun boundary)
    year = b.year
    if b.month == 1 or (b.month == 2 and sun_lon < 315):
        year -= 1
    ys = (year - 4) % 10
    yb = (year - 4) % 12

    # month pillar
    idx = _month_index(sun_lon)
    mb = (2 + idx) % 12
    ms = ((ys % 5) * 2 + 2 + idx) % 10

    # day pillar
    jdn = ephem.jdn_noon(b.year, b.month, b.day)
    ds = (jdn - 1) % 10
    db = (jdn + 1) % 12

    # hour pillar
    hb = ((b.hour + 1) // 2) % 12
    hs = ((ds % 5) * 2 + hb) % 10

    pillars = {"year": (ys, yb), "month": (ms, mb), "day": (ds, db), "hour": (hs, hb)}
    tally: Counter[str] = Counter()
    for s, br in pillars.values():
        tally[STEMS[s][2].split()[1]] += 1
        tally[BRANCH_ELEMENT[br]] += 1
    return {"pillars": pillars, "day_master": STEMS[ds], "tally": tally}


def bazi(ctx) -> SystemReading:
    c = compute_bazi(ctx)

    def pl(key):
        s, b = c["pillars"][key]
        return f"{STEMS[s][1]}{BRANCHES[b][1]}"

    dm = c["day_master"]
    tally = ", ".join(f"{el} {n}" for el, n in c["tally"].most_common())
    return SystemReading(
        key="bazi",
        title="BaZi (Four Pillars)",
        cadence=Cadence.BLUEPRINT,
        layer=Layer.BLUEPRINT,
        summary=(
            f"Pillars {pl('year')} {pl('month')} {pl('day')} {pl('hour')} · "
            f"Day Master {dm[0]} ({dm[2]}). Elements: {tally}."
        ),
        detail={
            "year": f"{STEMS[c['pillars']['year'][0]][0]}-{BRANCHES[c['pillars']['year'][1]][0]}",
            "month": f"{STEMS[c['pillars']['month'][0]][0]}-{BRANCHES[c['pillars']['month'][1]][0]}",
            "day": f"{STEMS[c['pillars']['day'][0]][0]}-{BRANCHES[c['pillars']['day'][1]][0]}",
            "hour": f"{STEMS[c['pillars']['hour'][0]][0]}-{BRANCHES[c['pillars']['hour'][1]][0]}",
            "day_master": f"{dm[0]} ({dm[2]})",
            "elements": dict(c["tally"]),
        },
        keywords=[dm[2].split()[1].lower(), "day master"],
    )


def day_officer(ctx) -> SystemReading:
    sun_lon = ephem.planet_lon(ctx.jd_now, ephem.PLANETS["Sun"])[0]
    month_branch = (2 + _month_index(sun_lon)) % 12
    d = ctx.now
    jdn = ephem.jdn_noon(d.year, d.month, d.day)
    day_branch = (jdn + 1) % 12
    idx = (day_branch - month_branch) % 12
    pinyin, eng, note = OFFICERS[idx]
    return SystemReading(
        key="day_officer",
        title="Day Officer (Tong Shu)",
        cadence=Cadence.DAILY,
        layer=Layer.COSMIC,
        summary=f"{eng} day ({pinyin}) — {note}.",
        detail={"officer": f"{eng} ({pinyin})", "guidance": note},
        keywords=[eng.lower()],
    )
