# Shared contracts for story 007-1 "Alert depot on risk".
#
# Agreed between Sia (detection), Pun (sending) and Gramma (tests).
# Do not rename or change anything here without telling all three:
# their code and tests depend on these names.
#
# Runs on ESP32 MicroPython and on desktop CPython (for tests), like
# read_temp/config.py. So: plain dicts and constants only — no dataclasses,
# no typing module.

# ---------------------------------------------------------------- risk types
LOW_BUFFER = "LOW_BUFFER"            # AC1 (Sia)
FAST_DEPLETION = "FAST_DEPLETION"    # AC2 (Sia)
RED_AT_HANDOFF = "RED_AT_HANDOFF"    # AC3 (Pun)
RISK_TYPES = (LOW_BUFFER, FAST_DEPLETION, RED_AT_HANDOFF)

# ------------------------------------------------ box status at the clinic
GREEN = "GREEN"
RED = "RED"

# ---------------------------------------------------------------- data shapes
# Every record is a plain dict with exactly these keys.
#
# timestamp_s: whole seconds, as returned by time.time() on the box.
#              Tests use made-up values; one hour = 3600 seconds.

# One simulated reading of the remaining thermal buffer.
# Simulated in Sprint 1; the real value comes from story 004-4 (Sprint 3).
#   {"device_id": "BOX-001", "shipment_id": "SHP-1001",
#    "timestamp_s": 0, "remaining_buffer_pct": 40.0}       # 0–100
BUFFER_SNAPSHOT_KEYS = ("device_id", "shipment_id", "timestamp_s",
                        "remaining_buffer_pct")

# The box status when it arrives at the clinic.
#   {"device_id": "BOX-001", "shipment_id": "SHP-1001",
#    "timestamp_s": 7200, "status": RED}
HANDOFF_EVENT_KEYS = ("device_id", "shipment_id", "timestamp_s", "status")

# Alert thresholds, loaded from a JSON file — never hardcoded (AC4).
#   {"low_buffer_threshold_pct": 30, "max_depletion_pct_per_hour": 5}
ALERT_CONFIG_KEYS = ("low_buffer_threshold_pct", "max_depletion_pct_per_hour")

# A detected risk that must reach the depot.
# timestamp_s is the time of the reading or handoff, not of delivery.
# "value" is optional (see docs/decisions-and-open-questions.md).
#   {"type": LOW_BUFFER, "device_id": "BOX-001", "shipment_id": "SHP-1001",
#    "timestamp_s": 21600, "value": 28.0}
RISK_EVENT_KEYS = ("type", "device_id", "shipment_id", "timestamp_s")

# ---------------------------------------------------------------- interfaces
# Python uses duck typing: any object with these methods works.
#
# Network — the box's connection. Simulated in the mockup.
#     is_online() -> bool
#
# DepotInbox — anything that receives alerts on the depot side.
#     receive(event) -> None        # event is a RiskEvent dict
