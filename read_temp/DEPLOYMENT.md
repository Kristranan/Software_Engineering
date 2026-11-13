# Temperature storage and exposure comparison deployment

`main.py` loads the temperature thresholds and the separate saved heat and
freeze states for `SHIPMENT_ID` at boot. Every Scheduler record is printed as
JSON, appended to readings.jsonl, and passed once to each exposure accumulator.
The returned states are retained in `heat` and `freeze`. Their heat_s and
freeze_s fields use whole seconds.

For a successful reading, Plai's check_exposure loads profile.json and compares
each total with its own allowed duration. The result is kept in
`comparison_result`: status `compared` plus separate heat_exceeded and
freeze_exceeded booleans. Exact equality does not exceed a limit. Before the
first reading, after a failed reading, or when the profile/totals are invalid,
the status is `unknown`, both flags are None, and a reason is recorded.
The next good reading retries comparison. Serial output remains the original
reading JSON; comparison status is not added to the stored reading schema.

## Files on ESP32 or Wokwi

Copy these repository files into the same directory on the board. The imports
in `main.py` use the flat board layout, rather than the repository directories.

| Repository source | Board filename |
| --- | --- |
| `read_temp/main.py` | `main.py` |
| `read_temp/config.py` | `config.py` |
| `read_temp/scheduler.py` | `scheduler.py` |
| `store_readings/storage.py` | `storage.py` |
| `exposure/exposure_limits.py` | `exposure_limits.py` |
| `exposure/exposure_limits.json` | `exposure_limits.json` |
| `exposure/freeze_exposure.py` | `freeze_exposure.py` |
| `exposure/freeze_state.py` | `freeze_state.py` |
| `exposure/heat_exposure/heat_exposure.py` | `heat_exposure.py` |
| `exposure/heat_exposure/heat_state.py` | `heat_state.py` |
| `vaccine_profile/comparison.py` | `comparison.py` |
| `vaccine_profile/profile_loader.py` | `profile_loader.py` |
| `vaccine_profile/profile_check.py` | `profile_check.py` |
| `vaccine_profile/profile.json` | `profile.json` |

Provide `config.json` if a reading interval other than the default is required.
In Wokwi, add the Python and JSON files above as project files and retain the
DHT22 connection to GPIO 4 from `read_temp/diagram.json`.

The program creates readings.jsonl, heat_state.json, and freeze_state.json.
Reuse the state files when restarting the same shipment. Set the correct
SHIPMENT_ID before starting a different shipment; both loaders reject state
from a different shipment. The checked-in profile limits and temperature
thresholds are test/configuration values and require the team's product review.

## Verification on the board

1. Confirm that `main.py` imports successfully and readings appear on serial.
2. Use a test shipment and the configured lower threshold. Keep temperature
   below the threshold for at least two successful readings.
3. After pausing the Scheduler, inspect `freeze["freeze_s"]`, `heat["heat_s"]`,
   and `comparison_result` in the entry-point namespace. Freeze should contain
   the elapsed seconds attributed to cold readings.
4. Warm the sensor above the lower threshold. After the transition interval,
   subsequent warm intervals must leave the freeze total unchanged.
5. Raise temperature above the upper threshold and verify heat grows separately.
   Compare below, exactly at, and above each profile duration; also verify that
   a broken profile or failed sensor reading gives unknown.
6. Restart without removing the state files, using the same shipment ID. Confirm
   both saved totals are restored. Record the board output and the chosen
   timestamp source as evidence. Check readings.jsonl includes failed readings.

The desktop tests simulate a program reload with a temporary state file; they
do not establish physical flash durability or ESP32 execution. The current
time source can restart after a power cut. Time while power is off is not
counted, and non-increasing timestamps add no negative exposure.

## Desktop demonstration and checks

Run from the repository root:

```bash
python3 read_temp/demo_main.py
python3 -m unittest discover -s read_temp -p 'test_*.py' -v
```

The desktop demo stages the actual flat board files in a temporary directory,
simulates sensor/time in isolated CPython, and blocks socket access. It shows
heat, cold, warming, sensor failure, recovery, program reload, and a bad profile.
Its limits of 119 s heat / 120 s freeze are synthetic demonstration values.
It writes no state or readings files in the repository. Do not upload this
desktop-only demo or its tests to the board.

The application uses heat_on_reading and freeze_on_reading exactly once per
record. It does not additionally call update_and_compare, avoiding a second
accumulation path. append_reading's False return is ignored as agreed in
Issue 17; it does not stop the Scheduler. Hardware/Wokwi execution, physical
power-cut durability, and Product Owner acceptance still require evidence.
