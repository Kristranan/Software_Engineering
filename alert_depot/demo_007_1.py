# Demo of story 007-1 "Alert depot on risk" for the Sprint Review. Owner: Pun.
# Desktop Python only: from alert_depot/, run  python demo_007_1.py
#
# Uses the real team code (alert_config, detect_risk, detect_handoff_risk,
# AlertSender). Only the network signal and the depot are simulated.
import json
import os
import tempfile

import alert_config
import contracts
from alert_sender import AlertSender
from detect_handoff_risk import detect_handoff_risk
from detect_risk import detect_risk

HERE = os.path.dirname(os.path.abspath(__file__))


class SimulatedNetwork:
    def __init__(self):
        self.online = True

    def is_online(self):
        return self.online


class PrintingDepot:
    def __init__(self):
        self.received = []

    def receive(self, event):
        self.received.append(event)
        print("      depot received: %s" % describe(event))


def describe(event):
    text = "%s (%s, %s)" % (event["type"], event["device_id"], event["shipment_id"])
    if event["type"] == contracts.LOW_BUFFER:
        text += " buffer %.1f%%" % event["value"]
    elif event["type"] == contracts.FAST_DEPLETION:
        text += " %.1f%%/hour" % event["value"]
    return text


def load_history(name):
    with open(os.path.join(HERE, "test_data", name + ".json")) as f:
        return json.load(f)


def show_buffer(history):
    return " -> ".join("%.1f%%" % s["remaining_buffer_pct"] for s in history)


def main():
    network = SimulatedNetwork()
    depot = PrintingDepot()
    sender = AlertSender(network, depot)

    print("=== Story 007-1 Alert depot on risk: demo ===")
    print()

    config = alert_config.load_alert_config(os.path.join(HERE, "alert_thresholds.json"))
    print("[AC4] Thresholds read from alert_thresholds.json:")
    print("      alert when buffer < %s%% or drops faster than %s%%/hour"
          % (config["low_buffer_threshold_pct"], config["max_depletion_pct_per_hour"]))
    print()

    normal = load_history("normal")
    print("[OK ] Normal trip, buffer %s" % show_buffer(normal))
    events = detect_risk(normal, config)
    print("      %d alerts" % len(events))
    print()

    low = load_history("low_buffer")
    print("[AC1] Buffer gets low: %s" % show_buffer(low))
    for event in detect_risk(low, config):
        sender.send(event)
    print()

    fast = load_history("fast_depletion")
    print("[AC2] Buffer drops fast: %s in one hour" % show_buffer(fast))
    for event in detect_risk(fast, config):
        sender.send(event)
    print()

    red = {"device_id": "BOX-002", "shipment_id": "SHP-1002",
           "timestamp_s": 7200, "status": contracts.RED}
    print("[AC3] Box BOX-002 shows RED at the clinic")
    sender.send(detect_handoff_risk(red))
    green = dict(red, device_id="BOX-003", shipment_id="SHP-1003", status=contracts.GREEN)
    print("      Box BOX-003 shows GREEN -> alert: %s" % detect_handoff_risk(green))
    print()

    print("[AC5] Signal lost (no network on the road)")
    network.online = False
    for event in detect_risk(low, config) + [detect_handoff_risk(red)]:
        sender.send(event)
        print("      %s waits in the queue (waiting: %d)"
              % (event["type"], sender.pending_count()))
    print("      Signal back -> flush()")
    network.online = True
    sender.flush()
    print("      waiting: %d" % sender.pending_count())
    before = len(depot.received)
    sender.flush()
    print("      flush() again -> %d alerts sent twice" % (len(depot.received) - before))
    print()

    one_reading = [{"device_id": "BOX-004", "shipment_id": "SHP-1004",
                    "timestamp_s": 0, "remaining_buffer_pct": 35.0}]
    print("[AC4] Buffer 35%% with threshold %s%% -> %d alerts"
          % (config["low_buffer_threshold_pct"], len(detect_risk(one_reading, config))))
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "alert_thresholds.json")
    with open(path, "w") as f:
        json.dump({"low_buffer_threshold_pct": 40, "max_depletion_pct_per_hour": 5}, f)
    changed = alert_config.load_alert_config(path)
    print("      Threshold changed to 40% in the file (no code change):")
    for event in detect_risk(one_reading, changed):
        sender.send(event)
    os.remove(path)
    os.rmdir(folder)
    print()

    print("=== Depot received %d alerts in total, none lost ===" % len(depot.received))


if __name__ == "__main__":
    main()
