# Temperature limits for exposure (stories 004-1 and 004-2).
# lower_limit_c: Sia (004-2). upper_limit_c is added here by 004-1.
# Runs on ESP32 MicroPython and on desktop CPython (for tests), like
# read_temp/config.py: plain dicts, no dataclasses, no typing module.
#
# The limits live in exposure_limits.json on the box's flash, not in config.json:
#   - they change without a code change (edit/upload the file)
#   - a bad limit can never reset interval_s (config.load() falls back to
#     defaults for the whole file when one key is bad), and read_temp/config.py
#     and its tests stay as they are
#   - each key falls back to its own default, so a typo in one limit does not
#     wipe the other
#
# Defaults come from the vaccine profile (2–8 °C) in the temperature data
# format agreement from Sprint 1. They still need the Product Owner's OK.
import json
import os

LIMITS_PATH = "exposure_limits.json"

DEFAULTS = {
    # Time below this temperature counts as freeze exposure (004-2).
    # "Below" means strictly less than: 2.0 is not freeze, 1.9 is.
    "lower_limit_c": 2.0,
    # Time above this temperature counts as heat exposure (004-1).
    # "Above" means strictly greater than: 8.0 is not heat, 8.1 is.
    "upper_limit_c": 8.0,
}

# Accepted values: what the DHT22 can measure (-40 to 80 °C).
RANGES = {
    "lower_limit_c": (-40.0, 80.0),
    "upper_limit_c": (-40.0, 80.0),
}

# MicroPython has no os.replace; its rename overwrites the target.
_replace = getattr(os, "replace", os.rename)


def _check(key, value):
    """Return value as a float, or raise ValueError. Rejects bool, text, nan, inf."""
    lo, hi = RANGES[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not lo <= value <= hi:
        raise ValueError("%s must be a number in [%s, %s], got %r" % (key, lo, hi, value))
    return float(value)


def validate(limits):
    """Strict check used by save(): unknown keys and bad values raise ValueError.
    A missing key gets its default."""
    if not isinstance(limits, dict):
        raise ValueError("limits must be a JSON object")
    for key in limits:
        if key not in DEFAULTS:
            raise ValueError("unknown key %r" % (key,))
    out = {}
    for key, default in DEFAULTS.items():
        out[key] = _check(key, limits.get(key, default))
    if out["lower_limit_c"] >= out["upper_limit_c"]:
        raise ValueError("lower_limit_c must be less than upper_limit_c")
    return out


def load(path=LIMITS_PATH):
    """Never raises, so the box keeps accumulating exposure.
    A missing or broken file gives the defaults; a bad key gives that key's default only."""
    try:
        with open(path) as f:
            raw = json.load(f)
    except (OSError, ValueError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    out = {}
    for key, default in DEFAULTS.items():
        try:
            out[key] = _check(key, raw.get(key, default))
        except ValueError:
            out[key] = default
    if out["lower_limit_c"] >= out["upper_limit_c"]:
        return dict(DEFAULTS)
    return out


def save(limits, path=LIMITS_PATH):
    """Validate, then write via a temp file so a power cut never leaves a half-written file."""
    limits = validate(limits)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(limits, f)
    _replace(tmp, path)
    return limits