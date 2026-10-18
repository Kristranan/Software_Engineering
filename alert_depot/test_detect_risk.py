# Tests for story 007-1 AC1 (low buffer) and AC2 (fast depletion).
# Code under test: detect_risk.py (Sia).
# Behavior rules: docs/decisions-and-open-questions.md ("detect_risk", A1, A2)
#
# Not asserted yet (proposed, not agreed): the "value" field (C1), the order
# of two events (C2), same/out-of-order timestamps (C3), empty history.

import json
import os
import unittest

import contracts
from detect_risk import detect_risk

TEST_DATA = os.path.join(os.path.dirname(__file__), "test_data")

# Test values only (assumption A4), same as test_data/alert_thresholds_test.json.
CONFIG = {"low_buffer_threshold_pct": 30, "max_depletion_pct_per_hour": 5}


def load_history(name):
    with open(os.path.join(TEST_DATA, name)) as f:
        return json.load(f)


def make_snapshot(timestamp_s, pct):
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001",
            "timestamp_s": timestamp_s, "remaining_buffer_pct": pct}


def types_of(events):
    return sorted(e["type"] for e in events)


class DetectRiskScenarioTest(unittest.TestCase):
    def test_normal_gives_no_risk_at_any_reading(self):
        history = load_history("normal.json")
        for n in range(1, len(history) + 1):
            self.assertEqual(detect_risk(history[:n], CONFIG), [], n)

    def test_low_buffer_only_on_the_last_reading(self):
        history = load_history("low_buffer.json")   # 34, 32, 29.9
        self.assertEqual(detect_risk(history[:1], CONFIG), [])
        self.assertEqual(detect_risk(history[:2], CONFIG), [])
        self.assertEqual(types_of(detect_risk(history, CONFIG)),
                         [contracts.LOW_BUFFER])

    def test_fast_depletion(self):
        history = load_history("fast_depletion.json")   # 80 -> 70 = 10 %/h
        self.assertEqual(types_of(detect_risk(history, CONFIG)),
                         [contracts.FAST_DEPLETION])

    def test_both_risks_at_once(self):
        history = load_history("both.json")   # 40 -> 28 = 12 %/h, 28 < 30
        events = detect_risk(history, CONFIG)
        self.assertEqual(types_of(events),
                         sorted([contracts.LOW_BUFFER, contracts.FAST_DEPLETION]))

    def test_boundary_gives_no_risk(self):
        # 30 is not below 30 (A1); 5 %/h is not above 5 (A2).
        history = load_history("boundary.json")
        self.assertEqual(detect_risk(history, CONFIG), [])


class DetectRiskRuleTest(unittest.TestCase):
    def test_low_buffer_with_a_single_snapshot(self):
        history = [make_snapshot(0, 29.9)]
        self.assertEqual(types_of(detect_risk(history, CONFIG)),
                         [contracts.LOW_BUFFER])

    def test_single_snapshot_above_threshold_gives_no_risk(self):
        self.assertEqual(detect_risk([make_snapshot(0, 30)], CONFIG), [])

    def test_rate_uses_time_between_readings_fast(self):
        # 80 -> 76 in half an hour = 8 %/h > 5
        history = [make_snapshot(0, 80), make_snapshot(1800, 76)]
        self.assertEqual(types_of(detect_risk(history, CONFIG)),
                         [contracts.FAST_DEPLETION])

    def test_rate_uses_time_between_readings_slow(self):
        # 80 -> 74 in two hours = 3 %/h, not above 5
        history = [make_snapshot(0, 80), make_snapshot(7200, 74)]
        self.assertEqual(detect_risk(history, CONFIG), [])

    def test_only_the_two_newest_snapshots_count_for_the_rate(self):
        # Big drop earlier (90 -> 70), but the newest step 70 -> 69 is 1 %/h.
        history = [make_snapshot(0, 90), make_snapshot(3600, 70),
                   make_snapshot(7200, 69)]
        self.assertEqual(detect_risk(history, CONFIG), [])

    def test_events_copy_ids_and_time_from_newest_snapshot(self):
        history = load_history("both.json")
        history[-1]["device_id"] = "BOX-002"
        history[-1]["shipment_id"] = "SHP-2002"
        newest = history[-1]
        events = detect_risk(history, CONFIG)
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertEqual(event["device_id"], newest["device_id"])
            self.assertEqual(event["shipment_id"], newest["shipment_id"])
            self.assertEqual(event["timestamp_s"], newest["timestamp_s"])

    def test_events_have_every_risk_event_key(self):
        for event in detect_risk(load_history("both.json"), CONFIG):
            for key in contracts.RISK_EVENT_KEYS:
                self.assertIn(key, event, key)

    def test_history_is_not_changed(self):
        for name in ("normal.json", "low_buffer.json", "fast_depletion.json",
                     "both.json", "boundary.json"):
            history = load_history(name)
            before = json.dumps(history, sort_keys=True)
            detect_risk(history, CONFIG)
            self.assertEqual(json.dumps(history, sort_keys=True), before, name)


if __name__ == "__main__":
    unittest.main()
