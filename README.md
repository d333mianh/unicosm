# Unicosm

> Birth data × today, woven from many complementary traditions into one daily
> reading — and a personal routine you can actually keep.

You enter your birth date, time, and place once. Each day, Unicosm computes
where *you* are across a stack of guidance systems — astrology, numerology, the
Chinese day-pillar, the lunar phase, the solar term, Hellenistic profections,
your Jupiter chapter, the astrological age — organizes them by **cadence**
(this hour → today → this lunar month → season → year → chapter → era), and
weaves them into a single, non-contradictory reading. Then it turns that cosmic
state into a **timed, trackable routine** built on *your* habits.

This is **v0.1 — a thin vertical slice across every cadence layer**. It is built
to grow: the catalog of ~120 systems in
[`complementary-systems-v2.md`](complementary-systems-v2.md) is the backlog.

## Design choices

| Decision | Choice |
|---|---|
| Form | Local **CLI** (Python) |
| Birth data | Full **date + time + place** |
| Organization | **Cadence layers** + a woven synthesis |
| Synthesis | **Hybrid** — deterministic always, optional LLM narrative |
| Computation | **Local** Swiss Ephemeris (`pyswisseph`), offline, no API cost |
| Discipline | You define habits; the engine **times** them and **tracks streaks** |
| Language | English first, i18n-ready (`unicosm/i18n.py`) |

## Install

System Python here ships without `pip`, and `pyswisseph` compiles from source,
so a one-time toolchain setup is needed:

```bash
# build deps (Debian/Ubuntu)
apt-get install -y gcc g++ python3-dev

# isolated env + bootstrap pip (if ensurepip is missing)
python3 -m venv .venv --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python

# install Unicosm
.venv/bin/python -m pip install -e .
```

## Use

```bash
# 1. set your birth profile (lat N+, lon E+, IANA timezone)
unicosm profile set --name You --birth "1990-03-21 14:30" \
    --tz Europe/Kyiv --lat 50.45 --lon 30.52
#    add --cur-tz/--cur-lat/--cur-lon if you live elsewhere now

# 2. read today
unicosm today                 # the full woven reading + routine
unicosm today --brief         # hide the per-layer breakdown
unicosm today --json          # machine-readable
unicosm today --date 2026-12-21 --time 06:00   # any moment

# 3. your fixed signature
unicosm blueprint

# 4. discipline: define habits, anchor them to day-windows, track them
unicosm windows                                   # list anchor windows
unicosm habit add "Meditate" --window brahma_muhurta
unicosm habit add "Deep work" --window morning
unicosm habit list
unicosm check 1               # mark habit #1 done today (builds the streak)
```

Data lives in `~/.unicosm/unicosm.sqlite3` (override with `$UNICOSM_HOME`).

### Optional: LLM narrative

The deterministic synthesis always runs. If you set `ANTHROPIC_API_KEY` and
`pip install -e ".[llm]"`, `unicosm today` also prints a woven prose reading
(model via `$UNICOSM_LLM_MODEL`, default `claude-opus-4-8`). It never alters the
underlying facts and degrades silently if unavailable. Use `--no-llm` to skip.

## Architecture

```
unicosm/
  core/ephem.py     Swiss Ephemeris wrapper (Moshier — no data files needed)
  context.py        DayContext: profile + moment + cached astronomy, computed once
  systems/          one module per tradition -> SystemReading (cadence + layer + keywords)
  routine/          day windows, habit scheduling, streak tracking
  synthesis/        deterministic weave (+ optional LLM)
  engine.py         profile + moment -> DailyReport
  cli.py / render.py
```

A **system** is just `reading(ctx) -> SystemReading`. To add one: write the
module, append it to `systems/REGISTRY`. That is the seam the project grows on.

## Systems in v0.1 (one per cadence)

| Cadence | System(s) |
|---|---|
| Blueprint | Western natal (Sun/Moon/Asc), **Human Design** (type/authority/profile/centers/channels), **Gene Keys** (Activation Sequence), **Janma nakshatra**, Life Path number |
| This hour | Planetary hours, TCM organ clock |
| Today | Sexagenary day pillar (60 jiazi), Personal Day number, HD transit Sun-gate |
| This lunar month | Lunar phase (8-phase) |
| This season | 24 solar terms (jieqi) |
| This year | Annual profections, Personal Year, **Vimshottari antardasha** (+ pratyantar) |
| This chapter | Jupiter cycle (~12 yr), **Vimshottari mahadasha** |
| This era | Astrological age (Lahiri) |

## Roadmap (next steps, from the catalog)

1. ~~Human Design + Gene Keys~~ ✅ done.
2. ~~Vimshottari Dasha~~ ✅ done (maha/antar/pratyantar + janma nakshatra). Next
   in this track: Zodiacal Releasing, full natal aspects/houses, and Panchang
   (the nakshatra computation is already in place).
3. **On-demand divination** — I Ching, Tarot, Runes (`unicosm draw`).
4. **More cosmic weather** — full Panchang, Tong Shu, biodynamic/Maria Thun.
5. **Routine intelligence** — per-window cosmic accents, reminders (OS
   scheduling), cycle-syncing.
6. **i18n** — Ukrainian locale; real catalog behind `t()`.

## Accuracy notes

- Positions use the Moshier ephemeris (arc-second accuracy) — ample for these
  traditions.
- The sexagenary day formula is verified against the reference anchor
  2019-01-27 = 甲子 and the worked example 1781-03-13 = 壬戌 (see tests).
- Astrological-age boundaries use equal 30° sidereal signs (Lahiri ayanamsa);
  constellation-boundary conventions vary.
- Human Design uses the verified Rave Mandala wheel (Gate 41 at 2° Aquarius),
  the **true** lunar node, and the Design point at exactly 88° of solar arc
  before birth. Gene Key number = HD gate number. Worth spot-checking a chart or
  two against a reference calculator (e.g. Jovian Archive) before relying on it.
- Vimshottari Dasha uses the Lahiri ayanamsa for the Moon's nakshatra and a
  365.25-day year; dasha start dates can differ by a few days between software
  using different year-lengths/ayanamsas.

```bash
.venv/bin/python -m unittest discover -s tests   # run the tests
```
