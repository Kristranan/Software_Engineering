# TDD Test Report

Smart Cold Box · Sprint 2 · Story 004-2 Accumulate freeze exposure · Session 3: accumulate_freeze()

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 004-2 Accumulate freeze exposure | {freeze_s: 0, last_good: None} | TC-07 | New state starts at zero | Nutchuda D. (Sia) | 9 Nov 2026 |
| 004-2 Accumulate freeze exposure | freeze_s stays 0; last_good = the first reading | TC-08 | First reading is remembered and adds nothing | Nutchuda D. (Sia) | 9 Nov 2026 |
| 004-2 Accumulate freeze exposure | freeze_s goes from 600 to 900 s (1.5 °C at 300 s, next reading at 600 s) | TC-09 | Total grows by the freeze time | Nutchuda D. (Sia) | 9 Nov 2026 |
| 004-2 Accumulate freeze exposure | freeze_s stays 0; last_good stays the 0.5 °C reading | TC-10 | Failed read keeps the last good reading | Nutchuda D. (Sia) | 9 Nov 2026 |
| 004-2 Accumulate freeze exposure | Same as a new state: freeze_s 0, last_good = the reading | TC-11 | Missing state starts a new total | Nutchuda D. (Sia) | 9 Nov 2026 |
| 004-2 Accumulate freeze exposure | Old state still freeze_s 0; new state freeze_s 300 | TC-12 | Old state is not changed | Nutchuda D. (Sia) | 9 Nov 2026 |

*Full test file after the last refactor (all 27 tests in exposure/test_freeze_exposure.py):* `Ran 27 tests in 0.002s OK`

## Test Case Number: TC-07

**Test Case Name:** New state starts at zero (`test_new_state_starts_at_zero`)

**Expected output:** {freeze_s: 0, last_good: None}

### Red

Wrote the test first. new_freeze_state() did not exist yet, so the test stopped with an AttributeError.

*Test written first:*

```text
def test_new_state_starts_at_zero(self):
    self.assertEqual(fx.new_freeze_state(), {"freeze_s": 0, "last_good": None})
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_new_state_starts_at_zero ... ERROR
 
========================================
ERROR: test_new_state_starts_at_zero
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 20, in test_new_state_starts_at_zero
    self.assertEqual(fx.new_freeze_state(), {"freeze_s": 0, "last_good": None})
AttributeError: module 'freeze_exposure' has no attribute 'new_freeze_state'
 
----------------------------------------
Ran 1 test in 0.002s
 
FAILED (errors=1)
```

### Green

Smallest code that passes: return a dict with freeze_s = 0 and no reading yet.

*Code in freeze_exposure.py:*

```text
def new_freeze_state():
    return {"freeze_s": 0, "last_good": None}
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_new_state_starts_at_zero ... ok
 
----------------------------------------
Ran 1 test in 0.000s
 
OK
```

### Yellow

Added a docstring that says what the start state means (start of a shipment). No logic change; the test still passes.

*Code after refactoring:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_new_state_starts_at_zero ... ok
 
----------------------------------------
Ran 1 test in 0.000s
 
OK
```

## Test Case Number: TC-08

**Test Case Name:** First reading is remembered and adds nothing (`test_first_reading_is_remembered_and_adds_nothing`)

**Expected output:** freeze_s stays 0; last_good = the first reading

### Red

accumulate_freeze() did not exist yet, so the test stopped with an AttributeError.

*Test written first:*

```text
def test_first_reading_is_remembered_and_adds_nothing(self):
    r0 = reading(0, 0.5)
    state = fx.accumulate_freeze(fx.new_freeze_state(), r0, LIMIT)
    self.assertEqual(state, {"freeze_s": 0, "last_good": r0})
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_is_remembered_and_adds_nothing ... ERROR
test_new_state_starts_at_zero ... ok
 
========================================
ERROR: test_first_reading_is_remembered_and_adds_nothing
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 24, in test_first_reading_is_remembered_and_adds_nothing
    state = fx.accumulate_freeze(fx.new_freeze_state(), r0, LIMIT)
AttributeError: module 'freeze_exposure' has no attribute 'accumulate_freeze'
 
----------------------------------------
Ran 2 tests in 0.001s
 
FAILED (errors=1)
```

### Green

Smallest code that passes: store the reading as last_good and return the state.

*Code in freeze_exposure.py:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    state["last_good"] = record
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
 
----------------------------------------
Ran 2 tests in 0.000s
 
OK
```

### Yellow

No code change. The total is still not added here on purpose: the next test asks for it. Both tests pass.

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
 
----------------------------------------
Ran 2 tests in 0.000s
 
OK
```

## Test Case Number: TC-09

**Test Case Name:** Total grows by the freeze time (`test_total_grows_by_the_freeze_time`)

**Expected output:** freeze_s goes from 600 to 900 s (1.5 °C at 300 s, next reading at 600 s)

### Red

The function only remembered the reading, so the total stayed at 600 instead of 900.

*Test written first:*

```text
def test_total_grows_by_the_freeze_time(self):
    state = {"freeze_s": 600, "last_good": reading(300, 1.5)}
    state = fx.accumulate_freeze(state, reading(600, 0.5), LIMIT)
    self.assertEqual(state["freeze_s"], 900)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... FAIL
 
========================================
FAIL: test_total_grows_by_the_freeze_time
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 30, in test_total_grows_by_the_freeze_time
    self.assertEqual(state["freeze_s"], 900)
AssertionError: 600 != 900
 
----------------------------------------
Ran 3 tests in 0.001s
 
FAILED (failures=1)
```

### Green

Add freeze_increment_s() (from session 2) to freeze_s before remembering the new reading.

*Code in freeze_exposure.py:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
    state["last_good"] = record
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 3 tests in 0.000s
 
OK
```

### Yellow

Added a docstring. The total can only change by adding freeze_increment_s(), which is never negative, so it can never go down (AC2). All 3 tests pass.

*Code after refactoring:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Add the freeze time for `record` to the total, then remember `record`."""
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
    state["last_good"] = record
    return state
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 3 tests in 0.000s
 
OK
```

## Test Case Number: TC-10

**Test Case Name:** Failed read keeps the last good reading (`test_failed_read_keeps_the_last_good_reading`)

**Expected output:** freeze_s stays 0; last_good stays the 0.5 °C reading

### Red

The failed read replaced last_good. The gap after it would then be measured from a reading with no temperature, so freeze time would be lost.

*Test written first:*

```text
def test_failed_read_keeps_the_last_good_reading(self):
    cold = reading(0, 0.5)
    state = fx.accumulate_freeze({"freeze_s": 0, "last_good": cold}, failed(300), LIMIT)
    self.assertEqual(state, {"freeze_s": 0, "last_good": cold})
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... FAIL
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
========================================
FAIL: test_failed_read_keeps_the_last_good_reading
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 35, in test_failed_read_keeps_the_last_good_reading
    self.assertEqual(state, {"freeze_s": 0, "last_good": cold})
AssertionError: {'fre[96 chars]_s': 300, 'temp_c': None, 'ok': False, 'error'[15 chars]ut'}} != {'fre[96 chars]_s': 0, 'temp_c': 0.5, 'ok': True, 'error': None}}
  {'freeze_s': 0,
   'last_good': {'device_id': 'BOX-001',
-                'error': 'sensor_timeout',
+                'error': None,
-                'ok': False,
?                      ^^^^
 
+                'ok': True,
?                      ^^^
 
                 'seq': 1,
                 'shipment_id': 'SHP-1001',
-                'temp_c': None,
?                          ^^^^
 
+                'temp_c': 0.5,
?                          ^^^
 
-                'timestamp_s': 300}}
?                               --
 
+                'timestamp_s': 0}}
 
----------------------------------------
Ran 4 tests in 0.003s
 
FAILED (failures=1)
```

### Green

Only a good reading becomes last_good (uses is_good_reading() from session 2).

*Code in freeze_exposure.py:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Add the freeze time for `record` to the total, then remember `record`."""
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 4 tests in 0.000s
 
OK
```

### Yellow

Rewrote the docstring to explain why: after a failed read, the gap is counted when the next good reading arrives. All 4 tests pass.

*Code after refactoring:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Add the freeze time for `record` to the total.
 
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 4 tests in 0.000s
 
OK
```

## Test Case Number: TC-11

**Test Case Name:** Missing state starts a new total (`test_missing_state_starts_a_new_total`)

**Expected output:** Same as a new state: freeze_s 0, last_good = the reading

### Red

With no saved state (None), the function crashed with a TypeError. This will happen when nothing is saved on the box yet.

*Test written first:*

```text
def test_missing_state_starts_a_new_total(self):
    r0 = reading(0, 0.5)
    state = fx.accumulate_freeze(None, r0, LIMIT)
    self.assertEqual(state, {"freeze_s": 0, "last_good": r0})
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ERROR
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
========================================
ERROR: test_missing_state_starts_a_new_total
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 39, in test_missing_state_starts_a_new_total
    state = fx.accumulate_freeze(None, r0, LIMIT)
  File "freeze_exposure.py", line 59, in accumulate_freeze
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
TypeError: 'NoneType' object is not subscriptable
 
----------------------------------------
Ran 5 tests in 0.001s
 
FAILED (errors=1)
```

### Green

When state is None, start from new_freeze_state().

*Code in freeze_exposure.py:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Add the freeze time for `record` to the total.
 
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    if state is None:
        state = new_freeze_state()
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 5 tests in 0.001s
 
OK
```

### Yellow

Documented the state shape and when it can be None. All 5 tests pass.

*Code after refactoring:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Add the freeze time for `record` to the total.
 
    state: {"freeze_s": int, "last_good": record or None}, or None when there
    is no saved state yet (for example a new shipment).
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    if state is None:
        state = new_freeze_state()
    state["freeze_s"] += freeze_increment_s(state["last_good"], record, lower_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 5 tests in 0.001s
 
OK
```

## Test Case Number: TC-12

**Test Case Name:** Old state is not changed (`test_old_state_is_not_changed`)

**Expected output:** Old state still freeze_s 0; new state freeze_s 300

### Red

The function changed the state it was given, so the old state also showed 300 s and the new reading. Saving and comparing states (next session) needs the old one untouched.

*Test written first:*

```text
def test_old_state_is_not_changed(self):
    old = {"freeze_s": 0, "last_good": reading(300, 1.5)}
    new = fx.accumulate_freeze(old, reading(600, 0.5), LIMIT)
    self.assertEqual(old, {"freeze_s": 0, "last_good": reading(300, 1.5)})
    self.assertEqual(new["freeze_s"], 300)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_old_state_is_not_changed ... FAIL
test_total_grows_by_the_freeze_time ... ok
 
========================================
FAIL: test_old_state_is_not_changed
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 45, in test_old_state_is_not_changed
    self.assertEqual(old, {"freeze_s": 0, "last_good": reading(300, 1.5)})
AssertionError: {'freeze_s': 300, 'last_good': {'device_id': 'BOX-001'[96 chars]one}} != {'freeze_s': 0, 'last_good': {'device_id': 'BOX-001', [94 chars]one}}
- {'freeze_s': 300,
?              --
 
+ {'freeze_s': 0,
   'last_good': {'device_id': 'BOX-001',
                 'error': None,
                 'ok': True,
                 'seq': 1,
                 'shipment_id': 'SHP-1001',
-                'temp_c': 0.5,
?                          ^
 
+                'temp_c': 1.5,
?                          ^
 
-                'timestamp_s': 600}}
?                               ^
 
+                'timestamp_s': 300}}
?                               ^
 
 
----------------------------------------
Ran 6 tests in 0.001s
 
FAILED (failures=1)
```

### Green

Build a new dict instead of changing the old one.

*Code in freeze_exposure.py:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Add the freeze time for `record` to the total.
 
    state: {"freeze_s": int, "last_good": record or None}, or None when there
    is no saved state yet (for example a new shipment).
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    if state is None:
        state = new_freeze_state()
    freeze_s = state["freeze_s"] + freeze_increment_s(state["last_good"], record, lower_limit_c)
    last_good = state["last_good"]
    if is_good_reading(record):
        last_good = record
    return {"freeze_s": freeze_s, "last_good": last_good}
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_old_state_is_not_changed ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 6 tests in 0.000s
 
OK
```

### Yellow

Final clean-up: read last_good once, and a docstring that states AC1 (no heat here) and AC2 (only grows). This is the version in exposure/freeze_exposure.py. All 6 tests pass, and the full test file with all 27 tests passes.

*Code after refactoring:*

```text
def new_freeze_state():
    """Start of a shipment: no freeze time yet, no reading yet."""
    return {"freeze_s": 0, "last_good": None}
 
 
def accumulate_freeze(state, record, lower_limit_c):
    """Return the freeze state after `record`. Never changes `state`.
 
    state: {"freeze_s": int, "last_good": record or None}, or None when there
    is no saved state yet (for example a new shipment).
 
    freeze_s only ever grows (AC2): the only change is adding
    freeze_increment_s(), which is never negative. Heat is not read or written
    here (AC1). Only a good reading becomes last_good, so after a failed read
    the gap is counted when the next good reading arrives.
    """
    if state is None:
        state = new_freeze_state()
    last_good = state["last_good"]
    freeze_s = state["freeze_s"] + freeze_increment_s(last_good, record, lower_limit_c)
    if is_good_reading(record):
        last_good = record
    return {"freeze_s": freeze_s, "last_good": last_good}
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_old_state_is_not_changed ... ok
test_total_grows_by_the_freeze_time ... ok
 
----------------------------------------
Ran 6 tests in 0.000s
 
OK
```
