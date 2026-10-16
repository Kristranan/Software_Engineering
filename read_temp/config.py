# Interval setting + config storage (story 003-1).
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# The config lives in a JSON file on the box's flash, so it survives power loss
# and can be changed without a code change (edit/upload config.json).
import json
import os

CONFIG_PATH = "config.json"

DEFAULTS = {"interval_s": 300}
LIMITS = {"interval_s": (10, 3600)}

# MicroPython has no os.replace; its rename overwrites the target.
_replace = getattr(os, "replace", os.rename)


def validate(cfg):
    if not isinstance(cfg, dict):
        raise ValueError("config must be a JSON object")
    out = {}
    for key, default in DEFAULTS.items():
        value = cfg.get(key, default)
        lo, hi = LIMITS[key]
        if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
            raise ValueError("%s must be an int in [%d, %d], got %r" % (key, lo, hi, value))
        out[key] = value
    return out


def load(path=CONFIG_PATH):
    """Never raises: a missing or bad file falls back to defaults so the box keeps reading."""
    try:
        with open(path) as f:
            return validate(json.load(f))
    except (OSError, ValueError):
        return dict(DEFAULTS)


def save(cfg, path=CONFIG_PATH):
    """Validate, then write via a temp file so a power cut never leaves a half-written config."""
    cfg = validate(cfg)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cfg, f)
    _replace(tmp, path)
    return cfg
