# exposure/heat_exposure/test_heat_state.py
import unittest
import tempfile
import os
import json
import heat_state as hs

LIMIT = 25.0

def reading(timestamp_s, temp_c, shipment_id="SHP-1001", ok=True):
    return {
        "device_id": "BOX-001",
        "shipment_id": shipment_id,
        "seq": 1,
        "timestamp_s": timestamp_s,
        "temp_c": temp_c,
        "ok": ok,
        "error": None if ok else "sensor_timeout"
    }

class TestHeatState(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "heat_state.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, data):
        with open(self.path, "wb") as f:
            f.write(data)

    def test_saved_state_loads_back(self):
        state = {"heat_s": 900, "last_good": reading(900, 26.0)}
        self.assertTrue(hs.save_heat_state(state, self.path))
        self.assertEqual(hs.load_heat_state("SHP-1001", self.path), state)

    def test_no_saved_state_gives_none(self):
        self.assertIsNone(hs.load_heat_state("SHP-1001", self.path))

    def test_state_from_another_shipment_is_not_used(self):
        old = {"heat_s": 900, "last_good": reading(900, 26.0, "SHP-1000")}
        hs.save_heat_state(old, self.path)
        self.assertIsNone(hs.load_heat_state("SHP-1001", self.path))

    def test_broken_or_wrong_file_gives_none(self):
        good = reading(900, 26.0)
        for data in (b'{"heat_s": 9', b"\xff\xfe", b"[1, 2]", json.dumps({"heat_s": -5, "last_good": good}).encode()):
            self.write_raw(data)
            self.assertIsNone(hs.load_heat_state("SHP-1001", self.path))

    def test_save_never_raises(self):
        bad_path = os.path.join(self.dir.name, "no_folder", "heat_state.json")
        self.assertFalse(hs.save_heat_state({"heat_s": 0, "last_good": None}, bad_path))

    def test_each_reading_is_saved(self):
        state = hs.heat_on_reading(None, reading(0, 26.0), LIMIT, self.path)
        state = hs.heat_on_reading(state, reading(300, 26.0), LIMIT, self.path)
        self.assertEqual(state["heat_s"], 300)
        self.assertEqual(hs.load_heat_state("SHP-1001", self.path), state)

if __name__ == "__main__":
    unittest.main()