# exposure/heat_exposure/heat_state.py
import json
import os
from heat_exposure import accumulate_heat

HEAT_STATE_PATH = "heat_state.json"
_replace = getattr(os, "replace", os.rename)

def _is_valid_state(state):
    if not isinstance(state, dict):
        return False
    heat_s = state.get("heat_s")
    if isinstance(heat_s, bool) or not isinstance(heat_s, int) or heat_s < 0:
        return False
    last_good = state.get("last_good")
    return last_good is None or isinstance(last_good, dict)

def save_heat_state(state, path=HEAT_STATE_PATH):
    """Save the state safely using .tmp pattern against power cuts."""
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

def load_heat_state(shipment_id, path=HEAT_STATE_PATH):
    """Return saved state for this shipment, or None to start a new total."""
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except (OSError, ValueError):
        return None
    if not _is_valid_state(state):
        return None
    last_good = state["last_good"]
    if last_good is None or last_good.get("shipment_id") != shipment_id:
        return None
    return {"heat_s": state["heat_s"], "last_good": last_good}

def heat_on_reading(state, record, upper_limit_c, path=HEAT_STATE_PATH):
    """Add record to heat total, save it, and return the new state."""
    state = accumulate_heat(state, record, upper_limit_c)
    save_heat_state(state, path)
    return state