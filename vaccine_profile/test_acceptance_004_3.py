# Acceptance tests for story 004-3 Compare against vaccine profile.
# The whole flow on the box: profile.json on flash -> readings -> heat_s and freeze_s
# (Shogun's update_and_compare, with Aleef's and Sia's code) -> compare.
# Run from the repo root, like Shogun's tests:
#   python -m unittest discover -s vaccine_profile
# No hardware, clock or network: the profile is a file in a temporary folder.
import os
import tempfile
import unittest
from unittest import mock

import profile_check as check
from exposure_comparison import update_and_compare
from profile_loader import load_profile

UPPER_C = 8.0
LOWER_C = 2.0


def reading(t, temp_c):
    return {"timestamp_s": t, "temp_c": temp_c, "ok": True}


# R1: the time between two good readings is counted by the earlier one.
#   0 -> 60    9.0 C  heat   +60
#   60 -> 120  9.0 C  heat   +60  (heat_s = 120)
#   120 -> 180 1.0 C  freeze +60
#   180 -> 240 1.0 C  freeze +60  (freeze_s = 120)
TRIP = [reading(0, 9.0), reading(60, 9.0), reading(120, 1.0), reading(180, 1.0), reading(240, 4.0)]


class Story004_3AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "profile.json")
        # heat limit below the trip's 120 s, freeze limit equal to it
        with open(self.path, "w") as f:
            f.write('{"heat_limit_s": 119, "freeze_limit_s": 120}')

    def tearDown(self):
        self.dir.cleanup()

    def run_trip(self):
        profile = load_profile(self.path)
        state = None
        for record in TRIP:
            state, _ = update_and_compare(state, record, profile, UPPER_C, LOWER_C)
        return check.check_exposure(state["heat_s"], state["freeze_s"], self.path)

    # TC12 (AC1 compared to the loaded profile, AC2 heat and freeze each against its own limit)
    def test_trip_is_compared_with_limits_loaded_from_the_profile_file(self):
        self.assertEqual(self.run_trip(), {"heat_exceeded": True, "freeze_exceeded": False})

    # TC13 (AC3 comparison runs entirely on the box)
    def test_whole_trip_runs_with_no_network(self):
        def no_network(*args, **kwargs):
            raise OSError("network used")

        with mock.patch("socket.socket", no_network), \
                mock.patch("socket.create_connection", no_network), \
                mock.patch("socket.getaddrinfo", no_network):
            result = self.run_trip()
        self.assertEqual(result, {"heat_exceeded": True, "freeze_exceeded": False})


if __name__ == "__main__":
    unittest.main()
