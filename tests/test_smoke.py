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


class TestDailyReport(unittest.TestCase):
    def test_full_report(self):
        rep = daily_report(
            make_profile(),
            datetime(2026, 6, 13, 9, 30, tzinfo=ZoneInfo("Europe/Kyiv")),
            use_llm=False,
        )
        # every cadence layer represented (>= 18 systems now)
        self.assertGreaterEqual(len(rep.readings), 20)
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
