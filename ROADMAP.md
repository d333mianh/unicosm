# Unicosm Roadmap

Sequenced plan from v0.1 toward the full vision. Each step is a shippable
increment: new module(s) under `systems/` (or `routine/`, `synthesis/`),
appended to `systems.REGISTRY`, with tests and a commit. Catalog of candidate
systems lives in `complementary-systems-v2.md`.

**Two halves of the goal:** (1) cosmic state + woven guidance; (2) a personal
discipline/routine engine with real day-timing. Phases alternate between
deepening the reading and strengthening the routine.

---

## ✅ Done (v0.1 → now)

- Engine skeleton: ephemeris core, cadence layers, deterministic synthesis,
  optional LLM hook, SQLite, CLI, habit tracking. **18 readings across every
  cadence.**
- Systems: Western natal (Sun/Moon/Asc), Human Design (full bodygraph),
  Gene Keys (Activation Sequence), Vimshottari Dasha (+ janma nakshatra),
  numerology (life path / personal year / day), planetary hours, TCM organ
  clock, sexagenary day pillar, moon phase, 24 solar terms, annual profections,
  Jupiter cycle, astrological age.

---

## ✅ Phase A — Panchang + routine intelligence  (done)

- **A1** Panchang core — tithi, nakshatra, yoga, karana, vara.
- **A2** Day time-bands — Rahu Kalam, Yamaganda, Gulika, Abhijit, Choghadiya.
- **A3** Routine intelligence — per-window daily timing accents + a TODAY'S
  TIMING board (favor/avoid windows). The routine now adapts day to day.

## ✅ Phase B — Deepen the natal chart  (done)

- **B1** Full natal: house cusps + placements, major aspects, dignities, ruler.
- **B2** Daily transits to natal (incl. outer planets), applying/separating.
- **B3** Secondary progressions + progressed-Moon lunation cycle.

## ✅ Phase C — Personal time-lords  (done)

- **C1** Zodiacal Releasing from the Lot of Spirit (L1 years / L2 months).
- **C2** Solar & lunar return charts (year / lunar-month keynote).
- **C3** Numerology pinnacles & challenges (current stage by age).

## Phase D — On-demand divination (`unicosm draw`)  ← NEXT

*Fills the empty 4th functional layer; new command + draw history.*

- **D1** I Ching — hexagram + changing lines (+ the calendrical hexagram layer).
- **D2** Tarot — 78-card deck, daily card + 3-card spread, reversals.
- **D3** Runes — Elder Futhark, single + three-rune.

## Phase E — Cosmic-weather breadth

- **E1** Chinese: BaZi four pillars, Tong Shu day officers + activity verdicts,
  72 pentads.
- **E2** Western daily mechanics: void-of-course Moon, retrogrades, ingresses.
- **E3** Mayan Tzolkin / Dreamspell, Maria Thun biodynamic day, Sabian symbol.
- **E4** Secular: sunrise/sunset/day-length surfaced, eclipses, (optional online)
  Kp geomagnetic index.

## Phase F — Synthesis & intelligence

- **F1** Upgrade the deterministic weave: use *all* readings, complementarity
  rules, surface genuine tensions, per-cadence favorability.
- **F2** LLM narrative: tune the prompt, test live (needs a key in the runtime
  shell), response caching, model config.
- **F3** Resonance detection — the real "complementary" payoff: flag when many
  systems independently point the same way (e.g. "rest/release today").

## Phase G — Discipline & tracking maturity

- **G1** Daily check-in / journaling tied to the day's state; `history` view.
- **G2** Streak analytics, weekly/monthly review, consistency stats.
- **G3** OS reminders (cron/launchd/systemd) for window starts + auspicious times.

## Phase H — UX, data, quality

- **H1** Geocoding: city → lat/lon/tz, so onboarding isn't manual coordinates.
- **H2** Accuracy validation: golden-file tests vs reference calculators
  (HD chart, dasha dates, Panchang vs Drik Panchang).
- **H3** i18n: Ukrainian locale behind `t()`; externalize strings.
- **H4** Profile management: switch/edit/delete, multiple people, comparison.

## Phase I — Beyond the CLI (later, optional)

- Extract the engine as a reusable library/API; a web or TUI front-end; daily
  push notifications.

---

### Guiding principles

- **Step by step** — one increment per phase-item, always shippable and tested.
- **Local & offline** — Swiss Ephemeris + our own calendrical code; no network
  in the core path.
- **Complementary, not contradictory** — every system gets its own cadence slot;
  synthesis weaves, it doesn't average away the differences.
- **Verify against references** — these traditions have authoritative sources;
  spot-check before trusting (esp. HD, dashas, Panchang).
