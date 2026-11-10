# TDD Test Report
**Smart Cold Box Sprint 2 Story 004-1 Accumulate heat exposure**  
**Session 2: `accumulate_heat()`**

## Test Case Summary

| Feature | Expected Output | Test Case Number | Test Case Name | Dev | Test Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **004-1 Accumulate heat exposure** | `{"heat_s": 0, "last_good": None}` | **TC-07** | New state starts at zero | Kristranan P. (Areef) | 10 Nov 2026 |
| | `heat_s` stays 0; `last_good` = the first reading | **TC-08** | First reading is remembered and adds nothing | Kristranan P. (Areef) | 10 Nov 2026 |
| | `heat_s` goes from 600 to 900 s ($9.0^{\circ}\text{C}$ at 300 s, next reading at 600 s) | **TC-09** | Total grows by the heat time | Kristranan P. (Areef) | 10 Nov 2026 |
| | `heat_s` stays 0; `last_good` stays the $9.0^{\circ}\text{C}$ reading | **TC-10** | Failed read keeps the last good reading | Kristranan P. (Areef) | 10 Nov 2026 |
| | Same as a new state: `heat_s` 0, `last_good` = the reading | **TC-11** | Missing state starts a new total | Kristranan P. (Areef) | 10 Nov 2026 |
| | Old state still `heat_s` 0; new state `heat_s` 300 | **TC-12** | Old state is not changed | Kristranan P. (Areef) | 10 Nov 2026 |

*Full test file after the last refactor (all 27 tests in `heat_exposure/test_heat_exposure.py`): Ran 27 tests in 0.0025s OK*

---

### Test Case Number: TC-07
**Test Case Name:** New state starts at zero (`test_new_state_starts_at_zero`)  
**Expected Output:** `{"heat_s": 0, "last_good": None}`

#### RED PHASE
Wrote the test first. `new_heat_state()` did not exist yet, so the test stopped with an `AttributeError`.

*Test written first:*
```python
def test_new_state_starts_at_zero(self):
    self.assertEqual(hx.new_heat_state(), {"heat_s": 0, "last_good": None})
```

*Result: fails*
```text
$ python -m unittest -v test_heat_exposure
test_new_state_starts_at_zero ... ERROR

======================================================================
ERROR: test_new_state_starts_at_zero
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_heat_exposure.py", line 20, in test_new_state_starts_at_zero
    self.assertEqual(hx.new_heat_state(), {"heat_s": 0, "last_good": None})
AttributeError: module 'heat_exposure' has no attribute 'new_heat_state'

Ran 1 test in 0.002s
FAILED (errors=1)
```

#### GREEN PHASE
Smallest code that passes: return a dict with `heat_s = 0` and no reading yet.

*Code in `heat_exposure.py`:*
```python
def new_heat_state():
    return {"heat_s": 0, "last_good": None}
```

*Result: passes*
```text
$ python -m unittest -v test_heat_exposure
test_new_state_starts_at_zero ... ok

Ran 1 test in 0.000s
OK
```

#### YELLOW PHASE (REFACTOR)
Added a docstring that states what the start state means (start of a shipment). No logic change; the test still passes.

*Code after refactoring:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}
```

*Result: still passes*
```text
$ python -m unittest -v test_heat_exposure
test_new_state_starts_at_zero ... ok

Ran 1 test in 0.000s
OK
```

---

### Test Case Number: TC-08
**Test Case Name:** First reading is remembered and adds nothing (`test_first_reading_is_remembered_and_adds_nothing`)  
**Expected Output:** `heat_s` stays 0; `last_good` = the first reading

#### RED PHASE
`accumulate_heat()` did not exist yet, so the test stopped with an `AttributeError`.

*Test written first:*
```python
def test_first_reading_is_remembered_and_adds_nothing(self):
    r0 = reading(0, 9.0)
    state = hx.accumulate_heat(hx.new_heat_state(), r0, LIMIT)
    self.assertEqual(state, {"heat_s": 0, "last_good": r0})
```

*Result: fails*
```text
$ python -m unittest -v test_heat_exposure
test_first_reading_is_remembered_and_adds_nothing ... ERROR
test_new_state_starts_at_zero ... ok

======================================================================
ERROR: test_first_reading_is_remembered_and_adds_nothing
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_heat_exposure.py", line 24, in test_first_reading_is_remembered_and_adds_nothing
    state = hx.accumulate_heat(hx.new_heat_state(), r0, LIMIT)
AttributeError: module 'heat_exposure' has no attribute 'accumulate_heat'

Ran 2 tests in 0.001s
FAILED (errors=1)
```

#### GREEN PHASE
Smallest code that passes: store the reading as `last_good` and return the state.

*Code in `heat_exposure.py`:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    state["last_good"] = record
    return state
```

*Result: passes*
```text
$ python -m unittest -v test_heat_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok

Ran 2 tests in 0.000s
OK
```

#### YELLOW PHASE (REFACTOR)
No code change. The total is still not added here on purpose: the next test asks for it. Both tests pass.

*Result: still passes*
```text
$ python -m unittest -v test_heat_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok

Ran 2 tests in 0.000s
OK
```

---

### Test Case Number: TC-09
**Test Case Name:** Total grows by the heat time (`test_total_grows_by_the_heat_time`)  
**Expected Output:** `heat_s` goes from 600 to 900 s ($9.0^{\circ}\text{C}$ at 300 s, next reading at 600 s)

#### RED PHASE
The function only remembered the reading, so the total stayed at 600 instead of 900.

*Test written first:*
```python
def test_total_grows_by_the_heat_time(self):
    state = {"heat_s": 600, "last_good": reading(300, 9.0)}
    state = hx.accumulate_heat(state, reading(600, 5.0), LIMIT)
    self.assertEqual(state["heat_s"], 900)
```

*Result: fails*
```text
$ python -m unittest -v test_heat_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... FAIL

======================================================================
FAIL: test_total_grows_by_the_heat_time
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_heat_exposure.py", line 30, in test_total_grows_by_the_heat_time
    self.assertEqual(state["heat_s"], 900)
AssertionError: 600 != 900

Ran 3 tests in 0.001s
FAILED (failures=1)
```

#### GREEN PHASE
Add `heat_increment_s()` (from session 1) to `heat_s` before remembering the new reading.

*Code in `heat_exposure.py`:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
    state["last_good"] = record
    return state
```

*Result: passes*
```text
$ python -m unittest -v test_heat_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

Ran 3 tests in 0.000s
OK
```

#### YELLOW PHASE (REFACTOR)
Added a docstring. The total can only change by adding `heat_increment_s()`, which is never negative, so it can never go down (AC2). All 3 tests pass.

*Code after refactoring:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Add the heat time for record to the total, then remember record."""
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
    state["last_good"] = record
    return state
```

*Result: still passes*
```text
$ python -m unittest -v test_heat_exposure
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

Ran 3 tests in 0.000s
OK
```

---

### Test Case Number: TC-10
**Test Case Name:** Failed read keeps the last good reading (`test_failed_read_keeps_the_last_good_reading`)  
**Expected Output:** `heat_s` stays 0; `last_good` stays the $9.0^{\circ}\text{C}$ reading

#### RED PHASE
The failed read replaced `last_good`. The gap after it would then be measured from a reading with no temperature, so heat time would be lost.

*Test written first:*
```python
def test_failed_read_keeps_the_last_good_reading(self):
    warm = reading(0, 9.0)
    state = hx.accumulate_heat({"heat_s": 0, "last_good": warm}, failed(300), LIMIT)
    self.assertEqual(state, {"heat_s": 0, "last_good": warm})
```

*Result: fails*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... FAIL
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

======================================================================
FAIL: test_failed_read_keeps_the_last_good_reading
----------------------------------------------------------------------
AssertionError: {'heat_s': 0, 'last_good': {'ok': False, 'temp_c': None, ...}} != {'heat_s': 0, 'last_good': {'ok': True, 'temp_c': 9.0, ...}}

Ran 4 tests in 0.003s
FAILED (failures=1)
```

#### GREEN PHASE
Only a good reading becomes `last_good` (uses `is_good_reading()` from session 1).

*Code in `heat_exposure.py`:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Add the heat time for record to the total, then remember record."""
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: passes*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

Ran 4 tests in 0.000s
OK
```

#### YELLOW PHASE (REFACTOR)
Rewrote the docstring to explain why: after a failed read, the gap is counted when the next good reading arrives. All 4 tests pass.

*Code after refactoring:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Add the heat time for record to the total.
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: still passes*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

Ran 4 tests in 0.000s
OK
```

---

### Test Case Number: TC-11
**Test Case Name:** Missing state starts a new total (`test_missing_state_starts_a_new_total`)  
**Expected Output:** Same as a new state: `heat_s` 0, `last_good` = the reading

#### RED PHASE
With no saved state (`None`), the function crashed with a `TypeError`. This will happen when nothing is saved on the box yet.

*Test written first:*
```python
def test_missing_state_starts_a_new_total(self):
    r0 = reading(0, 9.0)
    state = hx.accumulate_heat(None, r0, LIMIT)
    self.assertEqual(state, {"heat_s": 0, "last_good": r0})
```

*Result: fails*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ERROR
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

======================================================================
ERROR: test_missing_state_starts_a_new_total
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_heat_exposure.py", line 39, in test_missing_state_starts_a_new_total
    state = hx.accumulate_heat(None, r0, LIMIT)
  File "heat_exposure.py", line 59, in accumulate_heat
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
TypeError: 'NoneType' object is not subscriptable

Ran 5 tests in 0.001s
FAILED (errors=1)
```

#### GREEN PHASE
When `state` is `None`, start from `new_heat_state()`.

*Code in `heat_exposure.py`:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Add the heat time for record to the total.
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    if state is None:
        state = new_heat_state()
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: passes*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

Ran 5 tests in 0.001s
OK
```

#### YELLOW PHASE (REFACTOR)
Documented the state shape and when it can be `None`. All 5 tests pass.

*Code after refactoring:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Add the heat time for record to the total.
    state: {"heat_s": int, "last_good": record or None}, or None when there
    is no saved state yet (for example a new shipment).
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    if state is None:
        state = new_heat_state()
    state["heat_s"] += heat_increment_s(state["last_good"], record, upper_limit_c)
    if is_good_reading(record):
        state["last_good"] = record
    return state
```

*Result: still passes*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_total_grows_by_the_heat_time ... ok

Ran 5 tests in 0.001s
OK
```

---

### Test Case Number: TC-12
**Test Case Name:** Old state is not changed (`test_old_state_is_not_changed`)  
**Expected Output:** Old state still `heat_s` 0; new state `heat_s` 300

#### RED PHASE
The function changed the state it was given, so the old state also showed 300 s and the new reading. Saving and comparing states needs the old one untouched.

*Test written first:*
```python
def test_old_state_is_not_changed(self):
    old = {"heat_s": 0, "last_good": reading(300, 9.0)}
    new = hx.accumulate_heat(old, reading(600, 5.0), LIMIT)
    self.assertEqual(old, {"heat_s": 0, "last_good": reading(300, 9.0)})
    self.assertEqual(new["heat_s"], 300)
```

*Result: fails*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_old_state_is_not_changed ... FAIL
test_total_grows_by_the_heat_time ... ok

======================================================================
FAIL: test_old_state_is_not_changed
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_heat_exposure.py", line 45, in test_old_state_is_not_changed
    self.assertEqual(old, {"heat_s": 0, "last_good": reading(300, 9.0)})
AssertionError: {'heat_s': 300, 'last_good': ...} != {'heat_s': 0, 'last_good': ...}

Ran 6 tests in 0.001s
FAILED (failures=1)
```

#### GREEN PHASE
Build a new dict instead of changing the old one.

*Code in `heat_exposure.py`:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Add the heat time for record to the total.
    state: {"heat_s": int, "last_good": record or None}, or None when there
    is no saved state yet (for example a new shipment).
    Only a good reading becomes last_good, so after a failed read the gap is
    counted when the next good reading arrives.
    """
    if state is None:
        state = new_heat_state()
    last_good = state["last_good"]
    heat_s = state["heat_s"] + heat_increment_s(last_good, record, upper_limit_c)
    if is_good_reading(record):
        last_good = record
    return {"heat_s": heat_s, "last_good": last_good}
```

*Result: passes*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_old_state_is_not_changed ... ok
test_total_grows_by_the_heat_time ... ok

Ran 6 tests in 0.000s
OK
```

#### YELLOW PHASE (REFACTOR)
Final clean-up: read `last_good` once, and a docstring that states AC1 (no freeze here) and AC2 (only grows). This is the version in `heat_exposure/heat_exposure.py`. All 6 tests pass, and the full test file with all 27 tests passes.

*Code after refactoring:*
```python
def new_heat_state():
    """Start of a shipment: no heat time yet, no reading yet."""
    return {"heat_s": 0, "last_good": None}

def accumulate_heat(state, record, upper_limit_c):
    """Return the heat state after record. Never changes state.
    state: {"heat_s": int, "last_good": record or None}, or None when there
    is no saved state yet (for example a new shipment).
    heat_s only ever grows (AC2): the only change is adding
    heat_increment_s(), which is never negative. Freeze is not read or written
    here (AC1). Only a good reading becomes last_good, so after a failed read
    the gap is counted when the next good reading arrives.
    """
    if state is None:
        state = new_heat_state()
    last_good = state["last_good"]
    heat_s = state["heat_s"] + heat_increment_s(last_good, record, upper_limit_c)
    if is_good_reading(record):
        last_good = record
    return {"heat_s": heat_s, "last_good": last_good}
```

*Result: still passes*
```text
$ python -m unittest -v test_heat_exposure
test_failed_read_keeps_the_last_good_reading ... ok
test_first_reading_is_remembered_and_adds_nothing ... ok
test_missing_state_starts_a_new_total ... ok
test_new_state_starts_at_zero ... ok
test_old_state_is_not_changed ... ok
test_total_grows_by_the_heat_time ... ok

Ran 6 tests in 0.000s
OK
```