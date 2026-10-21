# Tests for story 007-1 AC5: with no signal the alert waits in a queue and is
# sent when signal returns. It must never disappear.
# Code under test: alert_sender.py (Pun).
# Behavior rules: docs/decisions-and-open-questions.md ("AlertSender", A5)

import unittest

import contracts
from alert_sender import AlertSender


class FakeNetwork:
    """Simulated signal. Only is_online(), as in contracts.py."""

    def __init__(self, online):
        self.online = online

    def is_online(self):
        return self.online


class FakeDepot:
    """Simulated depot inbox. Only receive(event), as in contracts.py."""

    def __init__(self):
        self.received = []

    def receive(self, event):
        self.received.append(event)


def make_event(timestamp_s, risk_type=contracts.LOW_BUFFER):
    return {"type": risk_type, "device_id": "BOX-001",
            "shipment_id": "SHP-1001", "timestamp_s": timestamp_s}


class AlertSenderTest(unittest.TestCase):
    def setUp(self):
        self.network = FakeNetwork(online=True)
        self.depot = FakeDepot()
        self.sender = AlertSender(self.network, self.depot)

    def test_online_alert_is_delivered_immediately(self):
        a = make_event(0)
        self.sender.send(a)
        self.assertEqual(self.depot.received, [a])
        self.assertEqual(self.sender.pending_count(), 0)

    def test_offline_alert_is_queued_not_delivered(self):
        self.network.online = False
        self.sender.send(make_event(0))
        self.sender.send(make_event(3600))
        self.assertEqual(self.depot.received, [])
        self.assertEqual(self.sender.pending_count(), 2)

    def test_flush_after_signal_returns_delivers_queue(self):
        self.network.online = False
        a, b = make_event(0), make_event(3600, contracts.FAST_DEPLETION)
        self.sender.send(a)
        self.sender.send(b)
        self.network.online = True
        self.sender.flush()
        self.assertEqual(self.depot.received, [a, b])
        self.assertEqual(self.sender.pending_count(), 0)

    def test_order_is_kept_when_sending_online_after_offline(self):
        # Send A offline, signal returns, send B: the depot must get A then B.
        # Follows from two rules: "online: the depot receives the alert
        # immediately" and "alerts reach the depot in the order they were sent".
        self.network.online = False
        a = make_event(0)
        self.sender.send(a)
        self.network.online = True
        b = make_event(3600, contracts.RED_AT_HANDOFF)
        self.sender.send(b)
        self.assertEqual(self.depot.received, [a, b])
        self.assertEqual(self.sender.pending_count(), 0)
        self.sender.flush()
        self.assertEqual(self.depot.received, [a, b])

    def test_flush_twice_never_delivers_an_alert_twice(self):
        self.network.online = False
        a = make_event(0)
        self.sender.send(a)
        self.network.online = True
        self.sender.flush()
        self.sender.flush()
        self.assertEqual(self.depot.received, [a])
        self.assertEqual(self.sender.pending_count(), 0)

    def test_flush_while_offline_delivers_nothing_and_loses_nothing(self):
        self.network.online = False
        a, b = make_event(0), make_event(3600)
        self.sender.send(a)
        self.sender.send(b)
        self.sender.flush()
        self.assertEqual(self.depot.received, [])
        self.assertEqual(self.sender.pending_count(), 2)
        self.network.online = True
        self.sender.flush()
        self.assertEqual(self.depot.received, [a, b])


if __name__ == "__main__":
    unittest.main()
