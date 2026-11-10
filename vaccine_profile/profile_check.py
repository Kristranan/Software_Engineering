# Load the vaccine profile and compare the exposure totals on the box (story 004-3).
# Owner: Plai. Joins profile_loader.load_profile() (Plai) and
# comparison.compare_exposure() (Shogun). Runs on ESP32 MicroPython and on
# desktop CPython (for tests), with no network: the profile is read from flash.
#
# heat_s and freeze_s are whole seconds (exposure/FREEZE_DESIGN.md section 6).
# A missing or bad profile raises ProfileError and gives no result, so the
# caller must report "unknown", never "safe".
from comparison import compare_exposure
from profile_loader import PROFILE_PATH, ProfileError, load_profile


def check_exposure(heat_s, freeze_s, path=PROFILE_PATH):
    """Return {"heat_exceeded": bool, "freeze_exceeded": bool}. Raises ProfileError."""
    return compare_exposure(heat_s, freeze_s, load_profile(path))
