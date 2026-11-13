# Tests for heat_state.py (004-1: keep the heat total across a power cut).
# No hardware, clock or network: every test uses a temporary folder.
import json
import os
import tempfile
import unittest

import heat_state as hs

LIMIT = 8.0


def reading(ts, temp_c, shipment_id="SHP-1001"):
    return {
        "device_id": "BOX-001",
        "shipment_id": shipment_id,
        "seq": 1,
        "timestamp_s": ts,
        "temp_c": temp_c,
        "ok": True,
        "error": None,
    }


class HeatStateTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "heat_state.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, data):
        with open(self.path, "wb") as f:
            f.write(data)

    def test_saved_state_loads_back(self):
        state = {"heat_s": 900, "last_good": reading(900, 9.5)}
        self.assertTrue(hs.save_heat_state(state, self.path))
        self.assertEqual(hs.load_heat_state("SHP-1001", self.path), state)

    def test_no_saved_state_gives_none(self):
        self.assertIsNone(hs.load_heat_state("SHP-1001", self.path))

    def test_state_from_another_shipment_is_not_used(self):
        old = {"heat_s": 900, "last_good": reading(900, 9.5, "SHP-1000")}
        hs.save_heat_state(old, self.path)
        self.assertIsNone(hs.load_heat_state("SHP-1001", self.path))

    def test_broken_or_wrong_file_gives_none(self):
        good = reading(900, 9.5)
        for data in (
            b'{"heat_s": 9',  # cut off in the middle
            b"\xff\xfe",  # not text
            b"[1, 2]",
            json.dumps({"heat_s": -5, "last_good": good}).encode(),
            json.dumps({"heat_s": True, "last_good": good}).encode(),
            json.dumps({"heat_s": "900", "last_good": good}).encode(),
            json.dumps({"heat_s": 900, "last_good": "BOX-001"}).encode(),
        ):
            self.write_raw(data)
            self.assertIsNone(hs.load_heat_state("SHP-1001", self.path), data)

    def test_save_never_raises(self):
        path = os.path.join(self.dir.name, "no_such_folder", "heat_state.json")
        self.assertFalse(hs.save_heat_state({"heat_s": 0, "last_good": None}, path))

    def test_each_reading_is_saved(self):
        state = hs.heat_on_reading(None, reading(0, 9.5), LIMIT, self.path)
        state = hs.heat_on_reading(state, reading(300, 9.5), LIMIT, self.path)
        self.assertEqual(state["heat_s"], 300)
        self.assertEqual(hs.load_heat_state("SHP-1001", self.path), state)

    # --- acceptance criteria across a power cut (pass once TC-13 to TC-18 pass)

    def test_total_survives_a_power_cut(self):
        # AC2: after a restart the box loads the total and keeps adding to it.
        state = None
        for ts, temp in ((0, 9.5), (300, 9.5), (600, 9.5)):
            state = hs.heat_on_reading(state, reading(ts, temp), LIMIT, self.path)
        self.assertEqual(state["heat_s"], 600)
        # power cut: everything in memory is gone
        state = hs.load_heat_state("SHP-1001", self.path)
        self.assertEqual(state["heat_s"], 600)
        state = hs.heat_on_reading(state, reading(900, 5.0), LIMIT, self.path)
        self.assertEqual(state["heat_s"], 900)

    def test_leftover_temp_file_from_a_cut_save_is_ignored(self):
        state = {"heat_s": 300, "last_good": reading(300, 9.5)}
        hs.save_heat_state(state, self.path)
        with open(self.path + ".tmp", "wb") as f:
            f.write(b'{"heat_s": 6')  # save cut off by a power cut
        self.assertEqual(hs.load_heat_state("SHP-1001", self.path), state)
        newer = {"heat_s": 600, "last_good": reading(600, 9.5)}
        self.assertTrue(hs.save_heat_state(newer, self.path))
        self.assertEqual(hs.load_heat_state("SHP-1001", self.path), newer)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_new_shipment_starts_at_zero_even_with_an_old_file(self):
        hs.heat_on_reading(None, reading(0, 9.5, "SHP-1000"), LIMIT, self.path)
        hs.heat_on_reading(
            hs.load_heat_state("SHP-1000", self.path),
            reading(300, 9.5, "SHP-1000"),
            LIMIT,
            self.path,
        )
        state = hs.load_heat_state("SHP-1001", self.path)
        self.assertIsNone(state)
        state = hs.heat_on_reading(state, reading(600, 5.0), LIMIT, self.path)
        self.assertEqual(state["heat_s"], 0)

    def test_saved_file_holds_heat_only(self):
        # AC1: freeze is never written into the heat file.
        hs.heat_on_reading(None, reading(0, 0.5), LIMIT, self.path)
        with open(self.path, "rb") as f:
            saved = json.loads(f.read().decode())
        self.assertEqual(sorted(saved), ["heat_s", "last_good"])


if __name__ == "__main__":
    unittest.main()