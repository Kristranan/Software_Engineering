# Read, store and evaluate temperature exposure on the configured interval.
# Runs on ESP32 MicroPython in Wokwi. See DEPLOYMENT.md for board files.
#
# The driver is read(): it returns °C or raises when the sensor fails. The
# Scheduler adds device_id, shipment_id, seq and timestamp_s, waits interval_s
# from config.json, and emits a failed read as a record too (ok=false).
import json

from machine import Pin
from dht import DHT22

from scheduler import Scheduler
from storage import append_reading
from exposure_limits import load as load_limits
from freeze_state import load_freeze_state, freeze_on_reading
from heat_state import load_heat_state, heat_on_reading
from profile_check import ProfileError, check_exposure


def unknown_result(reason):
    """No valid comparison is available; neither exposure flag is a safe result."""
    return {"status": "unknown", "reason": reason,
            "heat_exceeded": None, "freeze_exceeded": None}


# Sprint 1 uses fixed test values (see the temperature data format agreement, item 9).
DEVICE_ID = "BOX-001"
SHIPMENT_ID = "SHP-1001"

limits = load_limits()
freeze = load_freeze_state(SHIPMENT_ID)
heat = load_heat_state(SHIPMENT_ID)
comparison_result = unknown_result("no readings yet")

dht = DHT22(Pin(4))


def read():
    """Return the temperature in °C. Raises OSError when the sensor fails."""
    dht.measure()
    return dht.temperature()


def emit(record):
    """Log, store, accumulate separate totals, and compare against the profile."""
    global freeze, heat, comparison_result
    print(json.dumps(record))
    append_reading(record)
    freeze = freeze_on_reading(freeze, record, limits["lower_limit_c"])
    heat = heat_on_reading(heat, record, limits["upper_limit_c"])
    if record.get("ok") is not True:
        comparison_result = unknown_result("sensor reading failed")
        return
    try:
        result = check_exposure(heat["heat_s"], freeze["freeze_s"])
        comparison_result = {
            "status": "compared",
            "heat_exceeded": result["heat_exceeded"],
            "freeze_exceeded": result["freeze_exceeded"],
        }
    except (ProfileError, ValueError) as error:
        comparison_result = unknown_result(str(error))


def main():
    Scheduler(read, emit, DEVICE_ID, SHIPMENT_ID).run()


if __name__ == "__main__":
    main()
