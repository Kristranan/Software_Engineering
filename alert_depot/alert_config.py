# Alert thresholds as configurable settings (story 007-1, AC4). Owner: Sia.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# The thresholds come only from the JSON file, never from code (AC4), so they
# change without a code change. 30 % and 5 %/hour are Sprint 1 test values (A4).
#
# A missing or bad file raises ValueError naming the file and the bad field,
# instead of silently falling back to values hidden in code.
# (Open question 4 in docs/decisions-and-open-questions.md.)
import json

import contracts

ALERT_CONFIG_PATH = "alert_thresholds.json"


def _is_finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return value - value == 0  # False for inf and nan


def load_alert_config(path=ALERT_CONFIG_PATH):
    """Read the alert thresholds file and return an AlertConfig dict."""
    try:
        with open(path) as f:
            raw = json.load(f)
    except OSError as e:
        raise ValueError("%s: cannot read file (%s)" % (path, e))
    except ValueError as e:
        raise ValueError("%s: not valid JSON (%s)" % (path, e))

    if not isinstance(raw, dict):
        raise ValueError("%s: must be a JSON object" % path)

    config = {}
    for key in contracts.ALERT_CONFIG_KEYS:
        if key not in raw:
            raise ValueError("%s: missing field %s" % (path, key))
        if not _is_finite_number(raw[key]):
            raise ValueError("%s: field %s must be a finite number, got %r"
                             % (path, key, raw[key]))
        config[key] = raw[key]
    return config
