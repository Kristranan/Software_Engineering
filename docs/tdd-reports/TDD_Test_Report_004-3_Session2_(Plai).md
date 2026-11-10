# TDD Test Report

**Story:** 004-3 Compare against vaccine profile (Sprint 2), Session 2

**Task:** Combine the profile loader with Shogun's comparison, and run it with no network (Meeting 4)

**Code:** vaccine_profile/profile_check.py (uses profile_loader.py by Plai and comparison.py by Shogun)

**Tests:** vaccine_profile/test_profile_check.py (Python unittest, no hardware, clock or network)

*Each test was written first and run before the code it needs (Red). Then only enough code was added to make it pass (Green). Then the code was checked for duplication, clarity and simplicity (Yellow). The results below are the real test outputs from 10 Nov 2026. Test case numbers continue from Session 1 (TC01 to TC06).*

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| Check exposure against the loaded profile (004-3) | Limits 7200 s / 1800 s from the file, heat 7201 s, freeze 1800 s: {"heat_exceeded": True, "freeze_exceeded": False} | TC07 | `test_uses_limits_from_profile_file` | Plai | 10 Nov 2026 |
| Check exposure against the loaded profile (004-3) | Called with no path on the box: reads profile.json in its own folder; heat 0 s, freeze 1801 s gives freeze_exceeded True | TC08 | `test_without_a_path_reads_profile_json_in_the_box_folder` | Plai | 10 Nov 2026 |
| Check exposure against the loaded profile (004-3) | Profile without freeze_limit_s: raises ProfileError and returns no result (never looks safe) | TC09 | `test_broken_profile_raises_profile_error_instead_of_a_result` | Plai | 10 Nov 2026 |
| Check exposure against the loaded profile (004-3) | With every socket blocked: still gives {"heat_exceeded": False, "freeze_exceeded": False} for values equal to the limits (AC3: runs entirely on the box) | TC10 | `test_runs_with_no_network` | Plai | 10 Nov 2026 |

## Test Case Number: TC07

**Test Case Name:** `test_uses_limits_from_profile_file`

### Red *(test written first, profile_check.py did not exist yet)*

```text
def test_uses_limits_from_profile_file(self):
    self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
    self.assertEqual(check.check_exposure(7201, 1800, self.path),
                     {"heat_exceeded": True, "freeze_exceeded": False})
```

**Result:**

```text
ERROR: test_profile_check
ImportError: Failed to import test module: test_profile_check
ModuleNotFoundError: No module named 'profile_check'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
from comparison import compare_exposure
from profile_loader import load_profile

def check_exposure(heat_s, freeze_s, path):
    return compare_exposure(heat_s, freeze_s, load_profile(path))
```

Result: Ran 1 test ... OK (1/1)

### Yellow *(refactor)*

No refactor needed: one line that joins the loader and the comparison. Tests re-run: OK (1/1).

## Test Case Number: TC08

**Test Case Name:** `test_without_a_path_reads_profile_json_in_the_box_folder`

### Red *(test written first, run before the code)*

```text
def test_without_a_path_reads_profile_json_in_the_box_folder(self):
    self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
    here = os.getcwd()
    os.chdir(self.dir.name)
    try:
        result = check.check_exposure(0, 1801)
    finally:
        os.chdir(here)
    self.assertEqual(result, {"heat_exceeded": False, "freeze_exceeded": True})
```

**Result:**

```text
ERROR: test_without_a_path_reads_profile_json_in_the_box_folder
TypeError: check_exposure() missing 1 required positional argument: 'path'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
from profile_loader import PROFILE_PATH, load_profile

def check_exposure(heat_s, freeze_s, path=PROFILE_PATH):
    return compare_exposure(heat_s, freeze_s, load_profile(path))
```

Result: Ran 2 tests ... OK (2/2)

### Yellow *(refactor)*

No refactor needed: the default comes from profile_loader.PROFILE_PATH, so the file name is written in one place only. Tests re-run: OK (2/2).

## Test Case Number: TC09

**Test Case Name:** `test_broken_profile_raises_profile_error_instead_of_a_result`

### Red *(test written first, run before the code)*

```text
def test_broken_profile_raises_profile_error_instead_of_a_result(self):
    self.write_raw('{"heat_limit_s": 7200}')
    with self.assertRaises(check.ProfileError):
        check.check_exposure(0, 0, self.path)
```

**Result:**

```text
ERROR: test_broken_profile_raises_profile_error_instead_of_a_result
AttributeError: module 'profile_check' has no attribute 'ProfileError'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
from profile_loader import PROFILE_PATH, ProfileError, load_profile
```

Result: Ran 3 tests ... OK (3/3)

### Yellow *(refactor)*

No refactor needed. Code that uses profile_check can now catch ProfileError from the same module. Tests re-run: OK (3/3).

## Test Case Number: TC10

**Test Case Name:** `test_runs_with_no_network`

### Red *(did not fail on its first run)*

```text
def test_runs_with_no_network(self):
    self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')

    def no_network(*args, **kwargs):
        raise OSError("network used")

    with mock.patch("socket.socket", no_network), \
            mock.patch("socket.create_connection", no_network), \
            mock.patch("socket.getaddrinfo", no_network):
        result = check.check_exposure(7200, 1800, self.path)
    self.assertEqual(result, {"heat_exceeded": False, "freeze_exceeded": False})
```

The test passed on its first run (Ran 4 tests ... OK), because the code never used the network. To show the test can still catch a network call, it was run once against a copy of profile_check.py that opens a connection (scratch copy only, not in the repo):

**Result:**

```text
    socket.create_connection(("example.com", 80))  # deliberate network call, only in this copy
ERROR: test_runs_with_no_network
OSError: network used
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

No code change needed: the real profile_check.py reads the profile from a local file only.

Result: Ran 4 tests ... OK (4/4)

### Yellow *(refactor)*

Refactor of profile_check.py, behaviour unchanged: added a header comment (owners, units, MicroPython, no network, and why a bad profile must be reported as unknown, never safe) and a docstring. Tests re-run: OK (4/4). All tests in vaccine_profile: Ran 15 tests ... OK (6 loader + 5 comparison + 4 check).
