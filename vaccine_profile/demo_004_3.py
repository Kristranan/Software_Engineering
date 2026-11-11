# Demo of story 004-3 "Compare against vaccine profile" for the Sprint Review. Owner: Plai.
# Desktop Python: from vaccine_profile/, run  python demo_004_3.py
#
# Uses the real team code: profile_loader (Plai), comparison (Shogun) and
# profile_check (Plai). Only the exposure totals are made up. No network is used:
# the limits come from profile.json (test values, not product values).
import os
import tempfile

from profile_check import PROFILE_PATH, ProfileError, check_exposure
from profile_loader import load_profile

HERE = os.path.dirname(os.path.abspath(__file__))


def side(exceeded):
    return "EXCEEDED" if exceeded else "within limit"


def verdict(heat_s, freeze_s, path=PROFILE_PATH):
    """One line for the audience. A bad profile shows UNKNOWN, never a safe-looking result."""
    try:
        result = check_exposure(heat_s, freeze_s, path)
    except ProfileError as e:
        return "UNKNOWN (profile error: %s)" % e
    return "heat: %s, freeze: %s" % (side(result["heat_exceeded"]), side(result["freeze_exceeded"]))


def main():
    path = os.path.join(HERE, "profile.json")
    profile = load_profile(path)
    print("Profile loaded from profile.json: heat limit %d s, freeze limit %d s"
          % (profile["heat_limit_s"], profile["freeze_limit_s"]))
    print()
    for label, heat_s, freeze_s in (
            ("1. Normal trip", 600, 0),
            ("2. Heat exactly at its limit", profile["heat_limit_s"], 0),
            ("3. Too long above 8 C", profile["heat_limit_s"] + 1, 0),
            ("4. Too long below 2 C", 0, profile["freeze_limit_s"] + 1),
            ("5. Heat over, freeze under", profile["heat_limit_s"] + 1, 60)):
        print("%-30s heat_s=%-5d freeze_s=%-5d -> %s" % (label, heat_s, freeze_s, verdict(heat_s, freeze_s, path)))

    with tempfile.TemporaryDirectory() as d:
        broken = os.path.join(d, "profile.json")
        with open(broken, "w") as f:
            f.write('{"heat_limit_s": 7200}')
        print("%-30s heat_s=%-5d freeze_s=%-5d -> %s" % ("6. Broken profile file", 0, 0, verdict(0, 0, broken)))


if __name__ == "__main__":
    main()
