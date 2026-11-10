# 003-2 Store readings locally: on-box storage format

Phase 1 of story 003-2 (issue #12). Owners: Pun, Gramma (Sprint 2 backlog).
Status: **agreed** by Pun and Gramma, 4 Nov 2026.

Acceptance criteria of 003-2:
- AC1. Every reading is written to on-box storage.
- AC2. Storage holds at least one full transit cycle.
- AC3. Readings survive power interruption.

## 1. What is stored

One reading = the record that `Scheduler` already emits (`read_temp/scheduler.py`,
`RECORD_KEYS`). 003-2 stores it as it is: no new fields, no renamed fields.

| Key | Type | Example |
|---|---|---|
| `device_id` | string | `"BOX-001"` |
| `shipment_id` | string | `"SHP-1001"` |
| `seq` | int, restarts at 1 on every boot | `12` |
| `timestamp_s` | int, whole seconds | `1793100000` |
| `temp_c` | number, or `null` when the read failed | `4.6` |
| `ok` | bool | `true` |
| `error` | string: the exception message, or its class name if the message is empty; `null` when the read worked | `"sensor_timeout"` |

Failed reads are stored too (`ok: false`), so 003-1's "failed reads are logged"
also holds after a power cut.

## 2. File format

- One file on the box: `readings.jsonl` (constant `READINGS_PATH`).
- **JSON Lines**: one record per line, written as `json.dumps(record)` followed
  by `"\n"`, encoded as UTF-8. Key order is not part of the format (MicroPython
  dicts do not keep it); readers use the keys.
- New readings are **appended** at the end. The file is never rewritten.

Example file:

```
{"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 1, "timestamp_s": 1793100000, "temp_c": 4.6, "ok": true, "error": null}
{"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 2, "timestamp_s": 1793100300, "temp_c": null, "ok": false, "error": "sensor_timeout"}
```

Why append and not rewrite (like `read_temp/config.py` does): the config file is
tiny and rarely changes, but this file grows every `interval_s`. Rewriting it on
every reading gets slower as it grows and wears the flash.

## 3. Writing and reading

**Files are always opened in binary mode** (`"ab"` to append, `"rb"` to read).
Text mode is not used: on Windows it writes `\r\n`, and CPython does not allow
seeking from the end of a text file.

### Writing one reading: `append_reading`

1. Build `line = json.dumps(record).encode() + b"\n"`.
2. If the file exists and is not empty, read its last byte: size from
   `os.stat(path)[6]`, then open `"rb"`, `seek(size - 1)`, `read(1)`.
   If that byte is not `b"\n"`, the last write was cut off: the new line starts
   with `b"\n"`, so it is not glued onto the broken one.
3. Open the file with `"ab"`, write the line with **one** `write()`, and
   **close** the file. A reading counts as stored only after `close()` succeeds:
   on the box, data reaches flash when the file is closed.

The check in step 2 runs **before every append**, not only after boot. This keeps
the function stateless, and it also covers a write that failed part-way during
the same boot (for example, when the flash is full).

Not used, because one of the two runtimes lacks them: `os.fsync` (missing on
MicroPython) and `os.sync` (missing in CPython on Windows). Opening `"a+"` is not
used either.

### Reading back: `load_readings`

- Read the file with `"rb"` and split it into lines.
- A blank line is ignored and **not** counted.
- A line is **skipped and counted** when it cannot be decoded (UTF-8 or JSON),
  is not a JSON object, or does not have all `RECORD_KEYS`. Catch `ValueError`:
  on both runtimes it covers JSON errors and UTF-8 decode errors.
- A skipped line is never raised as an error.

## 4. Power cuts (AC3)

With the rules in section 3, a power cut can only damage the line being written
at that moment. It may leave a half-written line, a torn UTF-8 character, or
(on FAT) zero bytes at the end of the file. Reading back skips that line, and
the next append starts on a new line. Every earlier line is already complete
and closed, so it is kept.

## 5. Size (AC2)

On the examples in section 2, one line (with `"\n"`) is 131–145 bytes. A
5-digit `seq` with a real sensor error such as `"[Errno 110] ETIMEDOUT"` gives
156 bytes. The error string has no length limit, so plan with **160 bytes**
(1 KB = 1000 bytes below).

Readings per hour = 3600 ÷ `interval_s` (`interval_s` is 10–3600 s, default 300 s).

| `interval_s` | Per hour | 24 h trip | 48 h trip | 72 h trip |
|---|---|---|---|---|
| 300 s (default) | 1.9 KB | 46 KB | 92 KB | 138 KB |
| 60 s | 9.6 KB | 230 KB | 461 KB | 691 KB |
| 10 s (minimum) | 57.6 KB | 1.4 MB | 2.8 MB | 4.1 MB |

A 4 MB ESP32 running MicroPython has a file system of about 2 MB, so the last
two cells of the 10 s row would not fit. The real free space still has to be
checked on the ESP32 in Wokwi (Phase 2).

**One full transit cycle is up to 72 hours** (#16). 72 h is 259,200 s, so a
trip stores 259,200 ÷ `interval_s` readings, at 160 bytes each:

- At 300 s (default): 864 readings, about 138 KB. Fits.
- At 21 s: 12,343 readings, about 1.97 MB. Just fits in about 2 MB.
- Below about 21 s (down to the 10 s minimum): does not fit. At 10 s a trip
  needs about 4.1 MB.

So AC2 holds for any `interval_s` of about 21 s or more, not only for the
300 s default. The exact limit depends on the real free space (open
question 4).

## 6. Functions (proposed)

Runs on ESP32 MicroPython and desktop CPython, like `read_temp/config.py`:
plain dicts and lists, no dataclasses, no typing module.

- `append_reading(record, path=READINGS_PATH)` → `True` when the line is
  written and the file closed; `False` otherwise. It **catches every
  `Exception`** (not only `OSError`: `json.dumps` can raise `TypeError`), so a
  storage problem can never stop the box from reading (003-1 AC2).
  `Scheduler` does not catch exceptions from `emit`, so this matters.
- `load_readings(path=READINGS_PATH)` → `(readings, skipped)`: the list of
  records in file order, and how many broken lines were skipped. A missing
  file gives `([], 0)`.

The file path is a parameter, so tests use a temporary folder, like
`read_temp/test_config.py`. No real clock or hardware is needed in tests.

## 7. How readings arrive

`Scheduler` calls `emit(record)` for every reading. `read_temp/main.py` defines
`emit()`. To store readings, `emit()` also calls `append_reading(record)`. Until
open question 2 is answered, `emit()` ignores the `False` return.

`main.py` is Shogun's file, so this change is agreed with Shogun and made by him.
`scheduler.py` does not change.

## 8. Not in 003-2

- Deleting or rotating old readings, and sending them to the depot: that is the
  sync story, not in the backlog yet.
- Whether the 007-1 alert queue should also survive a power cut is already open
  question 3 in `docs/decisions-and-open-questions.md`. It is not one of the
  003-2 acceptance criteria.

## 9. Open questions

1. **How long is one full transit cycle?** Answered in #16: up to 72 hours
   (rural clinic deliveries when rainy-season roads are closed). Waiting for
   the Product Owner to confirm.
2. **Storage full:** `append_reading` returns `False`. Should the box also show
   or send something? Not in the acceptance criteria.
3. **`seq` after a reboot:** it starts again at 1, so the same `seq` can appear
   twice in one file. After a power cut, `timestamp_s` may restart too, because
   the box has no battery-backed clock and is offline. File order is the only
   reliable order. Should `seq` keep counting across reboots
   (`read_temp/scheduler.py` notes this needs 003-2)?
4. **Shortest interval for a 72-hour trip:** `read_temp/config.py` allows
   `interval_s` from 10 s, but below about 21 s the file fills up before a
   72-hour trip ends (section 5). Should the box stop users from setting a
   shorter interval? For the Product Owner, through Aleef (asked in #16).
   Nothing is changed until this is answered.
