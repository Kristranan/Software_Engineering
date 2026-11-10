# TDD Test Report

**Story:** 004-3 Compare against vaccine profile (Sprint 2)

**Task:** Load the vaccine profile from a file on the box and check it (Meeting 3)

**Code:** vaccine_profile/profile_loader.py, vaccine_profile/profile.json

**Tests:** vaccine_profile/test_profile_loader.py (Python unittest, no hardware, clock or network)

*Each test was written first and run against the loader before it had that behaviour (Red). Then only enough code was added to make it pass (Green). Then the code was checked for duplication, clarity and simplicity (Yellow). The results below are the real test outputs from 6 Nov 2026.*

| **Feature** | **Expected output** | **Test Case Number** | **Test Case Name** | **Dev** | **Test Date** |
| --- | --- | --- | --- | --- | --- |
| Load vaccine profile (004-3) | A valid profile file returns {"heat_limit_s": 7200, "freeze_limit_s": 1800} | TC01 | `test_valid_profile_returns_both_limits` | Plai | 6 Nov 2026 |
| Load vaccine profile (004-3) | No profile file: raises ProfileError (never falls back to defaults) | TC02 | `test_missing_file_raises_profile_error` | Plai | 6 Nov 2026 |
| Load vaccine profile (004-3) | Broken JSON ({heat) or a JSON list ([7200, 1800]): raises ProfileError | TC03 | `test_broken_json_or_not_an_object_raises_profile_error` | Plai | 6 Nov 2026 |
| Load vaccine profile (004-3) | Profile without heat_limit_s or without freeze_limit_s: raises ProfileError | TC04 | `test_missing_limit_raises_profile_error` | Plai | 6 Nov 2026 |
| Load vaccine profile (004-3) | A limit that is negative (-1), a decimal (7200.5), text ("7200") or true: raises ProfileError | TC05 | `test_bad_limit_value_raises_profile_error` | Plai | 6 Nov 2026 |
| Load vaccine profile (004-3) | The sample vaccine_profile/profile.json loads and has both limits | TC06 | `test_profile_file_in_repo_loads` | Plai | 6 Nov 2026 |

## Test Case Number: TC01

**Test Case Name:** test_valid_profile_returns_both_limits

### Red *(run against an empty profile_loader.py)*

```text
def test_valid_profile_returns_both_limits(self):
    self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
    self.assertEqual(loader.load_profile(self.path),
                     {"heat_limit_s": 7200, "freeze_limit_s": 1800})
```

**Result:**

```text
ERROR: test_valid_profile_returns_both_limits
AttributeError: module 'profile_loader' has no attribute 'load_profile'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
import json
 
def load_profile(path):
    with open(path) as f:
        return json.load(f)
```

Result: Ran 1 test ... OK (1/1)

### Yellow *(refactor)*

No refactor needed: three lines, no duplication. Tests re-run: OK (1/1).

## Test Case Number: TC02

**Test Case Name:** test_missing_file_raises_profile_error

### Red *(test written first, run before the code)*

```text
def test_missing_file_raises_profile_error(self):
    with self.assertRaises(loader.ProfileError):
        loader.load_profile(self.path)
```

**Result:**

```text
ERROR: test_missing_file_raises_profile_error
AttributeError: module 'profile_loader' has no attribute 'ProfileError'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
class ProfileError(Exception):
    pass
 
def load_profile(path):
    try:
        with open(path) as f:
            return json.load(f)
    except OSError:
        raise ProfileError("no profile file at %r" % (path,))
```

Result: Ran 2 tests ... OK (2/2)

### Yellow *(refactor)*

No refactor needed. Tests re-run: OK (2/2).

## Test Case Number: TC03

**Test Case Name:** test_broken_json_or_not_an_object_raises_profile_error

### Red *(test written first, run before the code)*

```text
def test_broken_json_or_not_an_object_raises_profile_error(self):
    for text in ("{heat", "[7200, 1800]"):
        with self.subTest(text=text):
            self.write_raw(text)
            with self.assertRaises(loader.ProfileError):
                loader.load_profile(self.path)
```

**Result:**

```text
ERROR: (text='{heat')
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
FAIL: (text='[7200, 1800]')
AssertionError: ProfileError not raised
FAILED (failures=1, errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
    try:
        with open(path) as f:
            profile = json.load(f)
    except OSError:
        raise ProfileError("no profile file at %r" % (path,))
    except ValueError:
        raise ProfileError("profile file is not valid JSON")
    if not isinstance(profile, dict):
        raise ProfileError("profile must be a JSON object")
    return profile
```

Result: Ran 3 tests ... OK (3/3)

### Yellow *(refactor)*

No refactor needed. Tests re-run: OK (3/3).

## Test Case Number: TC04

**Test Case Name:** test_missing_limit_raises_profile_error

### Red *(test written first, run before the code)*

```text
def test_missing_limit_raises_profile_error(self):
    for text in ('{"freeze_limit_s": 1800}', '{"heat_limit_s": 7200}'):
        with self.subTest(text=text):
            self.write_raw(text)
            with self.assertRaises(loader.ProfileError):
                loader.load_profile(self.path)
```

**Result:**

```text
FAIL: (text='{"freeze_limit_s": 1800}')
AssertionError: ProfileError not raised
FAIL: (text='{"heat_limit_s": 7200}')
AssertionError: ProfileError not raised
FAILED (failures=2)
```

### Green *(smallest code that makes the test pass)*

```text
LIMIT_KEYS = ("heat_limit_s", "freeze_limit_s")
...
    for key in LIMIT_KEYS:
        if key not in profile:
            raise ProfileError("missing %s" % (key,))
    return profile
```

Result: Ran 4 tests ... OK (4/4)

### Yellow *(refactor)*

No refactor needed: the two limit names are already one constant (LIMIT_KEYS). Tests re-run: OK (4/4).

## Test Case Number: TC05

**Test Case Name:** test_bad_limit_value_raises_profile_error

### Red *(test written first, run before the code)*

```text
def test_bad_limit_value_raises_profile_error(self):
    for value in ("-1", "7200.5", '"7200"', "true"):
        with self.subTest(value=value):
            self.write_raw('{"heat_limit_s": %s, "freeze_limit_s": 1800}' % value)
            with self.assertRaises(loader.ProfileError):
                loader.load_profile(self.path)
```

**Result:**

```text
FAIL: (value='-1')      AssertionError: ProfileError not raised
FAIL: (value='7200.5')  AssertionError: ProfileError not raised
FAIL: (value='"7200"')  AssertionError: ProfileError not raised
FAIL: (value='true')    AssertionError: ProfileError not raised
FAILED (failures=4)
```

### Green *(smallest code that makes the test pass)*

```text
        value = profile[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ProfileError("%s must be a whole number of seconds >= 0, got %r"
                               % (key, value))
```

Result: Ran 5 tests ... OK (5/5)

### Yellow *(refactor)*

No refactor needed. The bool check stays first on purpose: in Python, true is also an int. Tests re-run: OK (5/5).

## Test Case Number: TC06

**Test Case Name:** test_profile_file_in_repo_loads

### Red *(run before profile.json existed)*

```text
def test_profile_file_in_repo_loads(self):
    profile = loader.load_profile(os.path.join(HERE, "profile.json"))
    self.assertIn("heat_limit_s", profile)
    self.assertIn("freeze_limit_s", profile)
```

**Result:**

```text
ERROR: test_profile_file_in_repo_loads
FileNotFoundError: [Errno 2] No such file or directory: '...profile.json'
profile_loader.ProfileError: no profile file at '...profile.json'
FAILED (errors=1)
```

### Green *(smallest code that makes the test pass)*

```text
profile.json (test values, not product values):
{"heat_limit_s": 7200, "freeze_limit_s": 1800}
```

Result: Ran 6 tests ... OK (6/6)

### Yellow *(refactor)*

Refactor of profile_loader.py, behaviour unchanged: added the default path PROFILE_PATH = "profile.json", a docstring, and header comments that explain why a bad profile raises instead of using defaults (so the comparison reports unknown, never safe). Tests re-run: OK (6/6).
