# Tests for story 007-1 AC3: alert immediately when the box shows red at handoff.
# Code under test: detect_handoff_risk.py (Pun).
# Behavior rules: docs/decisions-and-open-questions.md

import json
import unittest

import contracts
from detect_handoff_risk import detect_handoff_risk


def make_handoff(status, timestamp_s=7200):
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001",
            "timestamp_s": timestamp_s, "status": status}


class DetectHandoffRiskTest(unittest.TestCase):
    def test_red_handoff_gives_red_at_handoff_event(self):
        handoff = make_handoff(contracts.RED)
        event = detect_handoff_risk(handoff)
        self.assertIsNotNone(event)
        self.assertEqual(event["type"], contracts.RED_AT_HANDOFF)

    def test_red_event_copies_ids_and_time_from_handoff(self):
        handoff = make_handoff(contracts.RED, timestamp_s=10800)
        event = detect_handoff_risk(handoff)
        self.assertEqual(event["device_id"], handoff["device_id"])
        self.assertEqual(event["shipment_id"], handoff["shipment_id"])
        self.assertEqual(event["timestamp_s"], handoff["timestamp_s"])

    def test_red_event_has_every_risk_event_key(self):
        event = detect_handoff_risk(make_handoff(contracts.RED))
        for key in contracts.RISK_EVENT_KEYS:
            self.assertIn(key, event, key)

    def test_green_handoff_gives_none(self):
        self.assertIsNone(detect_handoff_risk(make_handoff(contracts.GREEN)))

    def test_input_is_not_changed(self):
        for status in (contracts.RED, contracts.GREEN):
            handoff = make_handoff(status)
            before = json.dumps(handoff, sort_keys=True)
            detect_handoff_risk(handoff)
            self.assertEqual(json.dumps(handoff, sort_keys=True), before, status)


if __name__ == "__main__":
    unittest.main()
