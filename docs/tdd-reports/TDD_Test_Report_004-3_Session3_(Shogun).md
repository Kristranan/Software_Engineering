# TDD Test Report

**Story:** 004-3 Compare against vaccine profile, Sprint 2, Session 3

**Developer:** Shogun

**Date:** 13 Nov 2026

**Task:** Prepare the demonstration and review acceptance criteria, including the pending connection from the sensor entry point to exposure totals and comparison.

**Status:** The entry point now stores every reading, updates separate persisted heat/freeze totals, and compares them against the loaded vaccine profile. The latest desktop verification passes across five relevant suites: 164 tests total after incorporating the team's additional heat tests at fa10ad8. Earlier 149-test results are retained below as historical evidence. A desktop demo exercises the actual flat board file layout with simulated hardware/time and blocked network access. ESP32/Wokwi execution and Product Owner acceptance remain pending. The original baseline was main at e11063a; Aleef's heat implementation was subsequently fetched from main at 2f6fed3.

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| Restore freeze state at boot | Load limits once and load state once for SHIPMENT_ID; retain None when no prior state exists. | TC09 | `test_boot_loads_freeze_state_for_current_shipment` | Shogun | 13 Nov 2026 |
| Update freeze on every emitted record | Good and failed readings each call the accumulator once with the configured lower threshold and the latest state; serial output remains the original JSON records. | TC10 | `test_emit_updates_freeze_for_good_and_failed_readings` | Shogun | 13 Nov 2026 |
| Persist freeze through warming and program reload | Cold-to-warm readings produce 60 s of freeze, save it, restore it for the same shipment, and retain it after another warm reading. | TC11 | `test_real_freeze_total_survives_warming_and_program_reload` | Shogun | 13 Nov 2026 |
| Store every reading (Issue 17) | Good and failed readings are passed to storage; a False storage result does not stop subsequent processing. | TC12 | `test_all_readings_are_stored_and_storage_false_does_not_stop_emit` | Shogun | 13 Nov 2026 |
| Restore and update heat separately | Load the current shipment's saved heat and call heat_on_reading with the configured upper temperature threshold. | TC13 | `test_heat_restores_at_boot_and_updates_with_its_own_threshold` | Shogun | 13 Nov 2026 |
| Compare updated totals | Pass the new heat total 120 s and freeze total 60 s to check_exposure and retain both returned flags. | TC14 | `test_comparison_uses_new_heat_and_freeze_totals` | Shogun | 13 Nov 2026 |
| Handle invalid comparison inputs/profile | ProfileError or ValueError yields unknown with unset flags; the next good reading retries successfully. | TC15 | `test_comparison_errors_are_unknown_and_next_reading_can_recover` | Shogun | 13 Nov 2026 |
| Handle sensor failure | Initial and failed-reading comparison status is unknown; comparison resumes after a good reading. | TC16 | `test_failed_read_is_unknown_and_next_good_reading_is_compared` | Shogun | 13 Nov 2026 |
| Offline full reading flow | Real Scheduler, storage, state, and profile code preserve 120 s heat / 120 s freeze and eight logged records through failure, warming, and program reload. | TC17 | `test_offline_trip_stores_failures_compares_totals_and_restores_after_restart` | Shogun | 13 Nov 2026 |
| Independent duration boundaries | Nine combinations of saved totals at 58, 59, and 60 s against 59 s limits yield the correct independent flags. | TC18 | `test_each_saved_total_below_at_and_above_its_own_profile_limit` | Shogun | 13 Nov 2026 |
| Invalid profile in full flow | A profile missing freeze_limit_s yields unknown with unset flags while both readings remain stored. | TC19 | `test_broken_profile_is_unknown_and_readings_are_still_stored` | Shogun | 13 Nov 2026 |

## Baseline verification

These are existing tests, including Plai's acceptance and demo tests. Their successful execution is baseline verification, not newly authored TDD evidence for this session.

```bash
python3 -m unittest discover -s vaccine_profile -p 'test_*.py' -v
```

Observed result:

```text
Ran 23 tests in 0.008s

OK
```

```bash
python3 -m unittest discover -s read_temp -p 'test_main.py' -v
```

Observed result:

```text
Ran 7 tests in 0.003s

OK
```

## Demonstration baseline

Ran `python3 vaccine_profile/demo_004_3.py`. The existing demo loads profile.json with synthetic limits of 7200 s for heat and 1800 s for freeze. Its supplied exposure totals are simulated.

| Scenario | Observed result |
| --- | --- |
| Normal trip, heat 600 s and freeze 0 s | Both within limit |
| Heat exactly 7200 s | Both within limit |
| Heat 7201 s | Heat EXCEEDED, freeze within limit |
| Freeze 1801 s | Heat within limit, freeze EXCEEDED |
| Heat 7201 s and freeze 60 s | Heat EXCEEDED, freeze within limit |
| Profile missing freeze_limit_s | UNKNOWN with a profile error |

## Acceptance criteria review

| Criterion | Current evidence | Remaining verification |
| --- | --- | --- |
| Accumulated exposure is compared to the loaded profile | TC17 executes actual main.py, Scheduler, persisted totals, and the real profile loader/checker in a staged board directory. Passed on desktop. | Verify the deployed flow on ESP32/Wokwi. |
| Heat and freeze are evaluated against their own limits | TC18 verifies all nine below/equal/above combinations through main.py; TC17 verifies cold and heat totals stay separate after warming. | Verify the same flow with the deployed modules. |
| Comparison runs entirely on the box | TC17-19 run the actual application modules offline in isolated CPython; socket operations are blocked. | Execute on ESP32 or Wokwi; desktop tests do not prove board execution. |

## Entry-point integration status

`read_temp/main.py` now loads exposure limits and separate freeze/heat states at boot. Each emitted record is printed unchanged as JSON, appended through storage.append_reading, and passed once to freeze_on_reading and heat_on_reading. Successful readings are evaluated through Plai's check_exposure, which loads profile.json and calls the existing comparison. The latest status and separate flags are exposed in main.comparison_result. Sensor failure, invalid profile, or invalid totals produce unknown rather than a safe-looking result; subsequent readings continue.

The original freeze-only stage did not include heat persistence, storage, or automatic comparison. During continuation, fetching main revealed Aleef's new heat_state.py at 2f6fed3; those connections could then be completed. The load_main test helper supplies fake modules by default, with explicit overrides for integration tests. Board file layout and remaining physical verification are documented in read_temp/DEPLOYMENT.md.

Deployment, power-loss behavior on the board, and Product Owner acceptance remain unverified. The existing acceptance tests and desktop demo do not close these verification gaps.

## Test Case Number TC09

**Test Case Name:** `test_boot_loads_freeze_state_for_current_shipment`

**Test file:** `read_temp/test_main_exposure.py`

**Expected behavior:** Importing the box entry point loads temperature limits once and restores freeze state once using the current SHIPMENT_ID. Both dependencies are mocked, so no state file is read or written.

### Red

Ran before adding the new imports and boot initialization to main.py:

```bash
python3 -m unittest discover -s read_temp -p 'test_main_exposure.py' -v
```

Observed result, with the traceback shortened:

```text
test_boot_loads_freeze_state_for_current_shipment (test_main_exposure.MainExposureTest.test_boot_loads_freeze_state_for_current_shipment) ... FAIL
AssertionError: Expected 'mock' to be called once. Called 0 times.

Ran 1 test in 0.001s

FAILED (failures=1)
```

The first assertion failed because load_limits had not been called. The subsequent load_freeze_state assertion was not reached.

### Green

Added imports to main.py for the limits loader and freeze state functions. After SHIPMENT_ID is declared, main loads limits and calls load_freeze_state(SHIPMENT_ID). Corrected the misplaced production imports/initialization in the test file and kept the test focused on dependency calls.

The existing load_main test helper gained default fake modules plus an optional modules argument for overrides. The new test uses these overrides, and legacy tests stay isolated from the filesystem.

Ran `python3 -m unittest discover -s read_temp -p 'test_main*.py' -v`:

```text
Ran 8 tests in 0.002s

OK
```

### Yellow Refactor review

Kept the dependency override in the existing import helper, avoiding separate copies of the hardware-faking setup. The helper preserves the original load_main(values) call interface for legacy tests.

## Test Case Number TC10

**Test Case Name:** `test_emit_updates_freeze_for_good_and_failed_readings`

**Expected behavior:** Starting from a saved state, emit sends a successful reading and a failed reading to freeze_on_reading in order, uses the configured lower_limit_c (0 C in this test), and keeps each returned state for the next call. JSON serial output remains unchanged.

### Red

Added the test after boot initialization passed, but before changing emit. Ran the new entry-point test file:

```text
test_boot_loads_freeze_state_for_current_shipment ... ok
test_emit_updates_freeze_for_good_and_failed_readings ... FAIL
AssertionError: {'freeze_s': 60, 'last_good': None} is not {'freeze_s': 120, 'last_good': None}

Ran 2 tests in 0.001s

FAILED (failures=1)
```

The failure occurred after the first emitted record: main.freeze still held the saved state rather than the accumulator's returned state. The failed-reading assertions had not yet been reached.

### Green

Added a global freeze declaration in emit and assigned the result of freeze_on_reading(freeze, record, limits["lower_limit_c"]) after printing the JSON record. There is no ok filter, so failed readings also reach the accumulator, which applies its existing failed-reading rules.

Ran the main test files again:

```text
Ran 9 tests in 0.002s

OK
```

The new test verifies both accumulator calls and their inputs, retention of the returned state, and both JSON output records.

### Yellow Refactor review

No additional production refactor was needed: emit contains one delegation to Sia's persistence function. It does not duplicate freeze accumulation or file-writing logic. scheduler.py was not modified.

## Test Case Number TC11

**Test Case Name:** `test_real_freeze_total_survives_warming_and_program_reload`

**Setup:** Uses the real freeze_exposure.py and freeze_state.py through the main entry point, with the sensor mocked and the state file in a temporary directory. Readings include shipment_id. The configured lower threshold is 2 C.

**Expected behavior:** At 0 s / 1 C, freeze is 0 s. At 60 s / 9 C it becomes 60 s, attributed to the earlier cold reading. At 120 s / 9 C it remains 60 s and is present in the state file. Reimporting main for the same shipment restores 60 s and the last reading at 120 s. A further warm reading at 180 s leaves freeze at 60 s.

### Red phase observation

No Red result occurred: this test passed on its first run after TC10. It verifies existing integration with the real persistence implementation rather than claiming a new failing behavior.

### Green

Ran `python3 -m unittest discover -s read_temp -p 'test_main_exposure.py' -v`:

```text
test_boot_loads_freeze_state_for_current_shipment ... ok
test_emit_updates_freeze_for_good_and_failed_readings ... ok
test_real_freeze_total_survives_warming_and_program_reload ... ok

Ran 3 tests in 0.003s

OK
```

The test checks intermediate totals, the actual JSON state file, restored last_good, and the total after a warm reading following reload. This is a desktop program-reload simulation, not a physical board power-cut test.

### Yellow Refactor review

Grouped test imports consistently after Green. The integration test keeps all file writes in a temporary directory and explicitly loads Sia's real modules, while the legacy tests retain fake modules.

## Freeze-stage regression verification

Ran the following commands independently after freeze integration:

```bash
python3 -m unittest discover -s read_temp -p 'test_*.py' -q
python3 -m unittest discover -s exposure -p 'test_*.py' -q
python3 -m unittest discover -s vaccine_profile -p 'test_*.py' -q
```

Observed results:

```text
read_temp:       Ran 27 tests in 0.008s — OK
exposure:        Ran 57 tests in 0.017s — OK
vaccine_profile: Ran 23 tests in 0.006s — OK
```

All 107 tests passed. The separate nested heat_exposure suite is not included in this count. After the final import-grouping cleanup, an additional focused run of `test_main*.py` passed: 10 tests in 0.003s, OK.

## Continued integration after the heat module became available

The following new tests were added in read_temp/test_main_pipeline.py. Each Red result below was observed before implementing the corresponding behavior. Tracebacks are shortened; no failures were manufactured by removing working code.

### TC12 Store every reading

**Red:** The append_reading mock received no calls for the good and failed readings:

```text
AssertionError: [] != [call({'timestamp_s': 0, 'temp_c': 4.0, 'o[62 chars]se})]
Ran 1 test in 0.000s
FAILED (failures=1)
```

**Green:** Imported append_reading in main.py and called it after printing each record. As requested in Issue 17, its boolean result is ignored. The test supplies False for the first append and True for the second; both records still reach freeze accumulation and retain their original serial JSON.

```text
Ran 1 test in 0.001s
OK
```

**Yellow:** The shared test helper supplies a fake storage module, keeping legacy tests from creating readings.jsonl. No scheduler change was needed.

### TC13 Restore and update heat

**Red:** The heat state loader was never called at boot:

```text
AssertionError: Expected 'mock' to be called once. Called 0 times.
Ran 2 tests in 0.001s
FAILED (failures=1)
```

**Green:** Imported Aleef's load_heat_state and heat_on_reading, restored heat for SHIPMENT_ID, and updated it on each record using upper_limit_c. The test uses 10 C as the configured upper threshold to catch a hardcoded 8 C or a swapped threshold, and verifies the returned state is retained.

```text
Ran 2 tests in 0.001s
OK
```

**Yellow:** Heat and freeze retain separate states/files and call their own persistence modules once per record. Existing update_and_compare is not called from emit, avoiding another accumulation path.

### TC14 Compare newly updated totals

**Red:** The comparison mock was not called after the accumulators returned heat 120 s and freeze 60 s:

```text
AssertionError: Expected 'mock' to be called once. Called 0 times.
Ran 3 tests in 0.001s
FAILED (failures=1)
```

**Green:** Called check_exposure with the new totals after both accumulators and retained its separate flags with status compared. This uses the real file-loading interface in production; no default vaccine limits are introduced.

```text
Ran 3 tests in 0.001s
OK
```

**Yellow:** Kept comparison status separate from the reading dictionary, preserving the serial/storage record schema and existing consumers.

### TC15 Comparison errors and recovery

**Red:** Both ProfileError and ValueError escaped emit and stopped the test's reading sequence:

```text
test_main.FakeProfileError: missing freeze limit
ValueError: bad total
Ran 4 tests in 0.002s
FAILED (errors=2)
```

**Green:** Catch these two expected comparison errors and retain status unknown, the reason, and None for both flags. The test checks that a second good reading retries and produces a valid comparison.

```text
Ran 4 tests in 0.001s
OK
```

**Yellow:** Added unknown_result(reason) to construct the same result shape consistently at boot and on errors.

### TC16 Sensor failure and recovery

**Red:** A failed sensor reading still received a compared status:

```text
AssertionError: 'compared' != 'unknown'
Ran 5 tests in 0.001s
FAILED (failures=1)
```

**Green:** After storing and updating states for every record, a failed reading sets unknown and skips comparison. Both states retain their own failed-reading handling. The next successful reading is compared normally. The test also verifies that boot status is unknown.

```text
Ran 15 tests in 0.009s
OK
```

This run included the legacy main tests, the three freeze-wiring tests, and all five new pipeline tests.

**Yellow:** No change to Scheduler or serial JSON output. Unknown flags are None, not False, so callers can distinguish missing comparison evidence from within-limit results.

## TC17 to TC19 Full-flow acceptance and demo

**Test file:** read_temp/test_box_pipeline.py

**Demo:** read_temp/demo_main.py

### Shared Red observation

The acceptance test file was added before its isolated desktop harness existed. Import failed, so none of the three test methods executed their assertions yet:

```text
ModuleNotFoundError: No module named 'demo_main'
Ran 1 test in 0.000s
FAILED (errors=1)
```

After the harness was implemented, all three cases passed on their first executable run. No individual behavioral Red result is claimed for these cases.

### Green and scope

The harness copies the actual main, Scheduler, config, storage, limits, heat/freeze, and profile modules into a temporary flat board directory. It runs them in an isolated CPython subprocess. Only machine/DHT hardware, time/sleep, and socket access are substituted. All application file loading, log appends, state updates, and profile comparisons are real.

- **TC17:** Readings at 60-second intervals are 9 C, 9 C, 1 C, 1 C, 4 C, sensor failure, and 4 C. Final heat and freeze are both 120 s; freeze stays unchanged after warming. With file-loaded profile limits 119 s heat and 120 s freeze, only heat exceeds. The failed reading is stored and produces unknown. Program reload restores both totals; one more warm reading leaves them unchanged. All eight logged records match the captured serial JSON, with zero skipped records. Socket access is blocked throughout.
- **TC18:** Seeds independent saved totals at 58, 59, and 60 seconds, reloads them through main, and emits a normal-temperature reading. All nine combinations against 59-second profile limits are checked. Below and equal are not exceeded; above is exceeded. This covers neither, heat only, freeze only, and both exceeded.
- **TC19:** The actual profile file lacks freeze_limit_s. Two readings are still stored, and both comparisons are unknown with unset flags.

```text
Ran 3 tests in 0.333s
OK
```

### Yellow and demonstration

The same isolated harness backs the executable desktop demo and the acceptance tests, avoiding a second simulated implementation of the application. No state or log files are written in the repository. Temporary files are removed after each simulation.

Ran `python3 read_temp/demo_main.py`. Observed highlights:

```text
DESKTOP SIMULATION: real board code, simulated sensor/time, network blocked
Synthetic profile limits: heat 119 s, freeze 120 s
t=240 s temp=4.0 heat=120 s freeze=120 s -> {"status": "compared", "heat_exceeded": true, "freeze_exceeded": false}
t=300 s temp=None heat=120 s freeze=120 s -> {"status": "unknown", "reason": "sensor reading failed", "heat_exceeded": null, "freeze_exceeded": null}
Restored after simulated program restart: {"heat_s": 120, "freeze_s": 120}
Stored 8 readings, including the failed reading; skipped=0
Broken profile -> {"status": "unknown", "reason": "missing freeze_limit_s", "heat_exceeded": null, "freeze_exceeded": null}
```

## Final combined regression verification

All commands were run independently from the repository root after the final pipeline implementation:

```bash
python3 -m unittest discover -s read_temp -p 'test_*.py' -q
python3 -m unittest discover -s exposure -p 'test_*.py' -q
python3 -m unittest discover -s exposure/heat_exposure -p 'test_*.py' -q
python3 -m unittest discover -s vaccine_profile -p 'test_*.py' -q
python3 -m unittest discover -s store_readings -p 'test_*.py' -q
```

```text
read_temp:              Ran 35 tests in 0.344s — OK
exposure:               Ran 57 tests in 0.019s — OK
exposure/heat_exposure: Ran 23 tests in 0.003s — OK
vaccine_profile:        Ran 23 tests in 0.008s — OK
store_readings:         Ran 11 tests in 0.055s — OK
```

**Total:** 149 tests passed. This count includes the newly integrated heat suite. Boundary subtests are included within their parent test, not counted separately.

## Remaining acceptance evidence

### Verification before publishing to main

Fetched origin/main and fast-forwarded from 2f6fed3 to fa10ad8 without conflicts. The remote change updated only the heat test files; the integration files did not overlap. Re-ran all five suites with the commands above:

```text
read_temp:              Ran 35 tests in 0.401s — OK
exposure:               Ran 57 tests in 0.021s — OK
exposure/heat_exposure: Ran 38 tests in 0.006s — OK
vaccine_profile:        Ran 23 tests in 0.006s — OK
store_readings:         Ran 11 tests in 0.074s — OK
```

Total: 164 tests passed. The count increased because main now includes additional heat tests from Aleef.

### Board and acceptance limits

The staged flat-layout subprocess test validates desktop imports and application behavior, not MicroPython execution or physical flash behavior. Run the deployment checklist on Wokwi/ESP32, verify the chosen time source and actual restart/power-loss behavior, and present evidence to the team/Product Owner before claiming final acceptance. Time during a power outage is not counted by the current design. Corrupt state files fall back to a new total under the existing loaders; that policy remains a team/PO question. Storage False is deliberately ignored per Issue 17, so comparison status does not certify that a reading reached storage.
