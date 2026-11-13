# Demo of story 004-2 "Accumulate freeze exposure" for the Sprint Review. Owner: Sia.
# Desktop Python: from exposure/, run  python demo_004_2.py
#
# Uses the real team code: exposure_limits (Sia, Aleef), freeze_exposure and
# freeze_state (Sia), heat_increment_s (Aleef, 004-1). Only the readings are
# made up. The freeze total is saved in a temporary folder, so the demo leaves
# no files behind.
import os
import tempfile

from exposure_limits import load as load_limits
from freeze_exposure import freeze_increment_s, is_good_reading
from freeze_state import freeze_on_reading, load_freeze_state
from heat_exposure.heat_exposure import heat_increment_s

HERE = os.path.dirname(os.path.abspath(__file__))
SHIPMENT = "SHP-DEMO"


def reading(ts, temp_c):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": temp_c, "ok": True, "error": None}


def failed(ts):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": None, "ok": False, "error": "sensor_timeout"}


# One reading every 5 minutes: in range, cold, a failed read, back in range,
# too warm, back in range.
TRIP = [reading(0, 4.0), reading(300, 1.5), reading(600, 0.5), failed(900),
        reading(1200, 3.0), reading(1500, 9.0), reading(1800, 4.0)]


def label(last_good, record, limits):
    """What the time since the last good reading counted as, in words."""
    if not is_good_reading(record):
        return "failed read: counted at the next good reading"
    if last_good is None:
        return "first reading"
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    freeze = freeze_increment_s(last_good, record, limits["lower_limit_c"])
    heat = heat_increment_s(last_good, record, limits["upper_limit_c"])
    if freeze:
        return "%d s below %.1f C: freeze +%d s" % (gap_s, limits["lower_limit_c"], freeze)
    if heat:
        return "%d s above %.1f C: heat +%d s, freeze +0" % (gap_s, limits["upper_limit_c"], heat)
    return "%d s in range: +0" % gap_s


def run_trip(records, limits, path, power_cut_after=None):
    """Feed the readings through the real freeze code. One row per reading.

    power_cut_after=n: after the n-th reading, everything in memory is dropped
    and the state is loaded back from the file, as after a real power cut.
    """
    rows = []
    state = None
    for count, record in enumerate(records, 1):
        text = label(state["last_good"] if state else None, record, limits)
        state = freeze_on_reading(state, record, limits["lower_limit_c"], path)
        rows.append({"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
                     "label": text, "freeze_s": state["freeze_s"]})
        if count == power_cut_after:
            state = load_freeze_state(SHIPMENT, path)
            rows.append({"timestamp_s": None, "temp_c": None,
                         "label": "POWER CUT: restart, loaded from freeze_state.json",
                         "freeze_s": state["freeze_s"]})
    return rows


def main():
    limits = load_limits(os.path.join(HERE, "exposure_limits.json"))
    print("Limits from exposure_limits.json: lower %.1f C, upper %.1f C"
          % (limits["lower_limit_c"], limits["upper_limit_c"]))
    print()
    with tempfile.TemporaryDirectory() as folder:  # the demo leaves no files behind
        rows = run_trip(TRIP, limits, os.path.join(folder, "freeze_state.json"), power_cut_after=4)
    print("%-7s %-7s %-50s %s" % ("time", "temp", "time since the last good reading", "freeze_s"))
    for row in rows:
        time = "" if row["timestamp_s"] is None else "%d s" % row["timestamp_s"]
        if row["timestamp_s"] is None:
            temp = ""
        elif row["temp_c"] is None:
            temp = "failed"
        else:
            temp = "%.1f C" % row["temp_c"]
        print("%-7s %-7s %-50s %d" % (time, temp, row["label"], row["freeze_s"]))
    totals = [row["freeze_s"] for row in rows]
    print()
    print("freeze_s never went down:", all(a <= b for a, b in zip(totals, totals[1:])))


if __name__ == "__main__":
    main()
