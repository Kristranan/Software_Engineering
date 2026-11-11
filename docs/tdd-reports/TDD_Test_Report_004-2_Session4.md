# TDD Test Report

Smart Cold Box · Sprint 2 · Story 004-2 Accumulate freeze exposure · Session 4: keep the freeze total across a power cut (freeze_state.py)

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 004-2 Accumulate freeze exposure | save returns True; load gives back the same state (freeze_s 900, last_good) | TC-13 | Saved state loads back | Nutchuda D. (Sia) | 11 Nov 2026 |
| 004-2 Accumulate freeze exposure | None (no file yet, so the total starts at 0) | TC-14 | No saved state gives None | Nutchuda D. (Sia) | 11 Nov 2026 |
| 004-2 Accumulate freeze exposure | None (the saved state belongs to SHP-1000, the box is now on SHP-1001) | TC-15 | State from another shipment is not used | Nutchuda D. (Sia) | 11 Nov 2026 |
| 004-2 Accumulate freeze exposure | None for 7 bad files: cut-off JSON, not text, a list, freeze_s -5 / true / "900", last_good not a reading | TC-16 | Broken or wrong file gives None | Nutchuda D. (Sia) | 11 Nov 2026 |
| 004-2 Accumulate freeze exposure | False when the file cannot be written; no error | TC-17 | Save never raises | Nutchuda D. (Sia) | 11 Nov 2026 |
| 004-2 Accumulate freeze exposure | After 2 cold readings: freeze_s 300, and the file holds the same state | TC-18 | Each reading is saved | Nutchuda D. (Sia) | 11 Nov 2026 |

*Full test file after the last refactor (all 10 tests in exposure/test_freeze_state.py, including 4 tests for AC1 and AC2 across a power cut):* `Ran 10 tests in 0.007s OK`

*All tests in exposure/ (limits, freeze_exposure, freeze_state):* `Ran 49 tests ... OK`

## Test Case Number: TC-13

**Test Case Name:** Saved state loads back (`test_saved_state_loads_back`)

**Expected output:** save returns True; load gives back the same state (freeze_s 900, last_good)

### Red

Wrote the test first. freeze_state.py had no save_freeze_state() yet, so the test stopped with an AttributeError.

*Test written first:*

```text
def test_saved_state_loads_back(self):
    state = {"freeze_s": 900, "last_good": reading(900, 0.5)}
    self.assertTrue(fs.save_freeze_state(state, self.path))
    self.assertEqual(fs.load_freeze_state("SHP-1001", self.path), state)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_state
test_saved_state_loads_back ... ERROR

========================================
ERROR: test_saved_state_loads_back
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_state.py", line 30, in test_saved_state_loads_back
    self.assertTrue(fs.save_freeze_state(state, self.path))
AttributeError: module 'freeze_state' has no attribute 'save_freeze_state'

----------------------------------------
Ran 1 test in 0.003s

FAILED (errors=1)
```

### Green

Smallest code that passes: write the state as JSON, read it back.

*Code in freeze_state.py:*

```text
import json


def save_freeze_state(state, path):
    with open(path, "w") as f:
        json.dump(state, f)
    return True


def load_freeze_state(shipment_id, path):
    with open(path) as f:
        return json.load(f)
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_state
test_saved_state_loads_back ... ok

----------------------------------------
Ran 1 test in 0.002s

OK
```

### Yellow

Made the save safe against a power cut: write to a .tmp file first, then rename it over the old file. Binary mode, like store_readings/storage.py, so Windows never writes "\r\n". Default path freeze_state.json. The test still passes.

*Code after refactoring:*

```text
import json
import os

FREEZE_STATE_PATH = "freeze_state.json"

# MicroPython has no os.replace; its rename overwrites the target.
_replace = getattr(os, "replace", os.rename)


def save_freeze_state(state, path=FREEZE_STATE_PATH):
    """Write to a .tmp file first, then rename it over the old file."""
    tmp = path + ".tmp"
    f = open(tmp, "wb")
    try:
        f.write(json.dumps(state).encode())
    finally:
        f.close()
    _replace(tmp, path)
    return True


def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    f = open(path, "rb")
    try:
        return json.loads(f.read().decode())
    finally:
        f.close()
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_state
test_saved_state_loads_back ... ok

----------------------------------------
Ran 1 test in 0.001s

OK
```

## Test Case Number: TC-14

**Test Case Name:** No saved state gives None (`test_no_saved_state_gives_none`)

**Expected output:** None (no file yet, so the total starts at 0)

### Red

On a new box there is no file yet, and load crashed with FileNotFoundError.

*Test written first:*

```text
def test_no_saved_state_gives_none(self):
    self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path))
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_state
test_no_saved_state_gives_none ... ERROR
test_saved_state_loads_back ... ok

========================================
ERROR: test_no_saved_state_gives_none
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_state.py", line 34, in test_no_saved_state_gives_none
    self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path))
  File "freeze_state.py", line 25, in load_freeze_state
    f = open(path, "rb")
FileNotFoundError: [Errno 2] No such file or directory: '<temp folder>/freeze_state.json'

----------------------------------------
Ran 2 tests in 0.003s

FAILED (errors=1)
```

### Green

Return None when the file cannot be opened. accumulate_freeze(None, ...) already starts a new total (TC-11).

*Code in freeze_state.py:*

```text
def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    try:
        f = open(path, "rb")
        try:
            return json.loads(f.read().decode())
        finally:
            f.close()
    except OSError:
        return None
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_state
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok

----------------------------------------
Ran 2 tests in 0.002s

OK
```

### Yellow

Read the state first, then return it, so the next rules have one place to go. Added a docstring. Both tests pass.

*Code after refactoring:*

```text
def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    """Return the saved state, or None to start a new total."""
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except OSError:
        return None
    return state
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_state
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok

----------------------------------------
Ran 2 tests in 0.002s

OK
```

## Test Case Number: TC-15

**Test Case Name:** State from another shipment is not used (`test_state_from_another_shipment_is_not_used`)

**Expected output:** None (the saved state belongs to SHP-1000, the box is now on SHP-1001)

### Red

The box loaded the freeze total of the previous shipment, so a new shipment would start with 900 s of freeze it never had.

*Test written first:*

```text
def test_state_from_another_shipment_is_not_used(self):
    old = {"freeze_s": 900, "last_good": reading(900, 0.5, "SHP-1000")}
    fs.save_freeze_state(old, self.path)
    self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path))
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_state
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... FAIL

========================================
FAIL: test_state_from_another_shipment_is_not_used
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_state.py", line 39, in test_state_from_another_shipment_is_not_used
    self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path))
AssertionError: {'freeze_s': 900, 'last_good': {'device_id': 'BOX-001', 'shipment_id': 'SHP-1000', 'seq': 1, 'timestamp_s': 900, 'temp_c': 0.5, 'ok': True, 'error': None}} is not None

----------------------------------------
Ran 3 tests in 0.003s

FAILED (failures=1)
```

### Green

Return None unless last_good belongs to the same shipment.

*Code in freeze_state.py:*

```text
def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    """Return the saved state, or None to start a new total."""
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except OSError:
        return None
    last_good = state["last_good"]
    if last_good is None or last_good.get("shipment_id") != shipment_id:
        return None
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_state
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 3 tests in 0.002s

OK
```

### Yellow

Docstring says a state from another shipment is never carried over. No logic change. All 3 tests pass.

*Code after refactoring:*

```text
def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    """Return the saved state for this shipment, or None to start a new total.

    A state saved during another shipment is never carried over.
    """
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except OSError:
        return None
    last_good = state["last_good"]
    if last_good is None or last_good.get("shipment_id") != shipment_id:
        return None
    return state
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_state
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 3 tests in 0.005s

OK
```

## Test Case Number: TC-16

**Test Case Name:** Broken or wrong file gives None (`test_broken_or_wrong_file_gives_none`)

**Expected output:** None for 7 bad files: cut-off JSON, not text, a list, freeze_s -5 / true / "900", last_good not a reading

### Red

A file cut off in the middle crashed load with a JSONDecodeError.

*Test written first:*

```text
def test_broken_or_wrong_file_gives_none(self):
    good = reading(900, 0.5)
    for data in (b'{"freeze_s": 9',  # cut off in the middle
                 b"\xff\xfe",  # not text
                 b"[1, 2]",
                 json.dumps({"freeze_s": -5, "last_good": good}).encode(),
                 json.dumps({"freeze_s": True, "last_good": good}).encode(),
                 json.dumps({"freeze_s": "900", "last_good": good}).encode(),
                 json.dumps({"freeze_s": 900, "last_good": "BOX-001"}).encode()):
        self.write_raw(data)
        self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path), data)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ERROR
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

========================================
ERROR: test_broken_or_wrong_file_gives_none
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_state.py", line 51, in test_broken_or_wrong_file_gives_none
    self.assertIsNone(fs.load_freeze_state("SHP-1001", self.path), data)
  File "freeze_state.py", line 32, in load_freeze_state
    state = json.loads(f.read().decode())
  File "json/__init__.py", line 352, in loads
    return _default_decoder.decode(s)
  File "json/decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "json/decoder.py", line 361, in raw_decode
    obj, end = self.scan_once(s, idx)
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 1 column 15 (char 14)

----------------------------------------
Ran 4 tests in 0.004s

FAILED (errors=1)
```

### Green

Catch bad JSON and bad text too, and check that freeze_s is a whole number >= 0 and last_good is a reading.

*Code in freeze_state.py:*

```text
def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    """Return the saved state for this shipment, or None to start a new total.

    A state saved during another shipment is never carried over.
    """
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict):
        return None
    freeze_s = state.get("freeze_s")
    if isinstance(freeze_s, bool) or not isinstance(freeze_s, int) or freeze_s < 0:
        return None
    last_good = state.get("last_good")
    if not isinstance(last_good, dict) or last_good.get("shipment_id") != shipment_id:
        return None
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 4 tests in 0.004s

OK
```

### Yellow

Moved the checks into _is_valid_state(), and return a clean dict with only freeze_s and last_good. All 4 tests pass.

*Code after refactoring:*

```text
def _is_valid_state(state):
    """freeze_s is a whole number >= 0, and last_good is a reading or None."""
    if not isinstance(state, dict):
        return False
    freeze_s = state.get("freeze_s")
    if isinstance(freeze_s, bool) or not isinstance(freeze_s, int) or freeze_s < 0:
        return False
    last_good = state.get("last_good")
    return last_good is None or isinstance(last_good, dict)


def load_freeze_state(shipment_id, path=FREEZE_STATE_PATH):
    """Return the saved state for this shipment, or None to start a new total.

    Never raises. None when there is no file, the file is broken or not a
    freeze state, or the state was saved during another shipment.
    """
    try:
        f = open(path, "rb")
        try:
            state = json.loads(f.read().decode())
        finally:
            f.close()
    except (OSError, ValueError):  # ValueError: bad JSON or bad UTF-8, on both runtimes
        return None
    if not _is_valid_state(state):
        return None
    last_good = state["last_good"]
    if last_good is None or last_good.get("shipment_id") != shipment_id:
        return None
    return {"freeze_s": state["freeze_s"], "last_good": last_good}
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_no_saved_state_gives_none ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 4 tests in 0.004s

OK
```

## Test Case Number: TC-17

**Test Case Name:** Save never raises (`test_save_never_raises`)

**Expected output:** False when the file cannot be written; no error

### Red

Saving into a folder that does not exist crashed with FileNotFoundError. On the box, that would stop the counting.

*Test written first:*

```text
def test_save_never_raises(self):
    path = os.path.join(self.dir.name, "no_such_folder", "freeze_state.json")
    self.assertFalse(fs.save_freeze_state({"freeze_s": 0, "last_good": None}, path))
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_no_saved_state_gives_none ... ok
test_save_never_raises ... ERROR
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

========================================
ERROR: test_save_never_raises
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_state.py", line 55, in test_save_never_raises
    self.assertFalse(fs.save_freeze_state({"freeze_s": 0, "last_good": None}, path))
  File "freeze_state.py", line 26, in save_freeze_state
    f = open(tmp, "wb")
FileNotFoundError: [Errno 2] No such file or directory: '<temp folder>/no_such_folder/freeze_state.json.tmp'

----------------------------------------
Ran 5 tests in 0.005s

FAILED (errors=1)
```

### Green

Catch any error while saving and return False.

*Code in freeze_state.py:*

```text
def save_freeze_state(state, path=FREEZE_STATE_PATH):
    """Write to a .tmp file first, then rename it over the old file."""
    try:
        tmp = path + ".tmp"
        f = open(tmp, "wb")
        try:
            f.write(json.dumps(state).encode())
        finally:
            f.close()
        _replace(tmp, path)
        return True
    except Exception:
        return False
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_no_saved_state_gives_none ... ok
test_save_never_raises ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 5 tests in 0.004s

OK
```

### Yellow

Docstring says it never raises and why the .tmp file protects the old state. All 5 tests pass.

*Code after refactoring:*

```text
def save_freeze_state(state, path=FREEZE_STATE_PATH):
    """Save the state. Never raises: False means it was not saved.

    Writes to a .tmp file first, then renames it over the old file, so a power
    cut during a save leaves the old state in place.
    """
    try:
        tmp = path + ".tmp"
        f = open(tmp, "wb")
        try:
            f.write(json.dumps(state).encode())
        finally:
            f.close()
        _replace(tmp, path)
        return True
    except Exception:
        return False
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_no_saved_state_gives_none ... ok
test_save_never_raises ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 5 tests in 0.004s

OK
```

## Test Case Number: TC-18

**Test Case Name:** Each reading is saved (`test_each_reading_is_saved`)

**Expected output:** After 2 cold readings: freeze_s 300, and the file holds the same state

### Red

freeze_on_reading() did not exist yet (AttributeError).

*Test written first:*

```text
def test_each_reading_is_saved(self):
    state = fs.freeze_on_reading(None, reading(0, 0.5), LIMIT, self.path)
    state = fs.freeze_on_reading(state, reading(300, 0.5), LIMIT, self.path)
    self.assertEqual(state["freeze_s"], 300)
    self.assertEqual(fs.load_freeze_state("SHP-1001", self.path), state)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_each_reading_is_saved ... ERROR
test_no_saved_state_gives_none ... ok
test_save_never_raises ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

========================================
ERROR: test_each_reading_is_saved
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_state.py", line 58, in test_each_reading_is_saved
    state = fs.freeze_on_reading(None, reading(0, 0.5), LIMIT, self.path)
AttributeError: module 'freeze_state' has no attribute 'freeze_on_reading'

----------------------------------------
Ran 6 tests in 0.006s

FAILED (errors=1)
```

### Green

Add the reading with accumulate_freeze(), save the new state, return it.

*Code in freeze_state.py:*

```text
def freeze_on_reading(state, record, lower_limit_c, path=FREEZE_STATE_PATH):
    state = accumulate_freeze(state, record, lower_limit_c)
    save_freeze_state(state, path)
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_each_reading_is_saved ... ok
test_no_saved_state_gives_none ... ok
test_save_never_raises ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 6 tests in 0.005s

OK
```

### Yellow

Final clean-up: header comment that explains why the file exists (AC2) and why heat has its own file (AC1), and a docstring for when a save fails. This is the version in exposure/freeze_state.py. All 6 tests pass, and the full test file with all 10 tests passes.

*Code after refactoring:*

```text
# Keep the freeze total across a power cut (story 004-2). Owner: Sia.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# The freeze state {"freeze_s", "last_good"} is saved to freeze_state.json on
# the box's flash after every reading. Without it, a power cut would restart
# freeze_s at 0 and erase a freeze event (against AC2). Heat keeps its own
# file, so the two totals never share a file (AC1).
#
# The file is small and rewritten whole: written to a .tmp file first, then
# renamed over the old one (like exposure_limits.save), so a power cut during
# a save leaves the old state. Binary mode, like store_readings/storage.py, so
# Windows never writes "\r\n".

import json
import os

from freeze_exposure import accumulate_freeze

FREEZE_STATE_PATH = "freeze_state.json"

# MicroPython has no os.replace; its rename overwrites the target.
_replace = getattr(os, "replace", os.rename)

# ... _is_valid_state, save_freeze_state, load_freeze_state as before ...

def freeze_on_reading(state, record, lower_limit_c, path=FREEZE_STATE_PATH):
    """Add `record` to the freeze total, save it, and return the new state.

    If the save fails, the box keeps counting in memory and tries again at the
    next reading.
    """
    state = accumulate_freeze(state, record, lower_limit_c)
    save_freeze_state(state, path)
    return state
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_state
test_broken_or_wrong_file_gives_none ... ok
test_each_reading_is_saved ... ok
test_no_saved_state_gives_none ... ok
test_save_never_raises ... ok
test_saved_state_loads_back ... ok
test_state_from_another_shipment_is_not_used ... ok

----------------------------------------
Ran 6 tests in 0.005s

OK
```
