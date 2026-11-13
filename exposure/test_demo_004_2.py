# Tests for demo_004_2.py (004-2 demo for the Sprint Review).
# No hardware, clock or network: every test uses a temporary folder.
import os
import tempfile
import unittest

import demo_004_2 as demo

LIMITS = {"lower_limit_c": 2.0, "upper_limit_c": 8.0}


class DemoTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "freeze_state.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_trip_ends_with_the_right_freeze_total(self):
        rows = demo.run_trip(demo.TRIP, LIMITS, self.path)
        self.assertEqual([row["freeze_s"] for row in rows], [0, 0, 300, 300, 900, 900, 900])

    def test_label_says_what_was_counted(self):
        rows = demo.run_trip(demo.TRIP, LIMITS, self.path)
        self.assertEqual([row["label"] for row in rows], [
            "first reading",
            "300 s in range: +0",
            "300 s below 2.0 C: freeze +300 s",
            "failed read: counted at the next good reading",
            "600 s below 2.0 C: freeze +600 s",
            "300 s in range: +0",
            "300 s above 8.0 C: heat +300 s, freeze +0",
        ])

    def test_power_cut_keeps_the_total(self):
        rows = demo.run_trip(demo.TRIP, LIMITS, self.path, power_cut_after=4)
        self.assertEqual([row["freeze_s"] for row in rows], [0, 0, 300, 300, 300, 900, 900, 900])
        self.assertTrue(rows[4]["label"].startswith("POWER CUT"))


if __name__ == "__main__":
    unittest.main()
