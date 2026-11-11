# TDD Test Report

**Story:** 004-3 Compare against vaccine profile (Sprint 2), Session 3

**Task:** Test a broken profile and bad totals, and run the acceptance tests with Shogun's code (Meeting 5)

**Code:** vaccine_profile/profile_check.py, vaccine_profile/profile_loader.py (Plai); uses exposure_comparison.py and comparison.py (Shogun)

**Tests:** vaccine_profile/test_profile_check.py (TC11), vaccine_profile/test_acceptance_004_3.py (TC12, TC13). Run from the repo root: python -m unittest discover -s vaccine_profile

*Each test was written first and run before any code change (Red). Then only enough code was added to make it pass (Green). Then the code was checked for duplication, clarity and simplicity (Yellow). The results below are the real test outputs from 11 Nov 2026. Test case numbers continue from Session 2 (TC07 to TC10). The missing file, missing limit and bad limit cases are already covered by TC02 to TC05 and TC09, and the offline case by TC10. TC12 and TC13 are acceptance tests for code that was already built, so they passed on their first run; each was also run once against a broken copy of the code to show it can fail.*

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| Check exposure against the loaded profile (004-3) | heat_s or freeze_s that is negative (-1), None, text ("60"), True or a decimal (60.5): raises ValueError and gives no result | TC11 | `test_bad_exposure_total_raises_value_error_instead_of_a_result` | Plai | 11 Nov 2026 |
| Check exposure against the loaded profile (004-3) | Trip with heat_s = 120 and freeze_s = 120, limits 119 s / 120 s read from the file: {"heat_exceeded": True, "freeze_exceeded": False} (AC1, AC2) | TC12 | `test_trip_is_compared_with_limits_loaded_from_the_profile_file` | Plai | 11 Nov 2026 |
| Check exposure against the loaded profile (004-3) | The same trip with every socket blocked: same result, no network used (AC3) | TC13 | `test_whole_trip_runs_with_no_network` | Plai | 11 Nov 2026 |

## Test Case Number: TC11

**Test Case Name:** `test_bad_exposure_total_raises_value_error_instead_of_a_result`

### Red *(test written first, run before the code)*

```text
def test_bad_exposure_total_raises_value_error_instead_of_a_result(self):
    self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
    for heat_s, freeze_s in ((-1, 0), (0, -1), (None, 0), (0, None),
                             ("60", 0), (True, 0), (60.5, 0)):
        with self.subTest(heat_s=heat_s, freeze_s=freeze_s):
            with self.assertRaises(ValueError):
                check.check_exposure(heat_s, freeze_s, self.path)
```

Four bad totals gave a result as if nothing was wrong (-1, True and 60.5 are numbers to Python), and three crashed with a TypeError inside the comparison:

**Result:**

```text
ERROR: (heat_s=None, freeze_s=0)   TypeError: '>' not supported between instances of 'NoneType' and 'int'
ERROR: (heat_s=0, freeze_s=None)   TypeError: '>' not supported between instances of 'NoneType' and 'int'
ERROR: (heat_s='60', freeze_s=0)   TypeError: '>' not supported between instances of 'str' and 'int'
FAIL: (heat_s=-1, freeze_s=0)      AssertionError: ValueError not raised
FAIL: (heat_s=0, freeze_s=-1)      AssertionError: ValueError not raised
FAIL: (heat_s=True, freeze_s=0)    AssertionError: ValueError not raised
FAIL: (heat_s=60.5, freeze_s=0)    AssertionError: ValueError not raised
FAILED (failures=4, errors=3)
```

### Green *(smallest code that makes the test pass)*

```text
def check_exposure(heat_s, freeze_s, path=PROFILE_PATH):
    for name, value in (("heat_s", heat_s), ("freeze_s", freeze_s)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("%s must be a whole number of seconds >= 0, got %r" % (name, value))
    return compare_exposure(heat_s, freeze_s, load_profile(path))
```

Result: Ran 5 tests ... OK (5/5 in test_profile_check)

### Yellow *(refactor)*

Refactor, behaviour unchanged: the same "whole seconds >= 0" check was now written twice (profile_loader.py for the limits, profile_check.py for the totals). Moved it into one function, profile_loader.is_whole_seconds(value), and both files use it. Tests re-run: all 19 tests in vaccine_profile OK.

## Test Case Number: TC12

**Test Case Name:** `test_trip_is_compared_with_limits_loaded_from_the_profile_file`

### Red *(acceptance test, passed on its first run)*

```text
# R1: the time between two good readings is counted by the earlier one.
#   0 -> 120 s at 9.0 C: heat_s = 120     120 -> 240 s at 1.0 C: freeze_s = 120
TRIP = [reading(0, 9.0), reading(60, 9.0), reading(120, 1.0), reading(180, 1.0), reading(240, 4.0)]

def run_trip(self):
    profile = load_profile(self.path)
    state = None
    for record in TRIP:
        state, _ = update_and_compare(state, record, profile, UPPER_C, LOWER_C)
    return check.check_exposure(state["heat_s"], state["freeze_s"], self.path)

def test_trip_is_compared_with_limits_loaded_from_the_profile_file(self):
    self.assertEqual(self.run_trip(), {"heat_exceeded": True, "freeze_exceeded": False})
```

The test passed on its first run (Ran 2 tests ... OK), because the loader, Shogun's update_and_compare() and check_exposure() already work together. To show it can fail, it was run once against a copy of profile_check.py that ignores the file and uses fixed limits (scratch copy only, not in the repo):

**Result:**

```text
return compare_exposure(heat_s, freeze_s, {"heat_limit_s": 7200, "freeze_limit_s": 1800})  # mutant
FAIL: test_trip_is_compared_with_limits_loaded_from_the_profile_file
AssertionError: {'heat_exceeded': False, 'freeze_exceeded': False} != {'heat_exceeded': True, 'freeze_exceeded': False}
FAILED (failures=2)
```

### Green *(smallest code that makes the test pass)*

No code change needed.

Result: Ran 2 tests ... OK (2/2 in test_acceptance_004_3)

### Yellow *(refactor)*

No refactor needed. Heat and freeze come out different (True / False) from totals of the same size, which shows each is compared against its own limit (AC2).

## Test Case Number: TC13

**Test Case Name:** `test_whole_trip_runs_with_no_network`

### Red *(acceptance test, passed on its first run)*

```text
def test_whole_trip_runs_with_no_network(self):
    def no_network(*args, **kwargs):
        raise OSError("network used")

    with mock.patch("socket.socket", no_network), \
            mock.patch("socket.create_connection", no_network), \
            mock.patch("socket.getaddrinfo", no_network):
        result = self.run_trip()
    self.assertEqual(result, {"heat_exceeded": True, "freeze_exceeded": False})
```

The test passed on its first run, because no part of the flow uses the network. To show it can fail, it was run once against a copy of profile_check.py that opens a connection (scratch copy only, not in the repo):

**Result:**

```text
socket.create_connection(("example.com", 80))  # mutant: uses the network
ERROR: test_whole_trip_runs_with_no_network
OSError: network used
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

No code change needed.

Result: Ran 2 tests ... OK (2/2 in test_acceptance_004_3). All tests in vaccine_profile: Ran 21 tests ... OK

### Yellow *(refactor)*

No refactor needed.
