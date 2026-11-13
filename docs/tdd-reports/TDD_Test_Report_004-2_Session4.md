# TDD Test Report

Smart Cold Box · Sprint 2 · Story 004-2 Accumulate freeze exposure · Session 4: acceptance tests and the demo for the Sprint Review

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 004-2 Accumulate freeze exposure (demo) | freeze_s after each of the 7 readings: 0, 0, 300, 300, 900, 900, 900 | TC-19 | Trip ends with the right freeze total | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (demo) | One line per reading in words, e.g. "300 s below 2.0 C: freeze +300 s" and "300 s above 8.0 C: heat +300 s, freeze +0" | TC-20 | Label says what was counted | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (demo) | With a power cut after the 4th reading: an extra POWER CUT row, and freeze_s still ends at 900 | TC-21 | Power cut keeps the total | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (AC1) | 600 s warm then 600 s cold: heat 600, freeze 600. Warm-only trip: freeze 0. Cold-only trip: heat 0. | TC-22 | Freeze and heat are two separate totals | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (AC1) | freeze_state.json has only freeze_s (600) and last_good; no heat in it | TC-23 | Saved file holds freeze only | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (AC1) | lower_limit_c set to 1.0 in exposure_limits.json: 1.5 C is not counted, 0.5 C is (freeze 300) | TC-24 | Lower threshold comes from the config file | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (AC2) | 900 s cold, then 1200 s up to 15 C, then back in range: freeze stays 900 and never goes down; the warm time goes to heat | TC-25 | Later warming never offsets freeze | Nutchuda D. (Sia) | 13 Nov 2026 |
| 004-2 Accumulate freeze exposure (AC2) | 600 s of freeze, power cut, load from flash: 600; clock restarts at 0: stays 600 | TC-26 | Freeze is not lost after a power cut or clock restart | Nutchuda D. (Sia) | 13 Nov 2026 |

*TC-19 to TC-21 (demo_004_2.py) were written test first: Red, Green, Yellow below. TC-22 to TC-26 are the story's acceptance tests. They were written after the features they check, so they passed the first time; a mutation check below shows they fail when the code is broken.*

*Demo tests after the last refactor (exposure/test_demo_004_2.py):* `Ran 3 tests in 0.004s OK`

*All tests in exposure/ (limits, freeze_exposure, freeze_state, demo, acceptance):* `Ran 57 tests ... OK`

## Test Case Number: TC-19

**Test Case Name:** Trip ends with the right freeze total (`test_trip_ends_with_the_right_freeze_total`)

**Expected output:** freeze_s after each of the 7 readings: 0, 0, 300, 300, 900, 900, 900

### Red

Wrote the test first. demo_004_2.py did not exist yet, so the test module could not import it.

*Test written first:*

```text
def test_trip_ends_with_the_right_freeze_total(self):
    rows = demo.run_trip(demo.TRIP, LIMITS, self.path)
    self.assertEqual([row["freeze_s"] for row in rows], [0, 0, 300, 300, 900, 900, 900])
```

*Result: fails*

```text
$ python -m unittest -v test_demo_004_2
test_demo_004_2  ... ERROR

========================================
ERROR: test_demo_004_2
----------------------------------------
ImportError: Failed to import test module: test_demo_004_2
Traceback (most recent call last):
  File "test_demo_004_2.py", line 7, in <module>
    import demo_004_2 as demo
ModuleNotFoundError: No module named 'demo_004_2'


----------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```

### Green

Smallest code that passes: the demo trip, and run_trip() that feeds each reading through the real freeze_on_reading() and keeps one row per reading.

*Code in demo_004_2.py:*

```text
from freeze_state import freeze_on_reading

SHIPMENT = "SHP-DEMO"


def reading(ts, temp_c):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": temp_c, "ok": True, "error": None}


def failed(ts):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": None, "ok": False, "error": "sensor_timeout"}


TRIP = [reading(0, 4.0), reading(300, 1.5), reading(600, 0.5), failed(900),
        reading(1200, 3.0), reading(1500, 9.0), reading(1800, 4.0)]


def run_trip(records, limits, path):
    rows = []
    state = None
    for record in records:
        state = freeze_on_reading(state, record, limits["lower_limit_c"], path)
        rows.append({"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
                     "freeze_s": state["freeze_s"]})
    return rows
```

*Result: passes*

```text
$ python -m unittest -v test_demo_004_2
test_trip_ends_with_the_right_freeze_total ... ok

----------------------------------------
Ran 1 test in 0.015s

OK
```

### Yellow

Added a comment that says what happens in the trip, and a docstring for run_trip(). The test still passes.

*Code after refactoring:*

```text
def reading(ts, temp_c):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": temp_c, "ok": True, "error": None}


def failed(ts):
    return {"device_id": "BOX-001", "shipment_id": SHIPMENT, "seq": ts // 300,
            "timestamp_s": ts, "temp_c": None, "ok": False, "error": "sensor_timeout"}


# One reading every 5 minutes: in range, cold, a failed read, back in range,
# too warm, back in range.
TRIP = [reading(0, 4.0), reading(300, 1.5), reading(600, 0.5), failed(900),
        reading(1200, 3.0), reading(1500, 9.0), reading(1800, 4.0)]


def run_trip(records, limits, path):
    """Feed the readings through the real freeze code. One row per reading."""
    rows = []
    state = None
    for record in records:
        state = freeze_on_reading(state, record, limits["lower_limit_c"], path)
        rows.append({"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
                     "freeze_s": state["freeze_s"]})
    return rows
```

*Result: still passes*

```text
$ python -m unittest -v test_demo_004_2
test_trip_ends_with_the_right_freeze_total ... ok

----------------------------------------
Ran 1 test in 0.002s

OK
```

## Test Case Number: TC-20

**Test Case Name:** Label says what was counted (`test_label_says_what_was_counted`)

**Expected output:** One line per reading in words, e.g. "300 s below 2.0 C: freeze +300 s" and "300 s above 8.0 C: heat +300 s, freeze +0"

### Red

The rows had no label yet, so the test stopped with KeyError: 'label'.

*Test written first:*

```text
def test_label_says_what_was_counted(self):
    rows = demo.run_trip(demo.TRIP, LIMITS, self.path)
    self.assertEqual([row["label"] for row in rows], [
        "first reading",
        "300 s in range: +0",
        "300 s below 2.0 C: freeze +300 s",
        "failed read: counted at the next good reading",
        "600 s below 2.0 C: freeze +600 s",
        "300 s in range: +0",
        "300 s above 8.0 C: heat +300 s, freeze +0",
    ])
```

*Result: fails*

```text
$ python -m unittest -v test_demo_004_2
test_label_says_what_was_counted ... ERROR
test_trip_ends_with_the_right_freeze_total ... ok

========================================
ERROR: test_label_says_what_was_counted
----------------------------------------
Traceback (most recent call last):
  File "test_demo_004_2.py", line 26, in test_label_says_what_was_counted
    self.assertEqual([row["label"] for row in rows], [
KeyError: 'label'

----------------------------------------
Ran 2 tests in 0.006s

FAILED (errors=1)
```

### Green

Add label(): it asks the real freeze_increment_s() (Sia) and heat_increment_s() (Aleef) what the time since the last good reading counted as, and says it in words.

*Code in demo_004_2.py:*

```text
from freeze_exposure import freeze_increment_s, is_good_reading
from freeze_state import freeze_on_reading
from heat_exposure.heat_exposure import heat_increment_s

SHIPMENT = "SHP-DEMO"


def label(last_good, record, limits):
    if not is_good_reading(record):
        return "failed read: counted at the next good reading"
    if last_good is None:
        return "first reading"
    if freeze_increment_s(last_good, record, limits["lower_limit_c"]):
        return "%d s below %.1f C: freeze +%d s" % (
            record["timestamp_s"] - last_good["timestamp_s"], limits["lower_limit_c"],
            freeze_increment_s(last_good, record, limits["lower_limit_c"]))
    if heat_increment_s(last_good, record, limits["upper_limit_c"]):
        return "%d s above %.1f C: heat +%d s, freeze +0" % (
            record["timestamp_s"] - last_good["timestamp_s"], limits["upper_limit_c"],
            heat_increment_s(last_good, record, limits["upper_limit_c"]))
    return "%d s in range: +0" % (record["timestamp_s"] - last_good["timestamp_s"])


def run_trip(records, limits, path):
    """Feed the readings through the real freeze code. One row per reading."""
    rows = []
    state = None
    for record in records:
        text = label(state["last_good"] if state else None, record, limits)
        state = freeze_on_reading(state, record, limits["lower_limit_c"], path)
        rows.append({"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
                     "label": text, "freeze_s": state["freeze_s"]})
    return rows
```

*Result: passes*

```text
$ python -m unittest -v test_demo_004_2
test_label_says_what_was_counted ... ok
test_trip_ends_with_the_right_freeze_total ... ok

----------------------------------------
Ran 2 tests in 0.004s

OK
```

### Yellow

The gap and both increments were worked out twice. Now each is worked out once. Both tests pass.

*Code after refactoring:*

```text
def label(last_good, record, limits):
    """What the time since the last good reading counted as, in words."""
    if not is_good_reading(record):
        return "failed read: counted at the next good reading"
    if last_good is None:
        return "first reading"
    gap_s = record["timestamp_s"] - last_good["timestamp_s"]
    freeze = freeze_increment_s(last_good, record, limits["lower_limit_c"])
    heat = heat_increment_s(last_good, record, limits["upper_limit_c"])
    if freeze:
        return "%d s below %.1f C: freeze +%d s" % (gap_s, limits["lower_limit_c"], freeze)
    if heat:
        return "%d s above %.1f C: heat +%d s, freeze +0" % (gap_s, limits["upper_limit_c"], heat)
    return "%d s in range: +0" % gap_s
```

*Result: still passes*

```text
$ python -m unittest -v test_demo_004_2
test_label_says_what_was_counted ... ok
test_trip_ends_with_the_right_freeze_total ... ok

----------------------------------------
Ran 2 tests in 0.005s

OK
```

## Test Case Number: TC-21

**Test Case Name:** Power cut keeps the total (`test_power_cut_keeps_the_total`)

**Expected output:** With a power cut after the 4th reading: an extra POWER CUT row, and freeze_s still ends at 900

### Red

run_trip() had no way to act out a power cut (TypeError: unexpected keyword argument 'power_cut_after').

*Test written first:*

```text
def test_power_cut_keeps_the_total(self):
    rows = demo.run_trip(demo.TRIP, LIMITS, self.path, power_cut_after=4)
    self.assertEqual([row["freeze_s"] for row in rows], [0, 0, 300, 300, 300, 900, 900, 900])
    self.assertTrue(rows[4]["label"].startswith("POWER CUT"))
```

*Result: fails*

```text
$ python -m unittest -v test_demo_004_2
test_label_says_what_was_counted ... ok
test_power_cut_keeps_the_total ... ERROR
test_trip_ends_with_the_right_freeze_total ... ok

========================================
ERROR: test_power_cut_keeps_the_total
----------------------------------------
Traceback (most recent call last):
  File "test_demo_004_2.py", line 37, in test_power_cut_keeps_the_total
    rows = demo.run_trip(demo.TRIP, LIMITS, self.path, power_cut_after=4)
TypeError: run_trip() got an unexpected keyword argument 'power_cut_after'

----------------------------------------
Ran 3 tests in 0.005s

FAILED (errors=1)
```

### Green

After the n-th reading, drop the state in memory and load it back with load_freeze_state(), like the box does after a restart.

*Code in demo_004_2.py:*

```text
def run_trip(records, limits, path, power_cut_after=None):
    """Feed the readings through the real freeze code. One row per reading."""
    rows = []
    state = None
    for i, record in enumerate(records):
        text = label(state["last_good"] if state else None, record, limits)
        state = freeze_on_reading(state, record, limits["lower_limit_c"], path)
        rows.append({"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
                     "label": text, "freeze_s": state["freeze_s"]})
        if power_cut_after == i + 1:
            state = load_freeze_state(SHIPMENT, path)
            rows.append({"timestamp_s": None, "temp_c": None,
                         "label": "POWER CUT: restart, loaded from freeze_state.json",
                         "freeze_s": state["freeze_s"]})
    return rows
```

*Result: passes*

```text
$ python -m unittest -v test_demo_004_2
test_label_says_what_was_counted ... ok
test_power_cut_keeps_the_total ... ok
test_trip_ends_with_the_right_freeze_total ... ok

----------------------------------------
Ran 3 tests in 0.005s

OK
```

### Yellow

Count readings from 1 so power_cut_after=4 reads naturally, explain it in the docstring, and add main() that prints the demo. All 3 tests pass.

*Code after refactoring:*

```text
def run_trip(records, limits, path, power_cut_after=None):
    """Feed the readings through the real freeze code. One row per reading.

    power_cut_after=n: after the n-th reading, everything in memory is dropped
    and the state is loaded back from the file, as after a real power cut.
    """
    rows = []
    state = None
    for count, record in enumerate(records, 1):
        text = label(state["last_good"] if state else None, record, limits)
        state = freeze_on_reading(state, record, limits["lower_limit_c"], path)
        rows.append({"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
                     "label": text, "freeze_s": state["freeze_s"]})
        if count == power_cut_after:
            state = load_freeze_state(SHIPMENT, path)
            rows.append({"timestamp_s": None, "temp_c": None,
                         "label": "POWER CUT: restart, loaded from freeze_state.json",
                         "freeze_s": state["freeze_s"]})
    return rows
```

*Result: still passes*

```text
$ python -m unittest -v test_demo_004_2
test_label_says_what_was_counted ... ok
test_power_cut_keeps_the_total ... ok
test_trip_ends_with_the_right_freeze_total ... ok

----------------------------------------
Ran 3 tests in 0.005s

OK
```

## Acceptance tests: TC-22 to TC-26

File: `exposure/test_acceptance_004_2.py`. Each test runs the whole flow on the box: `exposure_limits.json` → readings → `freeze_on_reading()` (freeze total saved to `freeze_state.json`), with Aleef's `heat_increment_s()` counted next to it.

- **AC1.** Time below the lower threshold accumulates separately from heat: TC-22, TC-23, TC-24
- **AC2.** Freeze events are not offset by later warming: TC-25, TC-26

**TC-22 (AC1): Freeze and heat are two separate totals** (`test_freeze_and_heat_are_two_separate_totals`): 600 s warm then 600 s cold: heat 600, freeze 600. Warm-only trip: freeze 0. Cold-only trip: heat 0.

**TC-23 (AC1): Saved file holds freeze only** (`test_saved_file_holds_freeze_only`): freeze_state.json has only freeze_s (600) and last_good; no heat in it

**TC-24 (AC1): Lower threshold comes from the config file** (`test_lower_threshold_comes_from_the_config_file`): lower_limit_c set to 1.0 in exposure_limits.json: 1.5 C is not counted, 0.5 C is (freeze 300)

**TC-25 (AC2): Later warming never offsets freeze** (`test_later_warming_never_offsets_freeze`): 900 s cold, then 1200 s up to 15 C, then back in range: freeze stays 900 and never goes down; the warm time goes to heat

**TC-26 (AC2): Freeze is not lost after a power cut or clock restart** (`test_freeze_is_not_lost_after_a_power_cut_or_clock_restart`): 600 s of freeze, power cut, load from flash: 600; clock restarts at 0: stays 600

*Result:*

```text
$ python -m unittest -v test_acceptance_004_2
test_freeze_and_heat_are_two_separate_totals ... ok
test_freeze_is_not_lost_after_a_power_cut_or_clock_restart ... ok
test_later_warming_never_offsets_freeze ... ok
test_lower_threshold_comes_from_the_config_file ... ok
test_saved_file_holds_freeze_only ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.008s

OK
```

### Mutation check: do the acceptance tests catch real mistakes?

Each row is a copy of the code broken on purpose in one way, then the acceptance tests run against it. Every broken copy failed, so the tests really check AC1 and AC2. The real code is unchanged.

| Broken on purpose | Acceptance tests that failed | Result |
| --- | --- | --- |
| Warming takes freeze time off (and negative time allowed) | `test_freeze_and_heat_are_two_separate_totals`, `test_freeze_is_not_lost_after_a_power_cut_or_clock_restart`, `test_later_warming_never_offsets_freeze`, `test_lower_threshold_comes_from_the_config_file`, `test_saved_file_holds_freeze_only` | FAILED (failures=5) |
| Time above 8 C counted as freeze | `test_freeze_and_heat_are_two_separate_totals`, `test_freeze_is_not_lost_after_a_power_cut_or_clock_restart`, `test_later_warming_never_offsets_freeze`, `test_saved_file_holds_freeze_only` | FAILED (failures=4) |
| The total is never saved to the file | `test_freeze_is_not_lost_after_a_power_cut_or_clock_restart`, `test_saved_file_holds_freeze_only` | FAILED (errors=2) |
| Time going backwards is counted (negative) | `test_freeze_is_not_lost_after_a_power_cut_or_clock_restart` | FAILED (failures=1) |

## Demo output (python demo_004_2.py)

```text
Limits from exposure_limits.json: lower 2.0 C, upper 8.0 C

time    temp    time since the last good reading                   freeze_s
0 s     4.0 C   first reading                                      0
300 s   1.5 C   300 s in range: +0                                 0
600 s   0.5 C   300 s below 2.0 C: freeze +300 s                   300
900 s   failed  failed read: counted at the next good reading      300
                POWER CUT: restart, loaded from freeze_state.json  300
1200 s  3.0 C   600 s below 2.0 C: freeze +600 s                   900
1500 s  9.0 C   300 s in range: +0                                 900
1800 s  4.0 C   300 s above 8.0 C: heat +300 s, freeze +0          900

freeze_s never went down: True
```

## Definition of Done

| Definition of Done | Status |
| --- | --- |
| Code is merged | On `main` in `exposure/` once the files from this session are uploaded |
| Unit tests pass | Yes: 57 tests in `exposure/` OK |
| Acceptance Criteria pass | Yes: TC-22 to TC-26 (AC1 and AC2), and the mutation check |
| No critical defects remain | None known in the 004-2 code. Known limits: `main.py` still needs Shogun's two calls before the real box counts; time while the power is off is not counted until the team picks a time source; not yet run on the ESP32 board |
| The Product Owner accepts the Story | At the Sprint Review, 14 Nov 2026 |
