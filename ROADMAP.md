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

## ✅ Phase D — On-demand divination (`unicosm draw`)  (done)

- **D1** I Ching — coin cast, changing lines, relating hexagram.
- **D2** Tarot — 78-card deck, single card + 3-card spread, reversals.
- **D3** Runes — Elder Futhark, single + three-rune, merkstave.
- Shared `draw`/`draws` commands + SQLite draw history; `--daily`/`--seed`.

## ✅ Phase E — Cosmic-weather breadth  (done)

- **E1** BaZi four pillars (blueprint) + Tong Shu Day Officer (Jian Chu).
- **E2** Sky mechanics: retrogrades + void-of-course Moon.
- **E3** Maria Thun biodynamic day (root/leaf/flower/fruit).
- **E4** Sky data: day length + next solar/lunar eclipse.
- Deferred: Tzolkin/Dreamspell, Sabian symbols, Kp index, 72 pentads.

## ✅ Phase F — Synthesis & intelligence  (done)

- **F1** Weave upgrade: uses all readings, per-cadence favorability, tensions.
- **F2** LLM narrative: resonance/tension-aware prompt, on-disk caching, env
  model config, graceful fallback. (Live output needs a key at runtime.)
- **F3** Resonance detection — themes echoed by 3+ systems surfaced in the
  headline + COSMIC STATE.

## ✅ Phase G — Discipline & tracking maturity  (done)

- **G1** Daily check-in / journaling with the day's state snapshot; `history`.
- **G2** `stats` — per-habit streaks, 30-day rate, totals, overall consistency.
- **G3** `remind` — today's reminder times + a crontab helper for a daily summary.

## ✅ Phase H — UX, data, quality  (done)

- **H1** `--place` city geocoding (bundled gazetteer).
- **H2** Golden cross-system regression test.
- **H3** i18n catalog framework + Ukrainian demo (chrome partial).
- **H4** Profile `use`/`rm` + `compare` (synastry-lite cross-aspects).

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
