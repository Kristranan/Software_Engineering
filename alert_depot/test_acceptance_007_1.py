# Acceptance tests for story 007-1 "Alert depot on risk" (AC1-AC5), end to end:
# load config -> detect_risk / detect_handoff_risk -> AlertSender -> depot.
# Network and depot are fakes; buffer readings come from test_data/.
# Behavior rules: docs/decisions-and-open-questions.md

import json
import os
import tempfile
import unittest

import contracts
from alert_config import load_alert_config
from alert_sender import AlertSender
from detect_handoff_risk import detect_handoff_risk
from detect_risk import detect_risk

TEST_DATA = os.path.join(os.path.dirname(__file__), "test_data")
TEST_CONFIG = os.path.join(TEST_DATA, "alert_thresholds_test.json")


class FakeNetwork:
    def __init__(self, online):
        self.online = online

    def is_online(self):
        return self.online


class FakeDepot:
    def __init__(self):
        self.received = []

    def receive(self, event):
        self.received.append(event)


def load_history(name):
    with open(os.path.join(TEST_DATA, name)) as f:
        return json.load(f)


def make_handoff(status, timestamp_s):
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001",
            "timestamp_s": timestamp_s, "status": status}


class Box:
    """Simulated box: checks risk after each new reading and sends alerts."""

    def __init__(self, config, network):
        self.config = config
        self.depot = FakeDepot()
        self.sender = AlertSender(network, self.depot)
        self.sent = []          # every event passed to send(), in order

    def run_readings(self, readings):
        history = []
        for reading in readings:
            history.append(reading)
            for event in detect_risk(history, self.config):
                self.sent.append(event)
                self.sender.send(event)

    def handoff(self, handoff):
        event = detect_handoff_risk(handoff)
        if event is not None:
            self.sent.append(event)
            self.sender.send(event)


class AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.network = FakeNetwork(online=True)
        self.box = Box(load_alert_config(TEST_CONFIG), self.network)

    def received_types(self):
        return [e["type"] for e in self.box.depot.received]

    def test_ac1_low_buffer_alert_reaches_depot(self):
        self.box.run_readings(load_history("low_buffer.json"))
        self.assertEqual(self.received_types(), [contracts.LOW_BUFFER])
        self.assertEqual(self.box.depot.received[0]["timestamp_s"], 7200)

    def test_ac2_fast_depletion_alert_reaches_depot(self):
        self.box.run_readings(load_history("fast_depletion.json"))
        self.assertEqual(self.received_types(), [contracts.FAST_DEPLETION])

    def test_no_alert_for_normal_and_boundary(self):
        self.box.run_readings(load_history("normal.json"))
        self.box.run_readings(load_history("boundary.json"))
        self.assertEqual(self.box.depot.received, [])

    def test_ac3_red_handoff_alerts_depot_immediately(self):
        self.box.handoff(make_handoff(contracts.RED, 7200))
        self.assertEqual(self.received_types(), [contracts.RED_AT_HANDOFF])
        self.assertEqual(self.box.sender.pending_count(), 0)

    def test_ac3_green_handoff_sends_nothing(self):
        self.box.handoff(make_handoff(contracts.GREEN, 7200))
        self.assertEqual(self.box.depot.received, [])

    def test_ac4_changed_config_file_changes_alerts(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "alert_thresholds.json")
            with open(path, "w") as f:
                json.dump({"low_buffer_threshold_pct": 35,
                           "max_depletion_pct_per_hour": 5}, f)
            box = Box(load_alert_config(path), FakeNetwork(online=True))
        box.run_readings(load_history("boundary.json"))   # newest 30 < 35
        self.assertEqual([e["type"] for e in box.depot.received],
                         [contracts.LOW_BUFFER])

    def test_ac5_offline_alerts_wait_then_arrive_once_in_order(self):
        self.network.online = False
        self.box.run_readings(load_history("both.json"))
        self.box.handoff(make_handoff(contracts.RED, 7200))
        self.assertEqual(self.box.depot.received, [])
        self.assertEqual(self.box.sender.pending_count(), 3)

        self.network.online = True
        self.box.sender.flush()
        self.box.sender.flush()
        self.assertEqual(self.box.depot.received, self.box.sent)
        self.assertEqual(len(self.box.depot.received), 3)
        self.assertEqual(self.box.sender.pending_count(), 0)


if __name__ == "__main__":
    unittest.main()
