# Acceptance tests for story 004-2 Accumulate freeze exposure.
#   AC1. Time below the lower threshold accumulates separately from heat.
#   AC2. Freeze events are not offset by later warming.
# The whole flow on the box: exposure_limits.json -> readings -> freeze_on_reading()
# (freeze_exposure + freeze_state, Sia), with heat_increment_s (Aleef, 004-1)
# counted next to it. Run from exposure/:  python -m unittest test_acceptance_004_2
# No hardware, clock or network: the files live in a temporary folder.
import json
import os
import tempfile
import unittest

import exposure_limits
from freeze_state import freeze_on_reading, load_freeze_state
from heat_exposure.heat_exposure import heat_increment_s

SHIPMENT = "SHP-1001"


def reading(ts, temp_c):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": temp_c, "ok": True, "error": None}


def failed(ts):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": None, "ok": False, "error": "sensor_timeout"}


def trip(*temps):
    """One reading every 300 s; None means a failed read."""
    return [failed(i * 300) if t is None else reading(i * 300, t) for i, t in enumerate(temps)]


class Story004_2AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.limits_path = os.path.join(self.dir.name, "exposure_limits.json")
        self.state_path = os.path.join(self.dir.name, "freeze_state.json")
        exposure_limits.save({"lower_limit_c": 2.0, "upper_limit_c": 8.0}, self.limits_path)

    def tearDown(self):
        self.dir.cleanup()

    def run_trip(self, records, state=None):
        """Returns (freeze state, heat_s, freeze_s after every reading)."""
        limits = exposure_limits.load(self.limits_path)
        heat_s, totals = 0, []
        for record in records:
            last_good = state["last_good"] if state else None
            heat_s += heat_increment_s(last_good, record, limits["upper_limit_c"])
            state = freeze_on_reading(state, record, limits["lower_limit_c"], self.state_path)
            totals.append(state["freeze_s"])
        return state, heat_s, totals

    # TC-22 (AC1)
    def test_freeze_and_heat_are_two_separate_totals(self):
        # 600 s too warm, then 600 s too cold, then back in range
        state, heat_s, _ = self.run_trip(trip(9.0, 9.0, 1.0, 1.0, 4.0))
        self.assertEqual(heat_s, 600)
        self.assertEqual(state["freeze_s"], 600)
        # warm only: no freeze; cold only: no heat (each trip with its own state file)
        self.state_path = os.path.join(self.dir.name, "warm_trip.json")
        state, heat_s, _ = self.run_trip(trip(9.0, 9.5, 10.0, 9.0))
        self.assertEqual((heat_s, state["freeze_s"]), (900, 0))
        self.state_path = os.path.join(self.dir.name, "cold_trip.json")
        state, heat_s, _ = self.run_trip(trip(1.0, 0.5, 1.5, 1.0))
        self.assertEqual((heat_s, state["freeze_s"]), (0, 900))

    # TC-23 (AC1)
    def test_saved_file_holds_freeze_only(self):
        self.run_trip(trip(9.0, 9.0, 1.0, 1.0, 4.0))
        with open(self.state_path, "rb") as f:
            saved = json.loads(f.read().decode())
        self.assertEqual(sorted(saved), ["freeze_s", "last_good"])
        self.assertEqual(saved["freeze_s"], 600)

    # TC-24 (AC1, threshold from the config file)
    def test_lower_threshold_comes_from_the_config_file(self):
        exposure_limits.save({"lower_limit_c": 1.0, "upper_limit_c": 8.0}, self.limits_path)
        state, _, _ = self.run_trip(trip(1.5, 1.5, 0.5, 4.0))
        self.assertEqual(state["freeze_s"], 300)  # only the 0.5 C reading is below 1.0

    # TC-25 (AC2)
    def test_later_warming_never_offsets_freeze(self):
        # cold for 900 s, then too warm for a long time, then back in range
        temps = (1.0, 1.0, 1.0, 9.0, 12.0, 15.0, 9.0, 5.0, 4.0)
        state, heat_s, totals = self.run_trip(trip(*temps))
        self.assertEqual(totals[3:], [900] * 6)  # stays 900 after the cold ends
        self.assertTrue(all(a <= b for a, b in zip(totals, totals[1:])))
        self.assertEqual(heat_s, 1200)  # the warm time goes to heat, not off freeze

    # TC-26 (AC2)
    def test_freeze_is_not_lost_after_a_power_cut_or_clock_restart(self):
        state, _, _ = self.run_trip(trip(1.0, 1.0, 1.0))  # 600 s of freeze
        state = load_freeze_state(SHIPMENT, self.state_path)  # power cut: load from flash
        self.assertEqual(state["freeze_s"], 600)
        # without an RTC the clock restarts at 0: no negative time, no reset
        state, _, totals = self.run_trip([reading(0, 4.0), reading(300, 9.0), reading(600, 4.0)], state)
        self.assertEqual(totals, [600, 600, 600])


if __name__ == "__main__":
    unittest.main()
