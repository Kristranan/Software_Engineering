# TDD Test Report

**Story:** 004-3 Compare against vaccine profile, Sprint 2, Session 2

**Developer:** Shogun

**Test date:** 11 Nov 2026

**Task:** Connect comparison to Aleef's heat accumulation and Sia's freeze accumulation. Check that totals and profile limits use seconds, and that later warming does not cancel recorded freeze exposure.

**Implementation:** `vaccine_profile/exposure_comparison.py`, using `heat_increment_s`, `accumulate_freeze`, and `compare_exposure`.

**Tests:** `vaccine_profile/test_exposure_comparison.py`, Python unittest with simulated readings and no hardware.

**Status:** The three planned simulated integration cases pass: heat totals, freeze totals, and preservation of freeze after warming. The full vaccine_profile suite also passes (18 tests). The results below were observed during this session. TC numbers continue from Shogun's Session 1 and are scoped to this developer's report.

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| Connect accumulated heat to profile comparison | Two good readings at 9 C, at 0 s and 60 s, produce heat_s=60 and freeze_s=0. With heat_limit_s=59 and freeze_limit_s=120, heat_exceeded=True and freeze_exceeded=False. | TC06 | `test_heat_total_in_seconds_reaches_comparison` | Shogun | 11 Nov 2026 |
| Connect accumulated freeze to profile comparison | Two good readings at 1 C, at 0 s and 60 s, produce heat_s=0 and freeze_s=60. With heat_limit_s=120 and freeze_limit_s=59, heat_exceeded=False and freeze_exceeded=True. | TC07 | `test_freeze_total_in_seconds_reaches_comparison` | Shogun | 11 Nov 2026 |
| Preserve freeze exposure after warming | Readings at 0 s / 1 C, 60 s / 9 C, and 120 s / 9 C produce heat_s=60 and freeze_s=60. With both profile limits at 59 s, both exceeded flags are True. | TC08 | `test_later_warming_does_not_cancel_freeze` | Shogun | 11 Nov 2026 |

## Test Case Number TC06

**Test Case Name:** `test_heat_total_in_seconds_reaches_comparison`

**Setup:** Upper temperature threshold 8 C, lower temperature threshold 2 C. Readings at 0 s and 60 s both report 9 C with `ok=True`. Profile limits are synthetic test values of 59 s for heat and 120 s for freeze.

**Expected behavior:** The earlier reading determines exposure for the 60-second interval. Heat accumulates to 60 s, freeze stays at 0 s, and each total is compared against its own limit using strict `>`.

### Red

The test was written and its first-reading initialization was corrected before the implementation module was created. The corrected test was run with:

```bash
python3 -m unittest discover -s vaccine_profile -p 'test_exposure_comparison.py' -v
```

Observed result, with the traceback shortened:

```text
ImportError: Failed to import test module: test_exposure_comparison
ModuleNotFoundError: No module named 'exposure_comparison'

Ran 1 test in 0.000s

FAILED (errors=1)
```

The test could not yet execute its assertions because the integration module did not exist.

### Green

Added `update_and_compare(state, record, profile, upper_limit_c, lower_limit_c)`. It initializes a new shipment state, adds Aleef's heat increment to the previous heat total, obtains the updated freeze total and last good reading from Sia's accumulator, and passes the two totals to the existing comparison. It returns the new state and comparison result.

The same command was run after the implementation was added:

```text
test_heat_total_in_seconds_reaches_comparison (test_exposure_comparison.ExposureComparisonTest.test_heat_total_in_seconds_reaches_comparison) ... ok

Ran 1 test in 0.000s

OK
```

All four assertions passed: heat_s=60, freeze_s=0, heat_exceeded=True, and freeze_exceeded=False.

### Yellow Refactor review

Reviewed the integration function for duplication and clarity. It reuses the existing heat, freeze, and comparison functions. No refactor was applied in this cycle. The verification run above passed with the current implementation.

## Test Case Number TC07

**Test Case Name:** `test_freeze_total_in_seconds_reaches_comparison`

**Setup:** Upper temperature threshold 8 C, lower temperature threshold 2 C. Two good readings at 1 C are taken at 0 s and 60 s. Synthetic profile limits are 120 s for heat and 59 s for freeze.

**Expected behavior:** Freeze accumulates to 60 s while heat stays at 0 s. Comparison reports heat_exceeded=False and freeze_exceeded=True.

### Red phase observation

This test passed on its first observed run. There was no observed Red result for TC07: the implementation from TC06 already called Sia's freeze accumulator and forwarded its total to comparison. This case adds regression coverage for that existing behavior.

### Green

No implementation change was required. Ran:

```bash
python3 -m unittest discover -s vaccine_profile -p 'test_exposure_comparison.py' -v
```

Observed result:

```text
test_freeze_total_in_seconds_reaches_comparison (test_exposure_comparison.ExposureComparisonTest.test_freeze_total_in_seconds_reaches_comparison) ... ok
test_heat_total_in_seconds_reaches_comparison (test_exposure_comparison.ExposureComparisonTest.test_heat_total_in_seconds_reaches_comparison) ... ok

Ran 2 tests in 0.000s

OK
```

### Yellow Refactor review

No refactor was applied. Both tests remain explicit about their readings, profile limits, totals, and comparison results. The verification run above passed with the current implementation.

## Test Case Number TC08

**Test Case Name:** `test_later_warming_does_not_cancel_freeze`

**Setup:** Upper temperature threshold 8 C and lower temperature threshold 2 C. Good readings are 1 C at 0 s, 9 C at 60 s, and 9 C at 120 s. Both synthetic profile limits are 59 s.

**Expected behavior:** The first interval contributes 60 s of freeze. The second contributes 60 s of heat. Freeze remains 60 s after warming, and comparison reports both exceeded flags as True.

### Red phase observation

The initial attempted run stopped at a test-file indentation error:

```text
IndentationError: expected an indented block after function definition on line 58
```

This was a syntax error in the new test, not evidence of a failed freeze-preservation behavior. After the method indentation was corrected, the test passed on its first executable run. No production-code change was needed for TC08, so no behavioral Red result is claimed.

### Green

Ran the integration test command after correcting indentation:

```text
test_freeze_total_in_seconds_reaches_comparison (test_exposure_comparison.ExposureComparisonTest.test_freeze_total_in_seconds_reaches_comparison) ... ok
test_heat_total_in_seconds_reaches_comparison (test_exposure_comparison.ExposureComparisonTest.test_heat_total_in_seconds_reaches_comparison) ... ok
test_later_warming_does_not_cancel_freeze (test_exposure_comparison.ExposureComparisonTest.test_later_warming_does_not_cancel_freeze) ... ok

Ran 3 tests in 0.000s

OK
```

### Yellow Refactor review

No refactor was applied. The test states the cold-to-warm sequence explicitly and checks both final totals and both comparison flags. The implementation continues to add nonnegative increments to separate totals.

## Regression verification

After TC08 passed, ran the existing comparison, loader, profile-check, and new integration tests together:

```bash
python3 -m unittest discover -s vaccine_profile -p 'test_*.py' -v
```

Observed summary:

```text
Ran 18 tests in 0.005s

OK
```

## Verification limits

These results verify simulated heat and freeze accumulation through the integration function on desktop CPython, including a cold-to-warm sequence that preserves freeze exposure while heat grows. They do not establish operation on ESP32, power-loss recovery, or connection to the live sensor scheduler. The integration receives an already loaded profile; joining this reading-update function to Plai's file-loading flow has not been tested here.
