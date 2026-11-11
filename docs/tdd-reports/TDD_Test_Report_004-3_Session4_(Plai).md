# TDD Test Report

**Story:** 004-3 Compare against vaccine profile (Sprint 2), Session 4

**Task:** Final checks and the demo for the Sprint Review (Meeting 6)

**Code:** vaccine_profile/demo_004_3.py (Plai); uses profile_check.py, profile_loader.py and Shogun's comparison.py

**Tests:** vaccine_profile/test_demo_004_3.py. Run from the repo root: python -m unittest discover -s vaccine_profile

*Each test was written first and run before the code (Red). Then only enough code was added to make it pass (Green). Then the code was checked for duplication, clarity and simplicity (Yellow). The results below are the real test outputs from 11 Nov 2026. Test case numbers continue from Session 3 (TC11 to TC13).*

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| Demo of 004-3 for the Sprint Review | Limits 119 s / 120 s, heat 120 s, freeze 120 s: "heat: EXCEEDED, freeze: within limit" | TC14 | `test_verdict_names_each_side_with_its_own_result` | Plai | 11 Nov 2026 |
| Demo of 004-3 for the Sprint Review | Profile without freeze_limit_s: the text starts with UNKNOWN and never says "within limit" | TC15 | `test_broken_profile_shows_unknown_never_safe` | Plai | 11 Nov 2026 |

## Test Case Number: TC14

**Test Case Name:** `test_verdict_names_each_side_with_its_own_result`

### Red *(test written first, demo_004_3.py did not exist yet)*

```text
def test_verdict_names_each_side_with_its_own_result(self):
    self.write_raw('{"heat_limit_s": 119, "freeze_limit_s": 120}')
    self.assertEqual(demo.verdict(120, 120, self.path),
                     "heat: EXCEEDED, freeze: within limit")
```

**Result:**

```text
ERROR: test_demo_004_3
ImportError: Failed to import test module: test_demo_004_3
ModuleNotFoundError: No module named 'demo_004_3'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
from profile_check import check_exposure

def verdict(heat_s, freeze_s, path):
    result = check_exposure(heat_s, freeze_s, path)
    side = lambda exceeded: "EXCEEDED" if exceeded else "within limit"
    return "heat: %s, freeze: %s" % (side(result["heat_exceeded"]), side(result["freeze_exceeded"]))
```

Result: Ran 1 test ... OK (1/1)

### Yellow *(refactor)*

No refactor yet: the lambda is cleaned up after TC15.

## Test Case Number: TC15

**Test Case Name:** `test_broken_profile_shows_unknown_never_safe`

### Red *(test written first, run before the code)*

```text
def test_broken_profile_shows_unknown_never_safe(self):
    self.write_raw('{"heat_limit_s": 119}')
    text = demo.verdict(0, 0, self.path)
    self.assertTrue(text.startswith("UNKNOWN"), text)
    self.assertNotIn("within limit", text)
```

The demo crashed instead of showing UNKNOWN:

**Result:**

```text
ERROR: test_broken_profile_shows_unknown_never_safe
profile_loader.ProfileError: missing freeze_limit_s
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
from profile_check import ProfileError, check_exposure

def verdict(heat_s, freeze_s, path):
    try:
        result = check_exposure(heat_s, freeze_s, path)
    except ProfileError as e:
        return "UNKNOWN (profile error: %s)" % e
    ...
```

Result: Ran 2 tests ... OK (2/2)

### Yellow *(refactor)*

Refactor, behaviour unchanged: the lambda became a named function side(exceeded); verdict() got the default path PROFILE_PATH and a docstring; added a header comment and main(), which prints six cases for the Sprint Review using the real profile.json. Tests re-run: OK (2/2). All tests in vaccine_profile: Ran 23 tests ... OK.

## Demo output (python demo_004_3.py, from vaccine_profile/)

```text
Profile loaded from profile.json: heat limit 7200 s, freeze limit 1800 s

1. Normal trip                 heat_s=600   freeze_s=0     -> heat: within limit, freeze: within limit
2. Heat exactly at its limit   heat_s=7200  freeze_s=0     -> heat: within limit, freeze: within limit
3. Too long above 8 C          heat_s=7201  freeze_s=0     -> heat: EXCEEDED, freeze: within limit
4. Too long below 2 C          heat_s=0     freeze_s=1801  -> heat: within limit, freeze: EXCEEDED
5. Heat over, freeze under     heat_s=7201  freeze_s=60    -> heat: EXCEEDED, freeze: within limit
6. Broken profile file         heat_s=0     freeze_s=0     -> UNKNOWN (profile error: missing freeze_limit_s)
```

## Final check against the Definition of Done (11 Nov 2026)

| Definition of Done | Status |
| --- | --- |
| Code is merged | Plai's code is committed; it is merged once it is pushed to main |
| Unit tests pass | Yes: 23 of 23 tests in vaccine_profile pass (Plai 15, Shogun 8; 2 of Plai's are acceptance tests) |
| Acceptance Criteria pass | AC1 (loaded profile): TC12. AC2 (heat and freeze each against its own limit): TC12, plus Shogun's tests. AC3 (runs on the box): TC10, TC13 on desktop Python; not yet checked on the ESP32 in Wokwi |
| No critical defects remain | None found. Open with Shogun: exposure_comparison.py imports exposure.heat_exposure..., which works from the repo root but must be checked on MicroPython (the folders have no __init__.py) |
| The Product Owner accepts the Story | Not yet: to ask at the Sprint Review on 14 Nov 2026 |
