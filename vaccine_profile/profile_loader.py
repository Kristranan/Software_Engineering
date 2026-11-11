# Load the vaccine profile from the box's flash (story 004-3). Owner: Plai.
# Runs on ESP32 MicroPython and on desktop CPython (for tests), like
# exposure/exposure_limits.py: plain dicts, no dataclasses, no typing module.
#
# The profile lives in profile.json, so the limits change without a code change
# and are read on the box with no network. Limits are whole seconds, the same
# unit as heat_s and freeze_s (agreed with Sia, exposure/FREEZE_DESIGN.md
# section 6). The values in profile.json are test values, not product values.
#
# Unlike exposure_limits.load(), a missing or bad profile is never replaced by
# defaults: a default could call the shipment safe against the wrong vaccine's
# limits. load_profile() raises ProfileError, and the comparison must then
# report "unknown", never "safe".
import json

PROFILE_PATH = "profile.json"

# Heat and freeze each have their own limit; they are never added together.
LIMIT_KEYS = ("heat_limit_s", "freeze_limit_s")


class ProfileError(Exception):
    pass


def is_whole_seconds(value):
    """True for an int >= 0. bool is rejected: in Python, True is also an int."""
    return not isinstance(value, bool) and isinstance(value, int) and value >= 0


def load_profile(path=PROFILE_PATH):
    """Return the profile dict with both limits as ints. Raises ProfileError."""
    try:
        with open(path) as f:
            profile = json.load(f)
    except OSError:
        raise ProfileError("no profile file at %r" % (path,))
    except ValueError:
        raise ProfileError("profile file is not valid JSON")
    if not isinstance(profile, dict):
        raise ProfileError("profile must be a JSON object")
    for key in LIMIT_KEYS:
        if key not in profile:
            raise ProfileError("missing %s" % (key,))
        value = profile[key]
        if not is_whole_seconds(value):
            raise ProfileError("%s must be a whole number of seconds >= 0, got %r" % (key, value))
    return profile
