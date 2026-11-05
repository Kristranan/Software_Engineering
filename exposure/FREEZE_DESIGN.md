# 004-2 Accumulate freeze exposure: design

Phase 1 of story 004-2. Owner: Sia (Sprint 2 backlog).
Status: **draft**, 4 Nov 2026. Updated 5 Nov: the 004-3 side is agreed with
Shogun and Plai (section 6). Still to agree with Aleef (004-1, same rules for heat).

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
- **For 004-1:** `upper_limit_c` (default 8.0) goes in the same file, as one more
  entry in `DEFAULTS` and `RANGES`. When both exist, `validate()` should also
  check `lower_limit_c < upper_limit_c`.

## 2. How the box adds up time below the limit

Input: the records `Scheduler` emits (`RECORD_KEYS` in `read_temp/scheduler.py`).
Only `timestamp_s`, `temp_c` and `ok` are used. Output: `freeze_s`, whole seconds.

**Rule R1 (proposed): the time between two good readings is counted by the
earlier one.** When a good reading arrives, look at the last good reading before
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

## 4. Functions (proposed)

Same style as `read_temp/` and `alert_depot/`: plain dicts, MicroPython and CPython.

- `freeze_increment_s(last_good, record, lower_limit_c)` → int ≥ 0. Pure: no
  file, no clock. `last_good` is `None` for the first reading.
- `accumulate_freeze(state, record, lower_limit_c)` → new state
  `{"freeze_s": int, "last_good": record or None}`. Pure.

004-1 could mirror these as `heat_increment_s` and `accumulate_heat`. Keeping
heat and freeze in two functions makes AC1 hold by construction.

## 5. Not in 004-2

- Comparing `freeze_s` with the vaccine's allowed freeze time: 004-3.
- Remaining buffer: 004-4.
- Storing the readings themselves: 003-2 (`store_readings/FORMAT.md`).

## 6. Agreed with Shogun and Plai (004-3), 5 Nov 2026

- `freeze_s` is a whole number of **seconds**. 004-3 keeps its freeze limit in
  seconds too, so nothing is converted to minutes and no precision is lost.
- 004-3 takes `heat_s` and `freeze_s` as two separate numbers and compares each
  with its own limit (heat limit, freeze limit). They are never added together
  and never cancel each other.
- `freeze_s` never going down matches AC2: warming later does not remove freeze
  exposure that is already counted.

## 7. Open questions

1. **Aleef (004-1):** Same file and key names (`lower_limit_c`, `upper_limit_c`)?
   Same time rule R1 for heat? The two totals must be counted the same way,
   because 004-3 compares both.
2. **Aleef (004-1):** How does 004-1 keep its total across a power cut (004-1
   AC2)? `freeze_s` must survive a restart too. Starting again from 0 would erase
   a freeze event, which goes against AC2. 004-2 will use the same method.
3. **Product Owner (through Aleef):** Does "freeze" mean below 2 °C (the
   bottom of the profile), or below a freezing point such as 0 °C? The AC says
   "lower threshold", so the default is 2.0. Either way it changes in the file,
   not the code.
4. **Long gaps:** With R1, a 2-hour sensor failure after a cold reading counts
   as 2 hours of freeze. Is that right (safe side), or should long gaps go to
   007-2 "unknown" instead?
5. **Time source after a power cut (Aleef and the team).** Not decided yet
   (Shogun, 5 Nov). The earlier prototype used `ticks_ms()`, which restarts after
   a power cut, so it cannot stand for real time that continues across one. The
   team still has to choose where the box gets its time from and how it recovers
   the time after a restart (Plai's agreement, item 1). Until then, R1 adds 0
   when time goes backwards, and the time while the power was off is not counted.
