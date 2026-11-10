# TDD Test Report

Smart Cold Box · Sprint 2 · Story 004-2 Accumulate freeze exposure · Session 2: freeze_increment_s()

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 004-2 Accumulate freeze exposure | 0 s (no earlier reading yet) | TC-01 | First reading adds nothing | Nutchuda D. (Sia) | 5 Nov 2026 |
| 004-2 Accumulate freeze exposure | 300 s (1.5 °C at 300 s, next reading at 600 s) | TC-02 | Earlier reading below the limit counts the whole gap | Nutchuda D. (Sia) | 5 Nov 2026 |
| 004-2 Accumulate freeze exposure | 0 s at 2.0 °C; 300 s at 1.9 °C | TC-03 | Exactly at the limit is not freeze | Nutchuda D. (Sia) | 5 Nov 2026 |
| 004-2 Accumulate freeze exposure | 0 s (the new read failed: ok = false, temp_c = null) | TC-04 | Failed read adds nothing | Nutchuda D. (Sia) | 5 Nov 2026 |
| 004-2 Accumulate freeze exposure | 0 s, no error (the earlier read failed) | TC-05 | Earlier reading must be a good reading | Nutchuda D. (Sia) | 5 Nov 2026 |
| 004-2 Accumulate freeze exposure | 0 s (clock went from 5000 s back to 10 s, as after a power cut) | TC-06 | Time going backwards adds nothing | Nutchuda D. (Sia) | 5 Nov 2026 |

*Full test file after the last refactor (all 17 tests in exposure/test_freeze_exposure.py):* `Ran 17 tests in 0.001s OK`

## Test Case Number: TC-01

**Test Case Name:** First reading adds nothing (`test_first_reading_adds_nothing`)

**Expected output:** 0 s (no earlier reading yet)

### Red

Wrote the test before any code. freeze_increment_s() did not exist yet, so the test module could not even import it.

*Test written first:*

```text
def test_first_reading_adds_nothing(self):
    self.assertEqual(freeze_increment_s(None, reading(0, 0.5), LIMIT), 0)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_freeze_exposure  ... ERROR
 
========================================
ERROR: test_freeze_exposure
----------------------------------------
ImportError: Failed to import test module: test_freeze_exposure
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 3, in <module>
    from freeze_exposure import freeze_increment_s
ImportError: cannot import name 'freeze_increment_s' from 'freeze_exposure' (freeze_exposure.py)
 
 
----------------------------------------
Ran 1 test in 0.000s
 
FAILED (errors=1)
```

### Green

Smallest code that passes: the function returns 0.

*Code in freeze_exposure.py:*

```text
def freeze_increment_s(last_good, record, lower_limit_c):
    return 0
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 1 test in 0.000s
 
OK
```

### Yellow

Added a module header and a docstring that states the contract (always a whole number of seconds, 0 or more). No logic change; the test still passes.

*Code after refactoring:*

```text
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    return 0
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 1 test in 0.000s
 
OK
```

## Test Case Number: TC-02

**Test Case Name:** Earlier reading below the limit counts the whole gap (`test_earlier_reading_below_limit_counts_the_whole_gap`)

**Expected output:** 300 s (1.5 °C at 300 s, next reading at 600 s)

### Red

The function always returns 0, so the 300 seconds between the two readings were not counted.

*Test written first:*

```text
def test_earlier_reading_below_limit_counts_the_whole_gap(self):
    self.assertEqual(freeze_increment_s(reading(300, 1.5), reading(600, 0.5), LIMIT), 300)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... FAIL
test_first_reading_adds_nothing ... ok
 
========================================
FAIL: test_earlier_reading_below_limit_counts_the_whole_gap
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 23, in test_earlier_reading_below_limit_counts_the_whole_gap
    self.assertEqual(freeze_increment_s(reading(300, 1.5), reading(600, 0.5), LIMIT), 300)
AssertionError: 0 != 300
 
----------------------------------------
Ran 2 tests in 0.001s
 
FAILED (failures=1)
```

### Green

When there is an earlier reading, return the time between the two timestamps.

*Code in freeze_exposure.py:*

```text
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if last_good is None:
        return 0
    return record["timestamp_s"] - last_good["timestamp_s"]
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 2 tests in 0.000s
 
OK
```

### Yellow

Named the time between readings gap_s, so the next rule (look at the earlier temperature) reads clearly. Both tests still pass.

*Code after refactoring:*

```text
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if last_good is None:
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    return gap_s
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 2 tests in 0.000s
 
OK
```

## Test Case Number: TC-03

**Test Case Name:** Exactly at the limit is not freeze (`test_exactly_at_limit_is_not_freeze`)

**Expected output:** 0 s at 2.0 °C; 300 s at 1.9 °C

### Red

The gap was counted no matter what the temperature was, so a reading of exactly 2.0 °C still added 300 s.

*Test written first:*

```text
def test_exactly_at_limit_is_not_freeze(self):
    self.assertEqual(freeze_increment_s(reading(0, 2.0), reading(300, 2.0), LIMIT), 0)
    self.assertEqual(freeze_increment_s(reading(0, 1.9), reading(300, 2.0), LIMIT), 300)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... FAIL
test_first_reading_adds_nothing ... ok
 
========================================
FAIL: test_exactly_at_limit_is_not_freeze
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 26, in test_exactly_at_limit_is_not_freeze
    self.assertEqual(freeze_increment_s(reading(0, 2.0), reading(300, 2.0), LIMIT), 0)
AssertionError: 300 != 0
 
----------------------------------------
Ran 3 tests in 0.001s
 
FAILED (failures=1)
```

### Green

Count the gap only when the earlier reading is strictly below lower_limit_c (2.0 is not freeze, 1.9 is).

*Code in freeze_exposure.py:*

```text
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if last_good is None:
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 3 tests in 0.000s
 
OK
```

### Yellow

No code change. Checked that strict “\<” matches assumption A1 (“below” means strictly less than) and that the same rule also gives 0 for a reading that is too warm. All 3 tests pass.

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 3 tests in 0.000s
 
OK
```

## Test Case Number: TC-04

**Test Case Name:** Failed read adds nothing (`test_failed_read_adds_nothing`)

**Expected output:** 0 s (the new read failed: ok = false, temp_c = null)

### Red

A failed read still has a timestamp, so the function counted 300 s of freeze for a reading with no temperature.

*Test written first:*

```text
def test_failed_read_adds_nothing(self):
    self.assertEqual(freeze_increment_s(reading(0, 0.5), failed(300), LIMIT), 0)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... FAIL
test_first_reading_adds_nothing ... ok
 
========================================
FAIL: test_failed_read_adds_nothing
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 30, in test_failed_read_adds_nothing
    self.assertEqual(freeze_increment_s(reading(0, 0.5), failed(300), LIMIT), 0)
AssertionError: 300 != 0
 
----------------------------------------
Ran 4 tests in 0.001s
 
FAILED (failures=1)
```

### Green

Return 0 when the new record is not ok.

*Code in freeze_exposure.py:*

```text
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if last_good is None:
        return 0
    if not record.get("ok"):
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 4 tests in 0.000s
 
OK
```

### Yellow

Moved the “did the read work?” check into its own function, is_good_reading(): ok must be True and temp_c must be a number. Same behaviour, easier to reuse for the earlier reading. All 4 tests pass.

*Code after refactoring:*

```text
def is_good_reading(record):
    """True when the read worked: ok is True and temp_c is a number."""
    if record is None or record.get("ok") is not True:
        return False
    temp = record.get("temp_c")
    return not isinstance(temp, bool) and isinstance(temp, (int, float))
 
 
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if last_good is None:
        return 0
    if not is_good_reading(record):
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
 
----------------------------------------
Ran 4 tests in 0.000s
 
OK
```

## Test Case Number: TC-05

**Test Case Name:** Earlier reading must be a good reading (`test_last_good_must_be_good`)

**Expected output:** 0 s, no error (the earlier read failed)

### Red

When the earlier reading had failed, its temp_c is None and comparing None \< 2.0 crashed with a TypeError.

*Test written first:*

```text
def test_last_good_must_be_good(self):
    self.assertEqual(freeze_increment_s(failed(0), reading(300, 0.5), LIMIT), 0)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
test_last_good_must_be_good ... ERROR
 
========================================
ERROR: test_last_good_must_be_good
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 33, in test_last_good_must_be_good
    self.assertEqual(freeze_increment_s(failed(0), reading(300, 0.5), LIMIT), 0)
  File "freeze_exposure.py", line 20, in freeze_increment_s
    if last_good["temp_c"] < lower_limit_c:
TypeError: '<' not supported between instances of 'NoneType' and 'float'
 
----------------------------------------
Ran 5 tests in 0.001s
 
FAILED (errors=1)
```

### Green

Return 0 when the earlier reading is not a good reading.

*Code in freeze_exposure.py:*

```text
def is_good_reading(record):
    """True when the read worked: ok is True and temp_c is a number."""
    if record is None or record.get("ok") is not True:
        return False
    temp = record.get("temp_c")
    return not isinstance(temp, bool) and isinstance(temp, (int, float))
 
 
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if last_good is None:
        return 0
    if not is_good_reading(record):
        return 0
    if not is_good_reading(last_good):
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
test_last_good_must_be_good ... ok
 
----------------------------------------
Ran 5 tests in 0.002s
 
OK
```

### Yellow

is_good_reading(None) already returns False, so the separate “last_good is None” check was removed and the three guard checks became one line. All 5 tests pass.

*Code after refactoring:*

```text
def is_good_reading(record):
    """True when the read worked: ok is True and temp_c is a number."""
    if record is None or record.get("ok") is not True:
        return False
    temp = record.get("temp_c")
    return not isinstance(temp, bool) and isinstance(temp, (int, float))
 
 
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if not is_good_reading(last_good) or not is_good_reading(record):
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
test_last_good_must_be_good ... ok
 
----------------------------------------
Ran 5 tests in 0.000s
 
OK
```

## Test Case Number: TC-06

**Test Case Name:** Time going backwards adds nothing (`test_time_going_backwards_adds_nothing`)

**Expected output:** 0 s (clock went from 5000 s back to 10 s, as after a power cut)

### Red

After a restart the clock can go back. The gap was negative, so the function returned −4990 and would have lowered the freeze total (breaks AC2).

*Test written first:*

```text
def test_time_going_backwards_adds_nothing(self):
    # After a power cut without an RTC, the clock can restart.
    self.assertEqual(freeze_increment_s(reading(5000, 0.5), reading(10, 0.5), LIMIT), 0)
```

*Result: fails*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
test_last_good_must_be_good ... ok
test_time_going_backwards_adds_nothing ... FAIL
 
========================================
FAIL: test_time_going_backwards_adds_nothing
----------------------------------------
Traceback (most recent call last):
  File "test_freeze_exposure.py", line 37, in test_time_going_backwards_adds_nothing
    self.assertEqual(freeze_increment_s(reading(5000, 0.5), reading(10, 0.5), LIMIT), 0)
AssertionError: -4990 != 0
 
----------------------------------------
Ran 6 tests in 0.001s
 
FAILED (failures=1)
```

### Green

Return 0 when the gap is 0 or less.

*Code in freeze_exposure.py:*

```text
def is_good_reading(record):
    """True when the read worked: ok is True and temp_c is a number."""
    if record is None or record.get("ok") is not True:
        return False
    temp = record.get("temp_c")
    return not isinstance(temp, bool) and isinstance(temp, (int, float))
 
 
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0."""
    if not is_good_reading(last_good) or not is_good_reading(record):
        return 0
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    if gap_s <= 0:
        return 0
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
test_last_good_must_be_good ... ok
test_time_going_backwards_adds_nothing ... ok
 
----------------------------------------
Ran 6 tests in 0.000s
 
OK
```

### Yellow

Final clean-up: whole-second timestamps with int(), a docstring that lists every case that adds 0, and the rule R1 comment. This is the version on GitHub (exposure/freeze_exposure.py). All 6 tests pass, and the full file with all 17 tests passes.

*Code after refactoring:*

```text
def is_good_reading(record):
    """True when the read worked: ok is True and temp_c is a number."""
    if record is None or record.get("ok") is not True:
        return False
    temp = record.get("temp_c")
    return not isinstance(temp, bool) and isinstance(temp, (int, float))
 
 
def freeze_increment_s(last_good, record, lower_limit_c):
    """Seconds of freeze to add when `record` arrives. Always an int >= 0 (AC2).
 
    last_good: the last good reading before `record`, or None for the first one.
    "Below" means strictly less than lower_limit_c (2.0 is not freeze, 1.9 is).
 
    Adds 0 when:
      - there is no earlier good reading yet
      - `record` is a failed read (the gap is counted at the next good reading)
      - time stands still or goes backwards (for example after a power cut,
        when the clock restarts)
      - the earlier reading was not below the limit
    """
    if not is_good_reading(last_good) or not is_good_reading(record):
        return 0
    gap_s = int(record["timestamp_s"]) - int(last_good["timestamp_s"])
    if gap_s <= 0:
        return 0
    if last_good["temp_c"] < lower_limit_c:
        return gap_s
    return 0
```

*Result: still passes*

```text
$ python -m unittest -v test_freeze_exposure
test_earlier_reading_below_limit_counts_the_whole_gap ... ok
test_exactly_at_limit_is_not_freeze ... ok
test_failed_read_adds_nothing ... ok
test_first_reading_adds_nothing ... ok
test_last_good_must_be_good ... ok
test_time_going_backwards_adds_nothing ... ok
 
----------------------------------------
Ran 6 tests in 0.000s
 
OK
```
