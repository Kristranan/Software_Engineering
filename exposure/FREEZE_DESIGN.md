# 004-2 Accumulate freeze exposure: design

Phase 1 of story 004-2. Owner: Sia (Sprint 2 backlog).
Status: **agreed**, 5 Nov 2026, with Aleef (004-1) and with Shogun and Plai
(004-3). See section 6. Still open: the questions in section 7.

Acceptance criteria of 004-2:
- AC1. Time below the lower threshold accumulates separately from heat.
- AC2. Freeze events are not offset by later warming.

## 1. The lower limit (done in this phase)

- Key `lower_limit_c` in `exposure/exposure_limits.json`, loaded by
  `exposure/exposure_limits.py`. Default **2.0 °C**: the bottom of the 2–8 °C
  vaccine profile in the temperature data format agreement (Sprint 1).
- "Below" means **strictly less than**: 2.0 is not freeze, 1.9 is. This is the
  same rule as A1 in `docs/decisions-and-open-questions.md`.
- Any number from −40 to 80 °C (the DHT22 range), decimals allowed.
- Not in `read_temp/config.py`: `config.load()` falls back to defaults for the
  whole file when one key is bad, so a typo in a limit would also reset
  `interval_s`. Adding a key there would also break `test_save_then_load_roundtrip`.
- `load()` never raises: a bad key falls back to its own default, so the box keeps
  counting. `save()` is strict and rejects unknown keys (a typo such as
  `lower_limt_c`).
- **004-1 (agreed with Aleef):** Aleef adds `upper_limit_c` (default 8.0) to the
  same file, as one more entry in `DEFAULTS` and `RANGES`, plus a check that
  `lower_limit_c < upper_limit_c`.

## 2. How the box adds up time below the limit

Input: the records `Scheduler` emits (`RECORD_KEYS` in `read_temp/scheduler.py`).
Only `timestamp_s`, `temp_c` and `ok` are used. Output: `freeze_s`, whole seconds.

**Rule R1 (agreed, also used for heat in 004-1): the time between two good
readings is counted by the earlier one.** When a good reading arrives, look at the last good reading before
it. If that one was below `lower_limit_c`, add the time between them to
`freeze_s`. In other words: a temperature is assumed to hold until the next
reading. This needs only the last good reading, not the whole history, which is
also how `detect_risk` uses the previous snapshot in 007-1.

Example, `interval_s` = 300, `lower_limit_c` = 2.0:

| `timestamp_s` | `temp_c` | Last good reading below 2.0? | Added | `freeze_s` |
|---|---|---|---|---|
| 0 | 4.0 | (first reading) | 0 | 0 |
| 300 | 1.5 | no (4.0) | 0 | 0 |
| 600 | 0.5 | yes (1.5) | 300 | 300 |
| 900 | 3.0 | yes (0.5) | 300 | 600 |
| 1200 | 9.0 | no (3.0) | 0 | 600 |
| 1500 | 4.0 | no (9.0) | 0 | **600** |

At 1200 the box is too warm. That time goes to the heat total (004-1), and
`freeze_s` stays 600. Getting warm, or coming back to 2–8 °C, never lowers it (AC2).

## 3. Rules that make AC1 and AC2 hold

- **Separate (AC1).** `freeze_s` is its own number. Heat is `heat_s` (004-1).
  The freeze code never reads or writes `heat_s`, and the heat code never touches
  `freeze_s`. 004-3 compares each one to its own limit, and never adds them
  together or lets one cancel the other (agreed, section 6).
- **Never goes down (AC2).** The only change to `freeze_s` is adding a number
  that is 0 or more. There is no code path that subtracts or resets it during a
  shipment.
- **Failed read** (`ok: false`, `temp_c: null`): adds nothing and does not
  become the "last good reading". The gap is counted when the next good reading
  arrives, by the last good reading before the failure. A failed read is never
  treated as "not frozen" (Plai's agreement, item 7: unknown is never safe).
- **Time going backwards or standing still** (same `timestamp_s`, or the clock
  restarts after a power cut because the box has no RTC): add 0, never a
  negative number. Then carry on from the new reading.

## 4. Functions (in `exposure/freeze_exposure.py`)

Same style as `read_temp/` and `alert_depot/`: plain dicts, MicroPython and CPython.
All of them are pure: no file, no clock.

- `freeze_increment_s(last_good, record, lower_limit_c)` → int ≥ 0. **Done.**
  `last_good` is `None` for the first reading.
- `new_freeze_state()` → `{"freeze_s": 0, "last_good": None}`. **Done.**
- `accumulate_freeze(state, record, lower_limit_c)` → a new state
  `{"freeze_s": int, "last_good": record or None}`. **Done.** It never changes
  the `state` it is given. `state` can be `None` when nothing is saved yet.
  Only a good reading becomes `last_good`.

004-1 mirrors these as `heat_increment_s` (done, in `exposure/heat_exposure/`)
and `accumulate_heat`. Keeping heat and freeze in two functions makes AC1 hold
by construction.

### Saving the total across a power cut (`exposure/freeze_state.py`)

Without this, a power cut would restart `freeze_s` at 0 and erase a freeze
event, which goes against AC2.

- **One small file per total.** `freeze_state.json` holds only
  `{"freeze_s", "last_good"}`. Heat would get its own file (`heat_state.json`),
  so the two totals never share a file (AC1) and Aleef and Sia never edit the
  same code.
- **Saved after every reading, rewritten whole.** It is written to a `.tmp`
  file first and then renamed over the old one, the same way as
  `exposure_limits.save()`, so a power cut during a save leaves the old state.
  The readings log (003-2) appends one line per reading because it keeps every
  reading. The total is a single value, so rewriting a small file keeps it the
  same size for the whole trip. Binary mode, like `storage.py`.
- `save_freeze_state(state, path)` → True / False. **Never raises**, so a flash
  problem never stops the box from counting.
- `load_freeze_state(shipment_id, path)` → the saved state, or `None` to start
  a new total. **Never raises.** `None` when there is no file, the file is
  broken or not a freeze state, or it was saved during **another shipment**
  (a new shipment always starts at 0).
- `freeze_on_reading(state, record, lower_limit_c, path)` →
  `accumulate_freeze()` + `save_freeze_state()`, returns the new state.

**For Shogun (`read_temp/main.py`):**

```python
from exposure_limits import load as load_limits
from freeze_state import load_freeze_state, freeze_on_reading

# at boot
limits = load_limits()
freeze = load_freeze_state(shipment_id)        # None = start at 0

# in emit(), for every record from the Scheduler
freeze = freeze_on_reading(freeze, record, limits["lower_limit_c"])
# 004-3 reads freeze["freeze_s"]
```

## 5. Not in 004-2

- Comparing `freeze_s` with the vaccine's allowed freeze time: 004-3.
- Remaining buffer: 004-4.
- Storing the readings themselves: 003-2 (`store_readings/FORMAT.md`).

## 6. Agreed, 5 Nov 2026

### With Aleef (004-1)

- **One config file.** Both limits live in `exposure/exposure_limits.json`.
  Aleef adds `upper_limit_c` (default 8.0) to `DEFAULTS` and `RANGES` in
  `exposure_limits.py`, with a check that `lower_limit_c < upper_limit_c`.
- **Same time rule.** Heat uses R1 too: the time between two good readings is
  counted by the earlier one. Failed reads (`ok: false`) and time going
  backwards add nothing.
- **Totals survive a power cut.** `heat_s` is saved to a file on the flash, in
  the same style as 003-2's storage, so it is not lost after a power cut.
  `freeze_s` is saved the same way.

### With Shogun and Plai (004-3)

- `freeze_s` is a whole number of **seconds**. 004-3 keeps its freeze limit in
  seconds too, so nothing is converted to minutes and no precision is lost.
- 004-3 takes `heat_s` and `freeze_s` as two separate numbers and compares each
  with its own limit (heat limit, freeze limit). They are never added together
  and never cancel each other.
- `freeze_s` never going down matches AC2: warming later does not remove freeze
  exposure that is already counted.

## 7. Open questions

1. **Saving the totals (Aleef):** Freeze now uses its own file,
   `freeze_state.json`, saved after every reading (section 4). Can heat do the
   same with `heat_state.json`? Then `heat_s` and `freeze_s` are saved the same
   way, as agreed on 5 Nov.
2. **Product Owner (through Aleef):** Does "freeze" mean below 2 °C (the
   bottom of the profile), or below a freezing point such as 0 °C? The AC says
   "lower threshold", so the default is 2.0. Either way it changes in the file,
   not the code.
3. **Long gaps:** With R1, a 2-hour sensor failure after a cold reading counts
   as 2 hours of freeze. Is that right (safe side), or should long gaps go to
   007-2 "unknown" instead?
4. **Time source after a power cut (Aleef and the team).** Not decided yet
   (Shogun, 5 Nov). The earlier prototype used `ticks_ms()`, which restarts after
   a power cut, so it cannot stand for real time that continues across one. The
   team still has to choose where the box gets its time from and how it recovers
   the time after a restart (Plai's agreement, item 1). Until then, R1 adds 0
   when time goes backwards, and the time while the power was off is not counted.
5. **Broken state file:** If `freeze_state.json` is broken (not just missing),
   the box starts again at 0. This should almost never happen, because saves go
   through a `.tmp` file. Should it also mark the shipment "unknown" (007-2)?
