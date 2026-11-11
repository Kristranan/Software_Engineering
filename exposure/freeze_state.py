# Keep the freeze total across a power cut (story 004-2). Owner: Sia.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# The freeze state {"freeze_s", "last_good"} is saved to freeze_state.json on
# the box's flash after every reading. Without it, a power cut would restart
# freeze_s at 0 and erase a freeze event (against AC2). Heat keeps its own
# file, so the two totals never share a file (AC1).
#
# The file is small and rewritten whole: written to a .tmp file first, then
# renamed over the old one (like exposure_limits.save), so a power cut during
# a save leaves the old state. Binary mode, like store_readings/storage.py, so
# Windows never writes "\r\n".

import json
import os

from freeze_exposure import accumulate_freeze

FREEZE_STATE_PATH = "freeze_state.json"

# MicroPython has no os.replace; its rename overwrites the target.
_replace = getattr(os, "replace", os.rename)


def _is_valid_state(state):
    """freeze_s is a whole number >= 0, and last_good is a reading or None."""
    if not isinstance(state, dict):
        return False
    freeze_s = state.get("freeze_s")
    if isinstance(freeze_s, bool) or not isinstance(freeze_s, int) or freeze_s < 0:
        return False
    last_good = state.get("last_good")
    return last_good is None or isinstance(last_good, dict)


def save_freeze_state(state, path=FREEZE_STATE_PATH):
    """Save the state. Never raises: False means it was not saved.

    Writes to a .tmp file first, then renames it over the old file, so a power
    cut during a save leaves the old state in place.
    """
    try:
        tmp = path + ".tmp"
        f = open(tmp, "wb")
        try:
            f.write(json.dumps(state).encode())
        finally:
            f.close()
        _replace(tmp, path)
        return True
    except Exception:
        return False


def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    """Return the saved state for this shipment, or None to start a new total.

    Never raises. None when there is no file, the file is broken or not a
    freeze state, or the state was saved during another shipment.
    """
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except (OSError, ValueError):  # ValueError: bad JSON or bad UTF-8, on both runtimes
        return None
    if not _is_valid_state(state):
        return None
    last_good = state["last_good"]
    if last_good is None or last_good.get("shipment_id") != shipment_id:
        return None
    return {"freeze_s": state["freeze_s"], "last_good": last_good}


def freeze_on_reading(state, record, lower_limit_c, path=FREEZE_STATE_PATH):
    """Add `record` to the freeze total, save it, and return the new state.

    If the save fails, the box keeps counting in memory and tries again at the
    next reading.
    """
    state = accumulate_freeze(state, record, lower_limit_c)
    save_freeze_state(state, path)
    return state
