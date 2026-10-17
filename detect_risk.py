# Detect low buffer or abnormal depletion rate (story 007-1, AC1 + AC2). Owner: Sia.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Only DETECTS risks; sending them to the depot is Pun's AlertSender.
# The buffer values are simulated in Sprint 1 (real calculation: story 004-4).
# Pure function: no file reading, no clock, no network.
#
# Rules: docs/decisions-and-open-questions.md (A1, A2, C1-C3).
import contracts

SECONDS_PER_HOUR = 3600


def _event(risk_type, snapshot, value):
    return {"type": risk_type,
            "device_id": snapshot["device_id"],
            "shipment_id": snapshot["shipment_id"],
            "timestamp_s": snapshot["timestamp_s"],
            "value": value}


def detect_risk(history, config):
    """Check the newest BufferSnapshot in `history` against `config`.

    Returns a list of RiskEvent dicts: [] when there is no risk,
    [LOW_BUFFER, FAST_DEPLETION] in that order when both happen (C2).
    """
    if not history:
        return []

    newest = history[-1]
    events = []

    # AC1 / A1: strictly below the threshold. Also works with one snapshot.
    if newest["remaining_buffer_pct"] < config["low_buffer_threshold_pct"]:
        events.append(_event(contracts.LOW_BUFFER, newest,
                             newest["remaining_buffer_pct"]))

    # AC2 / A2: depletion rate in %/hour against the snapshot just before.
    if len(history) >= 2:
        previous = history[-2]
        seconds = newest["timestamp_s"] - previous["timestamp_s"]
        # C3: same or out-of-order timestamps -> skip this check (no division by zero).
        if seconds > 0:
            hours = seconds / SECONDS_PER_HOUR
            rate = (previous["remaining_buffer_pct"]
                    - newest["remaining_buffer_pct"]) / hours
            if rate > config["max_depletion_pct_per_hour"]:
                events.append(_event(contracts.FAST_DEPLETION, newest, rate))

    return events
