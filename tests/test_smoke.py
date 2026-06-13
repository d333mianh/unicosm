"""Smoke + correctness tests. Run: .venv/bin/python -m unittest -v"""

import os
import tempfile
import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

# Isolate the database before importing modules that resolve paths lazily.
os.environ["UNICOSM_HOME"] = tempfile.mkdtemp(prefix="unicosm_test_")

from unicosm.core import ephem
from unicosm.engine import daily_report
from unicosm.models import Profile
from unicosm.systems import base
from unicosm.systems.sexagenary import BRANCHES, STEMS


def make_profile() -> Profile:
    return Profile(
        name="Test",
        birth_dt=datetime(1990, 3, 21, 14, 30, tzinfo=ZoneInfo("Europe/Kyiv")),
        birth_lat=50.45, birth_lon=30.52, birth_tz="Europe/Kyiv",
        cur_lat=50.45, cur_lon=30.52, cur_tz="Europe/Kyiv",
    )


class TestSexagenary(unittest.TestCase):
    def test_reference_jiazi(self):
        # 2019-01-27 is the documented anchor: jiǎ-zǐ (甲子), cycle day 1.
        jdn = ephem.jdn_noon(2019, 1, 27)
        self.assertEqual(jdn, 2458511)
        self.assertEqual(STEMS[(jdn - 1) % 10][0], "Jiǎ")
        self.assertEqual(BRANCHES[(jdn + 1) % 12][0], "Zǐ")
        self.assertEqual((jdn - 11) % 60 + 1, 1)

    def test_worked_example_1781(self):
        # March 13, 1781 -> rén-xū (壬戌), cycle day 59.
        jdn = ephem.jdn_noon(1781, 3, 13)
        self.assertEqual(jdn, 2371629)
        self.assertEqual(STEMS[(jdn - 1) % 10][0], "Rén")
        self.assertEqual(BRANCHES[(jdn + 1) % 12][0], "Xū")
        self.assertEqual((jdn - 11) % 60 + 1, 59)


class TestNumerology(unittest.TestCase):
    def test_reduce_and_master(self):
        self.assertEqual(base.reduce_number(38), 11)       # 3+8=11, master kept by default
        self.assertEqual(base.reduce_number(38, keep_master=False), 2)
        self.assertEqual(base.reduce_number(29), 11)       # 2+9=11
        self.assertEqual(base.reduce_number(19), 1)        # 1+9=10 -> 1
        self.assertEqual(base.reduce_number(9), 9)
        self.assertEqual(base.ordinal(1), "1st")
        self.assertEqual(base.ordinal(11), "11th")
        self.assertEqual(base.ordinal(22), "22nd")


class TestEphem(unittest.TestCase):
    def test_equinox_sun(self):
        # A spring-equinox birth -> Sun very near 0° Aries.
        jd = ephem.jd_ut(datetime(1990, 3, 21, 14, 30, tzinfo=ZoneInfo("Europe/Kyiv")))
        lon, _ = ephem.planet_lon(jd, ephem.PLANETS["Sun"])
        self.assertLess(min(lon, 360 - lon), 1.5)  # within ~1.5° of 0° Aries

    def test_moon_phase_extremes(self):
        # construct phases via elongation mapping
        self.assertEqual(ephem.PHASE_NAMES[0], "New Moon")
        self.assertEqual(ephem.PHASE_NAMES[4], "Full Moon")


class TestAstrology(unittest.TestCase):
    def test_dignities(self):
        from unicosm.core import astro
        self.assertEqual(astro.dignity("Sun", 5.0), "exaltation")    # Aries
        self.assertEqual(astro.dignity("Mars", 5.0), "domicile")     # Aries
        self.assertEqual(astro.dignity("Saturn", 295.0), "domicile")  # Capricorn
        self.assertEqual(astro.dignity("Moon", 295.0), "detriment")   # Capricorn
        self.assertEqual(astro.dignity("Venus", 5.0), "detriment")    # Aries (rules Libra)
        self.assertIsNone(astro.dignity("Mercury", 5.0))             # Aries: peregrine

    def test_aspects(self):
        from unicosm.core import astro
        self.assertEqual(astro.aspect_between(0, 90)[0], "square")
        self.assertEqual(astro.aspect_between(0, 120)[0], "trine")
        self.assertEqual(astro.aspect_between(10, 14)[0], "conjunction")
        self.assertIsNone(astro.aspect_between(0, 45))

    def test_house_of(self):
        ctx = _ctx()
        # Sun at 0° Aries falls in the 9th house for this chart (verified)
        self.assertEqual(ctx.natal.house_of(ctx.natal.planets["Sun"]), 9)


class TestStreak(unittest.TestCase):
    def test_consecutive(self):
        from unicosm.routine.tracker import current_streak
        from unicosm import store
        hid = store.add_habit("StreakUser", "x", None)
        for d in ("2026-06-10", "2026-06-11", "2026-06-12", "2026-06-13"):
            store.log_completion(hid, d)
        self.assertEqual(current_streak(hid, date(2026, 6, 13)), 4)
        # a gap breaks it
        self.assertEqual(current_streak(hid, date(2026, 6, 15)), 0)


class TestHumanDesign(unittest.TestCase):
    def test_gate_line_anchor(self):
        from unicosm.core import hd
        self.assertEqual(hd.gate_line(302.0), (41, 1))      # 2° Aquarius
        self.assertEqual(hd.gate_line(307.625), (19, 1))
        self.assertEqual(hd.gate_line(330.125), (55, 1))

    def test_design_is_88_degrees_before(self):
        from unicosm.core import ephem, hd
        bjd = ephem.jd_ut(datetime(1990, 3, 21, 14, 30, tzinfo=ZoneInfo("Europe/Kyiv")))
        djd = hd.design_jd(bjd)
        psun = ephem.planet_lon(bjd, ephem.PLANETS["Sun"])[0]
        dsun = ephem.planet_lon(djd, ephem.PLANETS["Sun"])[0]
        self.assertAlmostEqual((psun - dsun) % 360, 88.0, places=2)

    def test_chart_is_coherent(self):
        from unicosm.core import ephem
        from unicosm.systems.human_design import compute_chart
        bjd = ephem.jd_ut(datetime(1990, 3, 21, 14, 30, tzinfo=ZoneInfo("Europe/Kyiv")))
        c = compute_chart(bjd)
        self.assertIn(c["type"], {"Manifestor", "Generator",
                                  "Manifesting Generator", "Projector", "Reflector"})
        self.assertRegex(c["profile"], r"^[1-6]/[1-6]$")

    def test_gene_keys_complete(self):
        from unicosm.data.gene_keys import SPECTRUM
        from unicosm.data.human_design import GATE_WHEEL
        self.assertEqual(len(SPECTRUM), 64)
        # every gate on the wheel has a Gene Key triad
        for g in GATE_WHEEL:
            self.assertIn(g, SPECTRUM)
            self.assertEqual(len(SPECTRUM[g]), 3)


class TestVimshottari(unittest.TestCase):
    def test_lords_sum_120(self):
        from unicosm.data.vimshottari import YEARS
        self.assertEqual(sum(YEARS.values()), 120)

    def test_nakshatra_ruler_mapping(self):
        from unicosm.data.vimshottari import LORDS, NAKSHATRAS
        self.assertEqual(len(NAKSHATRAS), 27)
        # Ashwini -> Ketu, Uttara Ashadha (index 20) -> Sun
        self.assertEqual(LORDS[NAKSHATRAS.index("Ashwini") % 9], "Ketu")
        self.assertEqual(LORDS[NAKSHATRAS.index("Uttara Ashadha") % 9], "Sun")

    def test_period_nesting_contains_now(self):
        from unicosm.core import ephem
        from unicosm.systems.vimshottari import compute
        bjd = ephem.jd_ut(datetime(1990, 3, 21, 14, 30, tzinfo=ZoneInfo("Europe/Kyiv")))
        njd = ephem.jd_ut(datetime(2026, 6, 13, 9, 30, tzinfo=ZoneInfo("Europe/Kyiv")))
        c = compute(bjd, njd)
        maha, antar, praty = c["maha"], c["antar"], c["praty"]
        # each active period contains 'now' and nests inside its parent
        self.assertTrue(maha.start_jd <= njd < maha.end_jd)
        self.assertTrue(antar.start_jd <= njd < antar.end_jd)
        self.assertTrue(praty.start_jd <= njd < praty.end_jd)
        self.assertGreaterEqual(antar.start_jd, maha.start_jd - 1e-6)
        self.assertLessEqual(antar.end_jd, maha.end_jd + 1e-6)
        self.assertGreaterEqual(praty.start_jd, antar.start_jd - 1e-6)
        self.assertLessEqual(praty.end_jd, antar.end_jd + 1e-6)


class TestPanchang(unittest.TestCase):
    def test_tithi_boundaries(self):
        from unicosm.systems.panchang import _tithi
        self.assertEqual(_tithi(0.0)["name"], "Pratipada")
        self.assertEqual(_tithi(0.0)["paksha"].split()[0], "Shukla")
        self.assertEqual(_tithi(174.0)["name"], "Purnima")        # tithi 15
        self.assertEqual(_tithi(180.0)["paksha"].split()[0], "Krishna")
        self.assertEqual(_tithi(354.0)["name"], "Amavasya")       # tithi 30

    def test_karana_sequence(self):
        from unicosm.systems.panchang import _karana
        self.assertEqual(_karana(0.0), "Kimstughna")              # idx 0, first fixed
        self.assertEqual(_karana(6.0), "Bava")                    # idx 1, first movable
        self.assertEqual(_karana(342.0), "Shakuni")              # idx 57
        self.assertEqual(_karana(354.0), "Naga")                 # idx 59, last fixed

    def test_compute_runs(self):
        from unicosm.systems.panchang import compute
        from unicosm.data.panchang import YOGA_NAMES
        from unicosm.data.vimshottari import NAKSHATRAS
        p = compute(_ctx())
        self.assertIn(p["nakshatra"], NAKSHATRAS)
        self.assertIn(p["yoga"], YOGA_NAMES)
        self.assertTrue(1 <= p["tithi"]["num"] <= 30)


def _ctx():
    from unicosm.context import build_context
    return build_context(make_profile(),
                         datetime(2026, 6, 13, 9, 30, tzinfo=ZoneInfo("Europe/Kyiv")))


class TestTiming(unittest.TestCase):
    def test_bands(self):
        from unicosm.routine.timing import compute
        dt = compute(_ctx())
        self.assertEqual(len(dt.day_choghadiya), 8)
        self.assertEqual(len(dt.night_choghadiya), 8)
        # Rahu/Yama/Gulika are all inauspicious; Abhijit is good
        self.assertTrue(all(b.quality == "bad" for b in dt.inauspicious))
        self.assertEqual(dt.abhijit.quality, "good")
        # bands sit within the daylight window
        for b in dt.inauspicious:
            self.assertTrue(dt.sunrise <= b.start < dt.sunset)


class TestRoutineIntelligence(unittest.TestCase):
    def test_report_has_timing_and_window_accents(self):
        rep = daily_report(make_profile(),
                           datetime(2026, 6, 13, 9, 30, tzinfo=ZoneInfo("Europe/Kyiv")),
                           use_llm=False)
        # timing is attached and populated
        self.assertIsNotNone(rep.timing.sunrise)
        self.assertEqual(len(rep.timing.all_choghadiya()), 16)
        # at least one timed window carries a daily timing accent
        notes = [b.timing_note for b in rep.routine if b.timing_note]
        self.assertTrue(notes)


class TestZodiacalReleasing(unittest.TestCase):
    def test_zr_runs(self):
        from unicosm.systems.zodiacal_releasing import reading
        r = reading(_ctx())
        self.assertIn(r.detail["sect"], ("day", "night"))
        self.assertIn("L1", r.detail)
        self.assertIn("L2", r.detail)

    def test_lesser_years(self):
        from unicosm.systems.zodiacal_releasing import _sign_years
        self.assertEqual(_sign_years("Capricorn"), 30)   # Saturn
        self.assertEqual(_sign_years("Cancer"), 25)      # Moon
        self.assertEqual(_sign_years("Libra"), 8)        # Venus


class TestPinnacles(unittest.TestCase):
    def test_pinnacles_and_challenges(self):
        from unicosm.systems.numerology import pinnacles
        r = pinnacles(_ctx())
        # 1990-03-21 -> m=3 d=3 y=1 -> pinnacles 6/4/1/4, challenges 0/2/2/2
        self.assertEqual(r.detail["all_pinnacles"], [6, 4, 1, 4])
        self.assertEqual(r.detail["all_challenges"], [0, 2, 2, 2])


class TestReturns(unittest.TestCase):
    def test_solar_return_near_birthday(self):
        from unicosm.systems.returns import solar_return
        r = solar_return(_ctx())
        # natal Sun ~0° Aries -> solar return falls in March
        self.assertTrue(r.detail["date"].startswith("2026-03"))

    def test_lunar_return_recent(self):
        from datetime import date
        from unicosm.systems.returns import lunar_return
        r = lunar_return(_ctx())
        d = date.fromisoformat(r.detail["date"])
        days = (date(2026, 6, 13) - d).days
        self.assertTrue(0 <= days <= 28)   # within the current lunar month


class TestProgressions(unittest.TestCase):
    def test_progressed_sun_advances(self):
        from unicosm.systems.progressions import reading
        r = reading(_ctx())
        self.assertEqual(r.cadence.value, "decade")
        # ~36 yrs -> progressed Sun ~36° past natal 0° Aries -> Taurus
        self.assertIn("Taurus", r.detail["progressed_sun"])


class TestTransits(unittest.TestCase):
    def test_transits_run(self):
        from unicosm.systems.transits import reading
        r = reading(_ctx())
        self.assertEqual(r.cadence.value, "daily")
        self.assertEqual(r.layer.value, "personal")
        self.assertIn("active", r.detail)


class TestIChing(unittest.TestCase):
    def test_binary_map(self):
        from unicosm.data.iching import BINARY_TO_NUMBER
        self.assertEqual(len(set(BINARY_TO_NUMBER.values())), 64)
        self.assertEqual(BINARY_TO_NUMBER["111111"], 1)
        self.assertEqual(BINARY_TO_NUMBER["000000"], 2)
        self.assertEqual(BINARY_TO_NUMBER["111000"], 11)   # Peace
        self.assertEqual(BINARY_TO_NUMBER["101010"], 63)   # After Completion

    def test_cast_deterministic(self):
        import random
        from unicosm.divination.iching import cast
        a = cast(random.Random(7))
        b = cast(random.Random(7))
        self.assertEqual(a.primary, b.primary)
        self.assertTrue(1 <= a.primary <= 64)
        if a.changing_lines:
            self.assertIsNotNone(a.relating)


class TestTarot(unittest.TestCase):
    def test_deck_and_draw(self):
        import random
        from unicosm.divination.tarot import _deck, draw_cards
        deck = _deck()
        self.assertEqual(len(deck), 78)
        self.assertEqual(len({c[0] for c in deck}), 78)
        spread = draw_cards(random.Random(9), 3)
        self.assertEqual(len(spread), 3)
        # deterministic
        self.assertEqual(draw_cards(random.Random(9), 3)[0].name, spread[0].name)


class TestRunes(unittest.TestCase):
    def test_deck_and_invertibility(self):
        import random
        from unicosm.data.runes import RUNES
        from unicosm.divination.runes import draw_runes
        self.assertEqual(len(RUNES), 24)
        # symmetric runes carry no reversed text and never come up merkstave
        for name, glyph, up, rev, invertible in RUNES:
            if not invertible:
                self.assertEqual(rev, "")
        spread = draw_runes(random.Random(5), 3)
        self.assertEqual(len(spread), 3)
        for r in spread:
            if r.merkstave:
                self.assertTrue(r.reversed_meaning)


class TestBaZi(unittest.TestCase):
    def test_year_pillar_metal_horse(self):
        from unicosm.systems.bazi import compute_bazi
        c = compute_bazi(_ctx())
        ys, yb = c["pillars"]["year"]
        from unicosm.systems.sexagenary import BRANCHES, STEMS
        # 1990 = Geng (Yang Metal) Wu (Horse)
        self.assertEqual(STEMS[ys][0], "Gēng")
        self.assertEqual(BRANCHES[yb][2], "Horse")
        # eight characters -> element tally sums to 8
        self.assertEqual(sum(c["tally"].values()), 8)

    def test_day_officer_runs(self):
        from unicosm.systems.bazi import day_officer
        r = day_officer(_ctx())
        self.assertEqual(r.cadence.value, "daily")
        self.assertTrue(r.summary)


class TestSky(unittest.TestCase):
    def test_mechanics(self):
        from unicosm.systems.sky import mechanics
        r = mechanics(_ctx())
        self.assertEqual(r.cadence.value, "daily")
        self.assertIn("moon_void_of_course", r.detail)
        self.assertIsInstance(r.detail["retrograde"], (list, str))

    def test_sky_data_eclipses(self):
        from unicosm.systems.sky import sky_data
        r = sky_data(_ctx())
        # eclipse dates resolve to ISO-ish strings
        self.assertRegex(r.detail["next_solar_eclipse"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(r.detail["next_lunar_eclipse"], r"^\d{4}-\d{2}-\d{2}$")

    def test_biodynamic_day_type(self):
        from unicosm.systems.biodynamic import reading
        r = reading(_ctx())
        self.assertIn(r.detail["day_type"],
                      {"Root day", "Leaf day", "Flower day", "Fruit/Seed day"})


class TestCheckin(unittest.TestCase):
    def test_roundtrip_and_upsert(self):
        from unicosm import store
        store.save_checkin("CheckUser", "2026-06-13", 4, 3, "ok", "snap1")
        store.save_checkin("CheckUser", "2026-06-13", 5, 5, "better", "snap2")  # upsert
        rows = store.recent_checkins("CheckUser")
        self.assertEqual(len(rows), 1)            # same day -> one row
        self.assertEqual(rows[0]["mood"], 5)
        self.assertEqual(rows[0]["snapshot"], "snap2")


class TestSynthesis(unittest.TestCase):
    def _r(self, key, cad, kws, score=None):
        from unicosm.models import Cadence, Layer, SystemReading
        return SystemReading(key=key, title=key, cadence=Cadence(cad),
                             layer=Layer.COSMIC, summary="", keywords=kws, score=score)

    def test_resonance_and_tension(self):
        from unicosm.synthesis.weave import synthesize
        readings = [
            self._r("a", "daily", ["rest"], 0.5),
            self._r("b", "hourly", ["rest"], -0.5),
            self._r("c", "year", ["rest"]),
            self._r("d", "season", ["grow"]),
        ]
        syn = synthesize(readings)
        self.assertTrue(any("rest" in r for r in syn.resonances))   # 3 systems
        self.assertTrue(syn.tensions)                               # +0.5 vs -0.5
        self.assertIn("Today", syn.cadence_weather)                 # daily bucket labeled

    def test_real_report_resonates(self):
        rep = daily_report(make_profile(),
                           datetime(2026, 6, 13, 9, 30, tzinfo=ZoneInfo("Europe/Kyiv")),
                           use_llm=False)
        self.assertIsInstance(rep.synthesis.resonances, list)
        self.assertTrue(rep.synthesis.cadence_weather)


class TestLLM(unittest.TestCase):
    def test_no_key_and_cache(self):
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        from unicosm.synthesis import llm
        from unicosm.synthesis.weave import synthesize
        from unicosm.systems import all_readings
        rds = all_readings(_ctx())
        base = synthesize(rds)
        self.assertIsNone(llm.enhance(rds, base))         # no key -> None
        path = llm._cache_path(llm._payload(rds, base))
        path.write_text("woven.", encoding="utf-8")
        self.assertEqual(llm.enhance(rds, base), "woven.")  # cache hit


class TestDailyReport(unittest.TestCase):
    def test_full_report(self):
        rep = daily_report(
            make_profile(),
            datetime(2026, 6, 13, 9, 30, tzinfo=ZoneInfo("Europe/Kyiv")),
            use_llm=False,
        )
        # every cadence layer represented (>= 18 systems now)
        self.assertGreaterEqual(len(rep.readings), 32)
        cadences = {r.cadence.value for r in rep.readings}
        for expected in ("hourly", "daily", "lunar_month", "season",
                         "year", "decade", "era", "blueprint"):
            self.assertIn(expected, cadences)
        self.assertTrue(rep.synthesis.headline)
        self.assertTrue(rep.synthesis.accents)
        self.assertTrue(rep.routine)
        # no system errored out
        for r in rep.readings:
            self.assertNotEqual(r.title, "(system error)", r.summary)


if __name__ == "__main__":
    unittest.main()
