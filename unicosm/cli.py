"""Unicosm command-line interface."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import render, store
from .core.timeutil import civil_date, now_in
from .engine import daily_report
from .models import Profile
from .routine.windows import WINDOWS


# ---- helpers ------------------------------------------------------------

def _err(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 1


def _resolve_profile(name: str | None) -> Profile | None:
    return store.get_profile(name) if name else store.active_profile()


def _parse_when(profile: Profile, date_s: str | None, time_s: str | None) -> datetime | None:
    """Build an aware datetime in the profile's current tz, or None for now()."""
    if not date_s and not time_s:
        return None
    tz = ZoneInfo(profile.cur_tz)
    today = datetime.now(tz)
    d = datetime.strptime(date_s, "%Y-%m-%d").date() if date_s else today.date()
    if time_s:
        hh, mm = (int(x) for x in time_s.split(":"))
    else:
        hh, mm = today.hour, today.minute
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)


# ---- commands -----------------------------------------------------------

def cmd_profile_set(a: argparse.Namespace) -> int:
    from .data.cities import lookup

    lat, lon, tz = a.lat, a.lon, a.tz
    if a.place:
        hit = lookup(a.place)
        if not hit:
            return _err(f"unknown place '{a.place}'. Pass --lat/--lon/--tz, "
                        "or try a major city name.")
        lat, lon, tz = hit
    if lat is None or lon is None or tz is None:
        return _err("give a birth location: --place \"Kyiv\" or --lat/--lon/--tz")
    try:
        ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        return _err(f"unknown timezone: {tz} (use an IANA name like Europe/Kyiv)")
    try:
        birth = datetime.strptime(a.birth, "%Y-%m-%d %H:%M")
    except ValueError:
        return _err('birth must be "YYYY-MM-DD HH:MM" (e.g. "1990-03-21 14:30")')
    birth = birth.replace(tzinfo=ZoneInfo(tz))

    cur_tz = a.cur_tz or tz
    cur_lat = a.cur_lat if a.cur_lat is not None else lat
    cur_lon = a.cur_lon if a.cur_lon is not None else lon
    p = Profile(
        name=a.name, birth_dt=birth, birth_tz=tz,
        birth_lat=lat, birth_lon=lon,
        cur_tz=cur_tz, cur_lat=cur_lat, cur_lon=cur_lon,
    )
    store.save_profile(p, make_active=True)
    print(f"saved profile '{a.name}' (active).")
    print(f"  born {p.birth_label} at {lat}, {lon}")
    print(f"  current location: {cur_lat}, {cur_lon} ({cur_tz})")
    return 0


def cmd_profile_show(a: argparse.Namespace) -> int:
    names = store.list_profiles()
    if not names:
        return _err("no profiles yet. Create one with: unicosm profile set ...")
    active = store.active_profile()
    for n in names:
        p = store.get_profile(n)
        mark = "*" if active and p.name == active.name else " "
        print(f"{mark} {p.name:<16} born {p.birth_label}  ·  {p.cur_lat}, {p.cur_lon} ({p.cur_tz})")
    return 0


def cmd_profile_use(a: argparse.Namespace) -> int:
    if store.set_active(a.name):
        print(f"active profile is now '{a.name}'")
        return 0
    return _err(f"no profile named '{a.name}'")


def cmd_profile_rm(a: argparse.Namespace) -> int:
    if store.delete_profile(a.name):
        print(f"removed profile '{a.name}'")
        return 0
    return _err(f"no profile named '{a.name}'")


def cmd_compare(a: argparse.Namespace) -> int:
    from .context import compute_natal
    from .core import astro, ephem
    pa, pb = store.get_profile(a.a), store.get_profile(a.b)
    if not pa or not pb:
        return _err("both profiles must exist (see: unicosm profile show)")
    na, nb = compute_natal(pa), compute_natal(pb)

    print(render.bold(f"  {pa.name} ✕ {pb.name}"))
    for nm, n in ((pa.name, na), (pb.name, nb)):
        print(f"  {render.accent(nm):<22} Sun {n.sign('Sun')}, Moon {n.sign('Moon')}, "
              f"rising {n.sign('Asc')}")
    print(render.bold("\n  cross-aspects"))
    pairs = [("Sun", "Sun"), ("Sun", "Moon"), ("Moon", "Sun"),
             ("Moon", "Moon"), ("Venus", "Mars"), ("Mars", "Venus")]
    found = False
    for x, y in pairs:
        lum = x in ("Sun", "Moon") or y in ("Sun", "Moon")
        hit = astro.aspect_between(na.planets[x], nb.planets[y], lum)
        if hit:
            found = True
            name, glyph, orb = hit
            print(f"  {pa.name}'s {x} {glyph} {pb.name}'s {y}  "
                  f"{render.dim(f'{name} ({orb:.1f}°)')}")
    if not found:
        print(render.dim("  no tight cross-aspects among the key pairs"))
    return 0


def cmd_today(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile. Create one: unicosm profile set --name You "
                    '--birth "1990-03-21 14:30" --tz Europe/Kyiv --lat 50.45 --lon 30.52')
    when = _parse_when(p, a.date, a.time)
    rep = daily_report(p, when, use_llm=not a.no_llm)

    if a.json:
        print(json.dumps(_report_json(rep), ensure_ascii=False, indent=2))
        return 0

    print(render.header(p, rep.now))
    print(render.cosmic_state(rep.synthesis, rep.woven))
    if not a.brief:
        print(render.layers(rep.readings))
    print(render.accents(rep.synthesis))
    print(render.timing(rep.timing, rep.now))
    print(render.routine(rep.routine, show_empty=a.full_routine))
    print()
    return 0


def cmd_blueprint(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    rep = daily_report(p, None, use_llm=False)
    bp = [r for r in rep.readings if r.cadence.value == "blueprint"]
    print(render.header(p, rep.now))
    print(render.bold("\n  BLUEPRINT"))
    for r in bp:
        print(f"  {render.accent(r.title)}")
        print(f"    {r.summary}")
        for k, v in r.detail.items():
            print(render.dim(f"      {k}: {v}"))
    print()
    return 0


def cmd_habit_add(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    valid = {w.key for w in WINDOWS}
    if a.window and a.window not in valid:
        return _err(f"unknown window '{a.window}'. See: unicosm windows")
    hid = store.add_habit(p.name, a.name, a.window)
    print(f"added habit #{hid}: {a.name}" + (f" [{a.window}]" if a.window else ""))
    return 0


def cmd_habit_list(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    habits = store.list_habits(p.name)
    if not habits:
        print("no habits yet. Add one: unicosm habit add \"Meditate\" --window brahma_muhurta")
        return 0
    from .routine.tracker import current_streak, longest_streak
    today = datetime.now(ZoneInfo(p.cur_tz)).date()
    for h in habits:
        cs = current_streak(h.id, today)
        ls = longest_streak(h.id)
        win = f"[{h.window}]" if h.window else "[anytime]"
        print(f"  #{h.id:<3} {h.name:<28} {win:<16} streak {cs} (best {ls})")
    return 0


def cmd_habit_rm(a: argparse.Namespace) -> int:
    store.remove_habit(a.id)
    print(f"removed habit #{a.id}")
    return 0


def cmd_check(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    when = _parse_when(p, a.date, None) or datetime.now(ZoneInfo(p.cur_tz))
    day = civil_date(when)
    habits = {h.id for h in store.list_habits(p.name)}
    if a.id not in habits:
        return _err(f"no active habit #{a.id} for profile '{p.name}'")
    store.log_completion(a.id, day)
    from .routine.tracker import current_streak
    print(f"✓ checked habit #{a.id} for {day} — streak {current_streak(a.id, when.date())}")
    return 0


def _draw_rng(name: str, system: str, daily: bool, seed: int | None,
              tz: str) -> random.Random:
    if seed is not None:
        return random.Random(seed)
    if daily:
        key = f"{name}|{system}|{civil_date(now_in(tz))}"
        return random.Random(int(hashlib.sha256(key.encode()).hexdigest(), 16))
    return random.Random()


def cmd_draw(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    name = p.name if p else "anon"
    tz = p.cur_tz if p else "UTC"
    rng = _draw_rng(name, a.system, a.daily, a.seed, tz)

    text, summary = render.draw(a.system, rng, a.spread)
    if a.question:
        print(render.dim(f"  Q: {a.question}\n"))
    print(text)
    store.log_draw(name, a.system, summary, a.question)
    return 0


def cmd_draws(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    name = p.name if p else "anon"
    rows = store.recent_draws(name, a.limit)
    if not rows:
        print("no draws yet. Try: unicosm draw iching")
        return 0
    for r in rows:
        q = f"  — {render.dim(r['question'])}" if r["question"] else ""
        print(f"  {render.dim(r['ts'][:16])}  {r['system']:<7} {r['summary']}{q}")
    return 0


def cmd_stats(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    habits = store.list_habits(p.name)
    if not habits:
        print("no habits yet. Add one: unicosm habit add \"Meditate\"")
        return 0
    from .routine.tracker import current_streak, longest_streak, window_stats
    today = now_in(p.cur_tz).date()
    print(render.bold(f"  Consistency · last {a.days} days"))
    rates = []
    for h in habits:
        cs = current_streak(h.id, today)
        ls = longest_streak(h.id)
        w = window_stats(h.id, today, a.days)
        rates.append(w["rate"])
        bar = render.bar(w["rate"])
        meta = render.dim(f"streak {cs} (best {ls}) · {w['total']} total")
        print(f"  #{h.id:<3} {h.name:<24} {bar} {w['rate']*100:3.0f}%  {meta}")
    overall = sum(rates) / len(rates)
    print(render.dim(f"\n  overall consistency: {overall*100:.0f}%"))
    return 0


def cmd_checkin(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    when = _parse_when(p, a.date, None) or now_in(p.cur_tz)
    day = civil_date(when)
    # capture the day's cosmic-state snapshot
    rep = daily_report(p, when, use_llm=False)
    snapshot = f"{rep.synthesis.weather} | {rep.synthesis.headline}"
    if a.mood is not None and not (1 <= a.mood <= 5):
        return _err("--mood must be 1..5")
    if a.energy is not None and not (1 <= a.energy <= 5):
        return _err("--energy must be 1..5")
    store.save_checkin(p.name, day, a.mood, a.energy, a.note, snapshot)
    print(f"✓ checked in for {day}"
          + (f" · mood {a.mood}/5" if a.mood else "")
          + (f" · energy {a.energy}/5" if a.energy else ""))
    print(render.dim(f"  state: {snapshot}"))
    return 0


def cmd_history(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    rows = store.recent_checkins(p.name, a.limit)
    if not rows:
        print("no check-ins yet. Try: unicosm checkin --mood 4 --energy 3 \"a note\"")
        return 0
    for r in rows:
        me = []
        if r["mood"]:
            me.append(f"mood {r['mood']}/5")
        if r["energy"]:
            me.append(f"energy {r['energy']}/5")
        meta = ("  " + ", ".join(me)) if me else ""
        print(f"  {render.bold(r['day'])}{render.dim(meta)}")
        if r["note"]:
            print(f"    {r['note']}")
        if r["snapshot"]:
            print(render.dim(f"    ↳ {r['snapshot']}"))
    return 0


def cmd_remind(a: argparse.Namespace) -> int:
    p = _resolve_profile(a.profile)
    if not p:
        return _err("no profile yet.")
    from datetime import timedelta

    from .context import build_context
    from .routine.timing import compute as compute_timing
    ctx = build_context(p)
    dt = compute_timing(ctx)

    cron_line = f"0 5 * * *  unicosm today --no-llm --profile {p.name}"
    if a.cron:
        print("# add to your crontab (crontab -e) for a daily morning summary:")
        print(cron_line)
        return 0

    print(render.bold("  Today's reminders"))
    if dt.sunrise:
        bm = dt.sunrise - timedelta(minutes=96)
        print(f"  {render.accent(bm.strftime('%H:%M'))}  Brahma muhurta — practice window opens")
        print(f"  {render.accent(dt.sunrise.strftime('%H:%M'))}  Sunrise — light & movement")
        print(f"  {render.accent(dt.abhijit.start.strftime('%H:%M'))}  Abhijit muhurta — auspicious for what matters")
        for b in dt.inauspicious:
            print(f"  {render.dim(b.start.strftime('%H:%M'))}  avoid — {b.label} (until {b.end:%H:%M})")
    else:
        print(render.dim("  no sun events today (polar)"))
    print(render.dim(f"\n  for a daily auto-summary: unicosm remind --cron"))
    return 0


def cmd_windows(a: argparse.Namespace) -> int:
    print("Day windows you can anchor habits to (--window KEY):\n")
    for w in WINDOWS:
        print(f"  {render.accent(w.key):<28} {w.label:<16} {render.dim(w.note)}")
    return 0


# ---- json export --------------------------------------------------------

def _report_json(rep) -> dict:
    return {
        "profile": rep.profile.name,
        "now": rep.now.isoformat(),
        "synthesis": {
            "headline": rep.synthesis.headline,
            "weather": rep.synthesis.weather,
            "keywords": rep.synthesis.keywords,
            "accents": rep.synthesis.accents,
            "resonances": rep.synthesis.resonances,
            "tensions": rep.synthesis.tensions,
            "cadence_weather": rep.synthesis.cadence_weather,
        },
        "woven": rep.woven,
        "readings": [
            {"key": r.key, "title": r.title, "cadence": r.cadence.value,
             "layer": r.layer.value, "summary": r.summary, "detail": r.detail,
             "keywords": r.keywords, "score": r.score}
            for r in rep.readings
        ],
        "routine": [
            {"window": b.window.key, "label": b.window.label,
             "time": b.time_label, "is_now": b.is_now, "timing_note": b.timing_note,
             "habits": [{"id": sh.habit.id, "name": sh.habit.name,
                         "done": sh.done, "streak": sh.streak}
                        for sh in b.habits]}
            for b in rep.routine
        ],
        "timing": _timing_json(rep.timing),
    }


def _timing_json(dt) -> dict | None:
    if dt is None or dt.sunrise is None:
        return None
    return {
        "sunrise": dt.sunrise.strftime("%H:%M"),
        "sunset": dt.sunset.strftime("%H:%M"),
        "abhijit": dt.abhijit.time_label,
        "inauspicious": [{"label": b.label, "time": b.time_label} for b in dt.inauspicious],
        "choghadiya": [{"label": b.label, "time": b.time_label, "quality": b.quality}
                       for b in dt.all_choghadiya()],
    }


# ---- parser -------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="unicosm",
        description="Cosmic state and personal routine, woven from many systems.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # profile
    pp = sub.add_parser("profile", help="manage birth profiles")
    psub = pp.add_subparsers(dest="sub", required=True)
    ps = psub.add_parser("set", help="create/update a profile")
    ps.add_argument("--name", required=True)
    ps.add_argument("--birth", required=True, help='"YYYY-MM-DD HH:MM" (local birth time)')
    ps.add_argument("--place", help="known city name (fills lat/lon/tz)")
    ps.add_argument("--tz", help="IANA tz of birth, e.g. Europe/Kyiv")
    ps.add_argument("--lat", type=float, help="birth latitude (N+)")
    ps.add_argument("--lon", type=float, help="birth longitude (E+)")
    ps.add_argument("--cur-tz", help="current tz (default: birth tz)")
    ps.add_argument("--cur-lat", type=float, help="current latitude")
    ps.add_argument("--cur-lon", type=float, help="current longitude")
    ps.set_defaults(func=cmd_profile_set)
    psh = psub.add_parser("show", help="list profiles")
    psh.set_defaults(func=cmd_profile_show)
    pu = psub.add_parser("use", help="set the active profile")
    pu.add_argument("name")
    pu.set_defaults(func=cmd_profile_use)
    prm2 = psub.add_parser("rm", help="delete a profile")
    prm2.add_argument("name")
    prm2.set_defaults(func=cmd_profile_rm)

    # compare (synastry-lite)
    pcmp = sub.add_parser("compare", help="compare two profiles' charts")
    pcmp.add_argument("a")
    pcmp.add_argument("b")
    pcmp.set_defaults(func=cmd_compare)

    # today
    pt = sub.add_parser("today", help="the woven reading + routine for now")
    pt.add_argument("--profile", help="profile name (default: active)")
    pt.add_argument("--date", help="YYYY-MM-DD (default: today)")
    pt.add_argument("--time", help="HH:MM (default: now)")
    pt.add_argument("--no-llm", action="store_true", help="skip LLM narrative")
    pt.add_argument("--brief", action="store_true", help="hide the per-layer breakdown")
    pt.add_argument("--full-routine", action="store_true", help="show empty windows too")
    pt.add_argument("--json", action="store_true", help="machine-readable output")
    pt.set_defaults(func=cmd_today)

    # blueprint
    pb = sub.add_parser("blueprint", help="your fixed birth signature")
    pb.add_argument("--profile")
    pb.set_defaults(func=cmd_blueprint)

    # habits
    ph = sub.add_parser("habit", help="manage tracked practices")
    hsub = ph.add_subparsers(dest="sub", required=True)
    ha = hsub.add_parser("add")
    ha.add_argument("name")
    ha.add_argument("--window", help="window key (see: unicosm windows)")
    ha.add_argument("--profile")
    ha.set_defaults(func=cmd_habit_add)
    hl = hsub.add_parser("list")
    hl.add_argument("--profile")
    hl.set_defaults(func=cmd_habit_list)
    hr = hsub.add_parser("rm")
    hr.add_argument("id", type=int)
    hr.set_defaults(func=cmd_habit_rm)

    # check
    pc = sub.add_parser("check", help="log a habit as done")
    pc.add_argument("id", type=int)
    pc.add_argument("--date", help="YYYY-MM-DD (default: today)")
    pc.add_argument("--profile")
    pc.set_defaults(func=cmd_check)

    # draw (divination)
    pd = sub.add_parser("draw", help="on-demand divination (I Ching, Tarot, Runes)")
    pd.add_argument("system", choices=["iching", "tarot", "runes"])
    pd.add_argument("--question", help="the question you're holding")
    pd.add_argument("--daily", action="store_true", help="stable draw seeded by today's date")
    pd.add_argument("--seed", type=int, help="fixed seed (reproducible)")
    pd.add_argument("--spread", action="store_true",
                    help="three-card/rune spread (tarot/runes)")
    pd.add_argument("--profile")
    pd.set_defaults(func=cmd_draw)

    pdh = sub.add_parser("draws", help="recent divination history")
    pdh.add_argument("--limit", type=int, default=10)
    pdh.add_argument("--profile")
    pdh.set_defaults(func=cmd_draws)

    # stats
    pst = sub.add_parser("stats", help="habit consistency & streaks")
    pst.add_argument("--days", type=int, default=30)
    pst.add_argument("--profile")
    pst.set_defaults(func=cmd_stats)

    # checkin / history
    pci = sub.add_parser("checkin", help="log today's mood/energy + a note")
    pci.add_argument("note", nargs="?", help="free-text reflection")
    pci.add_argument("--mood", type=int, help="1..5")
    pci.add_argument("--energy", type=int, help="1..5")
    pci.add_argument("--date", help="YYYY-MM-DD (default: today)")
    pci.add_argument("--profile")
    pci.set_defaults(func=cmd_checkin)

    phi = sub.add_parser("history", help="recent check-ins with that day's state")
    phi.add_argument("--limit", type=int, default=14)
    phi.add_argument("--profile")
    phi.set_defaults(func=cmd_history)

    # remind
    prm = sub.add_parser("remind", help="today's reminder times + crontab helper")
    prm.add_argument("--cron", action="store_true", help="print a crontab line only")
    prm.add_argument("--profile")
    prm.set_defaults(func=cmd_remind)

    # windows
    pw = sub.add_parser("windows", help="list day windows")
    pw.set_defaults(func=cmd_windows)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
