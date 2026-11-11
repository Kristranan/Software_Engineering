# Tests for freeze_state.py (004-2: keep the freeze total across a power cut).
# No hardware, clock or network: every test uses a temporary folder.
import json
import os
import tempfile
import unittest

import freeze_state as fs

LIMIT = 2.0


def reading(ts, temp_c, shipment_id="SHP-1001"):
    return {"device_id": "BOX-001", "shipment_id": shipment_id, "seq": 1,
            "timestamp_s": ts, "temp_c": temp_c, "ok": True, "error": None}


class FreezeStateTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "freeze_state.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, data):
        with open(self.path, "wb") as f:
            f.write(data)

    def test_saved_state_loads_back(self):
        state = {"freeze_s": 900, "last_good": reading(900, 0.5)}
        self.assertTrue(fs.save_freeze_state(state, self.path))
        self.assertEqual(fs.load_freeze_state("SHP-1001", self.path), state)

    def test_no_saved_state_gives_none(self):
        self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path))

    def test_state_from_another_shipment_is_not_used(self):
        old = {"freeze_s": 900, "last_good": reading(900, 0.5, "SHP-1000")}
        fs.save_freeze_state(old, self.path)
        self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path))

    def test_broken_or_wrong_file_gives_none(self):
        good = reading(900, 0.5)
        for data in (b'{"freeze_s": 9',  # cut off in the middle
                     b"\xff\xfe",  # not text
                     b"[1, 2]",
                     json.dumps({"freeze_s": -5, "last_good": good}).encode(),
                     json.dumps({"freeze_s": True, "last_good": good}).encode(),
                     json.dumps({"freeze_s": "900", "last_good": good}).encode(),
                     json.dumps({"freeze_s": 900, "last_good": "BOX-001"}).encode()):
            self.write_raw(data)
            self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path), data)

    def test_save_never_raises(self):
        path = os.path.join(self.dir.name, "no_such_folder", "freeze_state.json")
        self.assertFalse(fs.save_freeze_state({"freeze_s": 0, "last_good": None}, path))

    def test_each_reading_is_saved(self):
        state = fs.freeze_on_reading(None, reading(0, 0.5), LIMIT, self.path)
        state = fs.freeze_on_reading(state, reading(300, 0.5), LIMIT, self.path)
        self.assertEqual(state["freeze_s"], 300)
        self.assertEqual(fs.load_freeze_state("SHP-1001", self.path), state)

    # --- acceptance criteria across a power cut (pass once TC-13 to TC-18 pass)

    def test_total_survives_a_power_cut(self):
        # AC2: after a restart the box loads the total and keeps adding to it.
        state = None
        for ts, temp in ((0, 0.5), (300, 0.5), (600, 0.5)):
            state = fs.freeze_on_reading(state, reading(ts, temp), LIMIT, self.path)
        self.assertEqual(state["freeze_s"], 600)
        # power cut: everything in memory is gone
        state = fs.load_freeze_state("SHP-1001", self.path)
        self.assertEqual(state["freeze_s"], 600)
        state = fs.freeze_on_reading(state, reading(900, 4.0), LIMIT, self.path)
        self.assertEqual(state["freeze_s"], 900)

    def test_leftover_temp_file_from_a_cut_save_is_ignored(self):
        state = {"freeze_s": 300, "last_good": reading(300, 0.5)}
        fs.save_freeze_state(state, self.path)
        with open(self.path + ".tmp", "wb") as f:
            f.write(b'{"freeze_s": 6')  # save cut off by a power cut
        self.assertEqual(fs.load_freeze_state("SHP-1001", self.path), state)
        newer = {"freeze_s": 600, "last_good": reading(600, 0.5)}
        self.assertTrue(fs.save_freeze_state(newer, self.path))
        self.assertEqual(fs.load_freeze_state("SHP-1001", self.path), newer)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_new_shipment_starts_at_zero_even_with_an_old_file(self):
        fs.freeze_on_reading(None, reading(0, 0.5, "SHP-1000"), LIMIT, self.path)
        fs.freeze_on_reading(fs.load_freeze_state("SHP-1000", self.path),
                             reading(300, 0.5, "SHP-1000"), LIMIT, self.path)
        state = fs.load_freeze_state("SHP-1001", self.path)
        self.assertIsNone(state)
        state = fs.freeze_on_reading(state, reading(600, 4.0), LIMIT, self.path)
        self.assertEqual(state["freeze_s"], 0)

    def test_saved_file_holds_freeze_only(self):
        # AC1: heat is never written into the freeze file.
        fs.freeze_on_reading(None, reading(0, 9.0), LIMIT, self.path)
        with open(self.path, "rb") as f:
            saved = json.loads(f.read().decode())
        self.assertEqual(sorted(saved), ["freeze_s", "last_good"])


if __name__ == "__main__":
    unittest.main()
