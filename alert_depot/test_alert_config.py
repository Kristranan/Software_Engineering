# Tests for story 007-1 AC4: thresholds are configurable without code change.
# Code under test: alert_config.py and detect_risk.py (Sia).
# Behavior rules: docs/decisions-and-open-questions.md
#
# Not asserted yet: what happens with a bad or missing config file
# (open question 4, Sia decides with the team).

import json
import os
import tempfile
import unittest

import contracts
from alert_config import load_alert_config
from detect_risk import detect_risk

TEST_DATA = os.path.join(os.path.dirname(__file__), "test_data")


def load_history(name):
    with open(os.path.join(TEST_DATA, name)) as f:
        return json.load(f)


class LoadAlertConfigTest(unittest.TestCase):
    def test_loads_both_keys_from_test_file(self):
        config = load_alert_config(
            os.path.join(TEST_DATA, "alert_thresholds_test.json"))
        for key in contracts.ALERT_CONFIG_KEYS:
            self.assertIn(key, config, key)
        self.assertEqual(config["low_buffer_threshold_pct"], 30)
        self.assertEqual(config["max_depletion_pct_per_hour"], 5)


class ThresholdsFromFileTest(unittest.TestCase):
    """AC4: change the JSON file, the result changes, no code change."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "alert_thresholds.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_config(self, low, max_rate):
        with open(self.path, "w") as f:
            json.dump({"low_buffer_threshold_pct": low,
                       "max_depletion_pct_per_hour": max_rate}, f)

    def test_higher_low_buffer_threshold_changes_result(self):
        history = load_history("boundary.json")   # newest = 30 %, 5 %/h
        self.write_config(30, 5)
        self.assertEqual(detect_risk(history, load_alert_config(self.path)), [])
        self.write_config(35, 5)
        events = detect_risk(history, load_alert_config(self.path))
        self.assertEqual([e["type"] for e in events], [contracts.LOW_BUFFER])

    def test_higher_max_depletion_changes_result(self):
        history = load_history("fast_depletion.json")   # 10 %/h
        self.write_config(30, 5)
        events = detect_risk(history, load_alert_config(self.path))
        self.assertEqual([e["type"] for e in events], [contracts.FAST_DEPLETION])
        self.write_config(30, 15)
        self.assertEqual(detect_risk(history, load_alert_config(self.path)), [])


if __name__ == "__main__":
    unittest.main()
