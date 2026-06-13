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

It now runs **32 readings across every cadence layer** plus on-demand divination
and a tracked, timing-aware routine. Roadmap Phases A–H are complete (see
[`ROADMAP.md`](ROADMAP.md)); the catalog of ~120 systems in
[`complementary-systems-v2.md`](complementary-systems-v2.md) is the remaining
backlog.

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
# 1. set your birth profile (--place fills lat/lon/tz, or pass them yourself)
unicosm profile set --name You --birth "1990-03-21 14:30" --place Kyiv
unicosm profile use You          # switch active profile
unicosm compare You Partner      # synastry-lite cross-aspects

# 2. read today
unicosm today                 # the full woven reading + routine + timing
unicosm today --brief         # hide the per-layer breakdown
unicosm today --json          # machine-readable
unicosm today --date 2026-12-21 --time 06:00   # any moment
unicosm blueprint             # your fixed birth signature

# 3. discipline: define habits, anchor to day-windows, track + review
unicosm windows                                   # list anchor windows
unicosm habit add "Meditate" --window brahma_muhurta
unicosm check 1               # mark habit #1 done today (builds the streak)
unicosm stats                 # streaks + 30-day consistency
unicosm remind                # today's reminder times + crontab helper

# 4. reflect + divine
unicosm checkin --mood 4 --energy 3 "felt clear"  # daily journal + state snapshot
unicosm history                                    # past check-ins with the day's state
unicosm draw iching --question "what does this need?"
unicosm draw tarot --spread
unicosm draw runes
unicosm draws                 # divination history
```

Data lives in `~/.unicosm/unicosm.sqlite3` (override with `$UNICOSM_HOME`).
Set `UNICOSM_LOCALE=uk` for a (partial) Ukrainian interface.

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

## Systems (32 readings across every cadence)

| Cadence | System(s) |
|---|---|
| Blueprint | Western natal (houses, aspects, dignities, chart ruler), **Human Design** (full bodygraph), **Gene Keys** (Activation Sequence), **BaZi** four pillars, Janma nakshatra, natal aspects, Life Path |
| This hour | Planetary hours, TCM organ clock, Choghadiya timing |
| Today | Sexagenary day pillar, Panchang (five limbs), Tong Shu Day Officer, Personal Day, HD transit gate, transits-to-natal, sky mechanics (retro / void Moon), biodynamic day |
| This lunar month | Lunar phase, lunar return |
| This season | 24 solar terms |
| This year | Annual profections, Personal Year, solar return, Vimshottari antardasha |
| This chapter | Jupiter cycle, Vimshottari mahadasha, Zodiacal Releasing, progressions, numerology pinnacles |
| This era | Astrological age, sky data (day length + eclipses) |
| On-demand | I Ching, Tarot, Runes (`unicosm draw`) |

## Roadmap

Phases **A–H are complete** — see [`ROADMAP.md`](ROADMAP.md) for the full
breakdown (Panchang + routine timing, deepened natal, personal time-lords,
divination, cosmic-weather breadth, synthesis intelligence, discipline/tracking,
UX/quality). The remaining work:

- **Phase I (optional, later):** extract the engine as a library/API; a web or
  TUI front-end; push notifications.
- **From the catalog:** more systems still in `complementary-systems-v2.md`
  (BaZi luck pillars, Tzolkin/Dreamspell, Sabian symbols, Nine Star Ki, …).
- **Depth:** loosing-of-the-bond peaks for ZR; richer per-system interpretation.

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
