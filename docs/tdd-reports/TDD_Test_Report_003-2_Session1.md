# TDD Test Report

Smart Cold Box · Sprint 2 · Story 003-2 Store readings locally · Session 1: append_reading() and load_readings()

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 003-2 Store readings locally | ([], 0): no readings, nothing skipped | TC-01 | Missing file gives no readings | Witthayut P. (Pun) | 6 Nov 2026 |
| 003-2 Store readings locally | append_reading() returns True 3 times; load gives the 3 records back in order (a failed read included), 0 skipped (AC1) | TC-02 | Every reading is stored in order | Witthayut P. (Pun) | 6 Nov 2026 |
| 003-2 Store readings locally | No \\r byte in the file; the file ends with }\\n (FORMAT.md section 3) | TC-03 | Lines end with \\n only | Witthayut P. (Pun) | 6 Nov 2026 |
| 003-2 Store readings locally | ([reading 1, reading 2], 1): the half-written line from the power cut is skipped and counted (AC3) | TC-04 | Torn last line is skipped, earlier readings kept | Witthayut P. (Pun) | 6 Nov 2026 |
| 003-2 Store readings locally | append_reading() returns True; load gives ([reading 1, reading 3], 1): reading 3 is kept (AC3) | TC-05 | Reading after a power cut starts a new line | Nattanita E. (Gramma) | 6 Nov 2026 |
| 003-2 Store readings locally | ([reading 1, reading 3], 2): a JSON list and a record without the error key are skipped and counted | TC-06 | Line that is not a reading is skipped | Nattanita E. (Gramma) | 6 Nov 2026 |
| 003-2 Store readings locally | ([reading 1, reading 2], 0): blank lines are not readings and not broken lines | TC-07 | Blank lines are ignored and not counted | Nattanita E. (Gramma) | 6 Nov 2026 |
| 003-2 Store readings locally | False for a path that is a folder; False for a record that cannot be written as JSON; no exception; the file stays empty | TC-08 | Storage problem returns False and never raises | Nattanita E. (Gramma) | 6 Nov 2026 |

*Full test file after the last refactor (all 8 tests in store_readings/test_storage.py):* `Ran 8 tests in 0.021s OK`

## Test Case Number: TC-01

**Test Case Name:** Missing file gives no readings (`test_missing_file_gives_no_readings`)

**Expected output:** ([], 0): no readings, nothing skipped

### Red

Wrote the test before any code. storage.py did not exist yet, so the test module could not even import it.

*Test written first:*

```text
# Tests for on-box reading storage (003-2, store_readings/FORMAT.md).
# No hardware, clock or network: files go in a temporary folder, records are
# plain dicts made up in the test.
import os
import tempfile
import unittest
 
from storage import load_readings
 
 
class StorageTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "readings.jsonl")
 
    def tearDown(self):
        self.dir.cleanup()
 
    def test_missing_file_gives_no_readings(self):
        self.assertEqual(load_readings(self.path), ([], 0))
 
 
if __name__ == "__main__":
    unittest.main()
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_storage ... ERROR
 
========================================
ERROR: test_storage
----------------------------------------
ImportError: Failed to import test module: test_storage
Traceback (most recent call last):
  File "test_storage.py", line 8, in <module>
    from storage import load_readings
ModuleNotFoundError: No module named 'storage'
 
 
----------------------------------------
Ran 1 test in 0.000s
 
FAILED (errors=1)
```

### Green

Smallest code that passes: load_readings() returns an empty list and 0.

*Code in storage.py:*

```text
def load_readings(path):
    return [], 0
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_missing_file_gives_no_readings ... ok
 
----------------------------------------
Ran 1 test in 0.003s
 
OK
```

### Yellow

Added the module header, the READINGS_PATH default and a docstring that states the contract. No logic change; the test still passes.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
 
READINGS_PATH = "readings.jsonl"
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    return [], 0
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_missing_file_gives_no_readings ... ok
 
----------------------------------------
Ran 1 test in 0.003s
 
OK
```

## Test Case Number: TC-02

**Test Case Name:** Every reading is stored in order (`test_every_reading_is_stored_in_order`)

**Expected output:** append_reading() returns True 3 times; load gives the 3 records back in order (a failed read included), 0 skipped (AC1)

### Red

append_reading() did not exist, so the import failed.

*Test written first:*

```text
def reading(seq, temp_c):
    """A good reading, shaped like the records Scheduler emits."""
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": seq,
            "timestamp_s": 1793100000 + 300 * seq, "temp_c": temp_c,
            "ok": True, "error": None}
 
def failed(seq):
    """A failed read: ok is False, temp_c is None, error says why."""
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": seq,
            "timestamp_s": 1793100000 + 300 * seq, "temp_c": None,
            "ok": False, "error": "sensor_timeout"}
 
def test_every_reading_is_stored_in_order(self):
    # AC1: every reading, failed reads too, comes back in the order written.
    records = [reading(1, 4.6), failed(2), reading(3, 5.1)]
    for record in records:
        self.assertTrue(append_reading(record, self.path))
    self.assertEqual(load_readings(self.path), (records, 0))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_storage ... ERROR
 
========================================
ERROR: test_storage
----------------------------------------
ImportError: Failed to import test module: test_storage
Traceback (most recent call last):
  File "test_storage.py", line 8, in <module>
    from storage import append_reading, load_readings
ImportError: cannot import name 'append_reading' from 'storage' (storage.py)
 
 
----------------------------------------
Ran 1 test in 0.000s
 
FAILED (errors=1)
```

### Green

Append json.dumps(record) plus a newline to the file; read the file back and decode each line. A missing file still gives ([], 0).

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
import json
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError:
        return [], 0
    return [json.loads(line) for line in lines], 0
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_missing_file_gives_no_readings ... ok
 
----------------------------------------
Ran 2 tests in 0.005s
 
OK
```

### Yellow

Built the line first and wrote it with one write(), then closed the file in finally: on the box a reading reaches flash when the file is closed. Both tests still pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
import json
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record) + "\n"
    f = open(path, "a")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError:
        return [], 0
    return [json.loads(line) for line in lines], 0
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_missing_file_gives_no_readings ... ok
 
----------------------------------------
Ran 2 tests in 0.005s
 
OK
```

## Test Case Number: TC-03

**Test Case Name:** Lines end with \\n only (`test_lines_end_with_newline_only`)

**Expected output:** No \\r byte in the file; the file ends with }\\n (FORMAT.md section 3)

### Red

The file was opened in text mode, so on Windows every line ended with \\r\\n.

*Test written first:*

```text
def test_lines_end_with_newline_only(self):
    # FORMAT.md section 3: one record per line, "\n" only (no "\r\n" on Windows).
    append_reading(reading(1, 4.6), self.path)
    with open(self.path, "rb") as f:
        raw = f.read()
    self.assertNotIn(b"\r", raw)
    self.assertTrue(raw.endswith(b"}\n"))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... FAIL
test_missing_file_gives_no_readings ... ok
 
========================================
FAIL: test_lines_end_with_newline_only
----------------------------------------
Traceback (most recent call last):
  File "test_storage.py", line 48, in test_lines_end_with_newline_only
    self.assertNotIn(b"\r", raw)
AssertionError: b'\r' unexpectedly found in b'{"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 1, "timestamp_s": 1793100300, "temp_c": 4.6, "ok": true, "error": null}\r\n'
 
----------------------------------------
Ran 3 tests in 0.016s
 
FAILED (failures=1)
```

### Green

Open the file in binary mode: "ab" to append (the line is encoded to bytes) and "rb" to read (each line is decoded).

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
import json
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    try:
        with open(path, "rb") as f:
            lines = f.read().splitlines()
    except OSError:
        return [], 0
    return [json.loads(line.decode()) for line in lines], 0
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
 
----------------------------------------
Ran 3 tests in 0.007s
 
OK
```

### Yellow

Added a header comment that says why files are always opened in binary mode. No logic change; all 3 tests pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    try:
        with open(path, "rb") as f:
            lines = f.read().splitlines()
    except OSError:
        return [], 0
    return [json.loads(line.decode()) for line in lines], 0
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
 
----------------------------------------
Ran 3 tests in 0.013s
 
OK
```

## Test Case Number: TC-04

**Test Case Name:** Torn last line is skipped, earlier readings kept (`test_torn_last_line_is_skipped_and_earlier_readings_kept`)

**Expected output:** ([reading 1, reading 2], 1): the half-written line from the power cut is skipped and counted (AC3)

### Red

A power cut left half a line at the end of the file. json.loads() raised JSONDecodeError, so load_readings() crashed and returned nothing.

*Test written first:*

```text
def write_raw(self, data):
    with open(self.path, "ab") as f:
        f.write(data)
 
def torn_line(self, record):
    """The first half of a line, as left by a power cut during the write."""
    line = json.dumps(record).encode()
    return line[:len(line) // 2]
 
def test_torn_last_line_is_skipped_and_earlier_readings_kept(self):
    # AC3: a power cut can only break the line being written.
    append_reading(reading(1, 4.6), self.path)
    append_reading(reading(2, 4.8), self.path)
    self.write_raw(self.torn_line(reading(3, 5.0)))
    self.assertEqual(load_readings(self.path),
                     ([reading(1, 4.6), reading(2, 4.8)], 1))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ERROR
 
========================================
ERROR: test_torn_last_line_is_skipped_and_earlier_readings_kept
----------------------------------------
Traceback (most recent call last):
  File "test_storage.py", line 66, in test_torn_last_line_is_skipped_and_earlier_readings_kept
    self.assertEqual(load_readings(self.path),
  File "storage.py", line 33, in load_readings
    return [json.loads(line.decode()) for line in lines], 0
json.decoder.JSONDecodeError: Unterminated string starting at: line 1 column 63 (char 62)
 
----------------------------------------
Ran 4 tests in 0.018s
 
FAILED (errors=1)
```

### Green

Catch ValueError for each line (JSONDecodeError is a ValueError) and count the line as skipped.

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    try:
        with open(path, "rb") as f:
            lines = f.read().splitlines()
    except OSError:
        return [], 0
    readings = []
    skipped = 0
    for line in lines:
        try:
            readings.append(json.loads(line.decode()))
        except ValueError:
            skipped += 1
    return readings, skipped
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 4 tests in 0.009s
 
OK
```

### Yellow

Read the file one line at a time with readline() instead of reading it all at once, because the file can be larger than the ESP32's RAM. The file is closed in finally. All 4 tests pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            readings.append(record)
    finally:
        f.close()
    return readings, skipped
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 4 tests in 0.007s
 
OK
```

## Test Case Number: TC-05

**Test Case Name:** Reading after a power cut starts a new line (`test_reading_after_power_cut_starts_a_new_line`)

**Expected output:** append_reading() returns True; load gives ([reading 1, reading 3], 1): reading 3 is kept (AC3)

### Red

The torn line had no newline, so reading 3 was glued onto it. The joined line was not valid JSON, so reading 3 was lost.

*Test written first:*

```text
def test_reading_after_power_cut_starts_a_new_line(self):
    # AC3: the next reading is not glued onto the broken line.
    append_reading(reading(1, 4.6), self.path)
    self.write_raw(self.torn_line(reading(2, 4.8)))
    self.assertTrue(append_reading(reading(3, 5.0), self.path))
    self.assertEqual(load_readings(self.path),
                     ([reading(1, 4.6), reading(3, 5.0)], 1))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... FAIL
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
========================================
FAIL: test_reading_after_power_cut_starts_a_new_line
----------------------------------------
Traceback (most recent call last):
  File "test_storage.py", line 74, in test_reading_after_power_cut_starts_a_new_line
    self.assertEqual(load_readings(self.path),
AssertionError: Tuples differ: ([{'d[122 chars]None}], 1) != ([{'d[122 chars]None}, {'device_id': 'BOX-001', 'shipment_id':[91 chars]], 1)
 
First differing element 0:
[{'de[121 chars]None}]
[{'de[121 chars]None}, {'device_id': 'BOX-001', 'shipment_id':[87 chars]one}]
 
  ([{'device_id': 'BOX-001',
     'error': None,
     'ok': True,
     'seq': 1,
     'shipment_id': 'SHP-1001',
     'temp_c': 4.6,
-    'timestamp_s': 1793100300}],
?                              -
 
+    'timestamp_s': 1793100300},
+   {'device_id': 'BOX-001',
+    'error': None,
+    'ok': True,
+    'seq': 3,
+    'shipment_id': 'SHP-1001',
+    'temp_c': 5.0,
+    'timestamp_s': 1793100900}],
   1)
 
----------------------------------------
Ran 5 tests in 0.011s
 
FAILED (failures=1)
```

### Green

Before writing, read the last byte of the file (size from os.stat(path)[6], then seek and read 1 byte). If it is not a newline, start the new line with one.

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    try:
        size = os.stat(path)[6]
    except OSError:
        size = 0
    if size > 0:
        with open(path, "rb") as last:
            last.seek(size - 1)
            if last.read(1) != b"\n":
                line = b"\n" + line
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            readings.append(record)
    finally:
        f.close()
    return readings, skipped
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 5 tests in 0.009s
 
OK
```

### Yellow

Moved the last-byte check into its own function, \_ends_with_newline(), and added a comment that explains the power-cut case. All 5 tests pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    # A write cut off by a power cut leaves no newline: start a fresh line,
    # so this reading is not glued onto the broken one.
    if not _ends_with_newline(path):
        line = b"\n" + line
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            readings.append(record)
    finally:
        f.close()
    return readings, skipped
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 5 tests in 0.011s
 
OK
```

## Test Case Number: TC-06

**Test Case Name:** Line that is not a reading is skipped (`test_line_that_is_not_a_reading_is_skipped`)

**Expected output:** ([reading 1, reading 3], 2): a JSON list and a record without the error key are skipped and counted

### Red

Both lines were valid JSON, so they were returned as if they were readings: the list [1, 2] and a record missing the error key.

*Test written first:*

```text
def test_line_that_is_not_a_reading_is_skipped(self):
    # Valid JSON but not a reading: not an object, or a key is missing.
    no_error_key = reading(2, 4.8)
    del no_error_key["error"]
    append_reading(reading(1, 4.6), self.path)
    self.write_raw(b"[1, 2]\n" + json.dumps(no_error_key).encode() + b"\n")
    append_reading(reading(3, 5.0), self.path)
    self.assertEqual(load_readings(self.path),
                     ([reading(1, 4.6), reading(3, 5.0)], 2))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... FAIL
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
========================================
FAIL: test_line_that_is_not_a_reading_is_skipped
----------------------------------------
Traceback (most recent call last):
  File "test_storage.py", line 84, in test_line_that_is_not_a_reading_is_skipped
    self.assertEqual(load_readings(self.path),
AssertionError: Tuples differ: ([{'d[124 chars]ne}, [1, 2], {'device_id': 'BOX-001', 'shipmen[214 chars]], 0) != ([{'d[124 chars]ne}, {'device_id': 'BOX-001', 'shipment_id': '[89 chars]], 2)
 
First differing element 0:
[{'de[123 chars]ne}, [1, 2], {'device_id': 'BOX-001', 'shipmen[210 chars]one}]
[{'de[123 chars]ne}, {'device_id': 'BOX-001', 'shipment_id': '[85 chars]one}]
 
  ([{'device_id': 'BOX-001',
     'error': None,
     'ok': True,
     'seq': 1,
     'shipment_id': 'SHP-1001',
     'temp_c': 4.6,
     'timestamp_s': 1793100300},
-   [1, 2],
-   {'device_id': 'BOX-001',
-    'ok': True,
-    'seq': 2,
-    'shipment_id': 'SHP-1001',
-    'temp_c': 4.8,
-    'timestamp_s': 1793100600},
    {'device_id': 'BOX-001',
     'error': None,
     'ok': True,
     'seq': 3,
     'shipment_id': 'SHP-1001',
     'temp_c': 5.0,
     'timestamp_s': 1793100900}],
-  0)
+  2)
 
----------------------------------------
Ran 6 tests in 0.017s
 
FAILED (failures=1)
```

### Green

Keep a line only when it is a dict that has every key in RECORD_KEYS (the record Scheduler emits); otherwise count it as skipped.

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
# The record Scheduler emits: read_temp/scheduler.py RECORD_KEYS. Keep in step.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    # A write cut off by a power cut leaves no newline: start a fresh line,
    # so this reading is not glued onto the broken one.
    if not _ends_with_newline(path):
        line = b"\n" + line
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            if isinstance(record, dict) and all(key in record for key in RECORD_KEYS):
                readings.append(record)
            else:
                skipped += 1
    finally:
        f.close()
    return readings, skipped
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 6 tests in 0.015s
 
OK
```

### Yellow

Moved the check into \_is_reading() and wrote it as a plain loop, so it reads the same on MicroPython and CPython. All 6 tests pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
# The record Scheduler emits: read_temp/scheduler.py RECORD_KEYS. Keep in step.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    # A write cut off by a power cut leaves no newline: start a fresh line,
    # so this reading is not glued onto the broken one.
    if not _ends_with_newline(path):
        line = b"\n" + line
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def _is_reading(record):
    if not isinstance(record, dict):
        return False
    for key in RECORD_KEYS:
        if key not in record:
            return False
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            if _is_reading(record):
                readings.append(record)
            else:
                skipped += 1
    finally:
        f.close()
    return readings, skipped
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 6 tests in 0.015s
 
OK
```

## Test Case Number: TC-07

**Test Case Name:** Blank lines are ignored and not counted (`test_blank_lines_are_ignored_and_not_counted`)

**Expected output:** ([reading 1, reading 2], 0): blank lines are not readings and not broken lines

### Red

Each blank line failed json.loads() and was counted as a broken line, so skipped was 2 instead of 0.

*Test written first:*

```text
def test_blank_lines_are_ignored_and_not_counted(self):
    append_reading(reading(1, 4.6), self.path)
    self.write_raw(b"\n  \n")
    append_reading(reading(2, 4.8), self.path)
    self.assertEqual(load_readings(self.path),
                     ([reading(1, 4.6), reading(2, 4.8)], 0))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_blank_lines_are_ignored_and_not_counted ... FAIL
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
========================================
FAIL: test_blank_lines_are_ignored_and_not_counted
----------------------------------------
Traceback (most recent call last):
  File "test_storage.py", line 91, in test_blank_lines_are_ignored_and_not_counted
    self.assertEqual(load_readings(self.path),
AssertionError: Tuples differ: ([{'d[201 chars]_s': 1793100600, 'temp_c': 4.8, 'ok': True, 'error': None}], 2) != ([{'d[201 chars]_s': 1793100600, 'temp_c': 4.8, 'ok': True, 'error': None}], 0)
 
First differing element 1:
2
0
 
  ([{'device_id': 'BOX-001',
     'error': None,
     'ok': True,
     'seq': 1,
     'shipment_id': 'SHP-1001',
     'temp_c': 4.6,
     'timestamp_s': 1793100300},
    {'device_id': 'BOX-001',
     'error': None,
     'ok': True,
     'seq': 2,
     'shipment_id': 'SHP-1001',
     'temp_c': 4.8,
     'timestamp_s': 1793100600}],
-  2)
+  0)
 
----------------------------------------
Ran 7 tests in 0.014s
 
FAILED (failures=1)
```

### Green

Skip a line that is empty after strip() before decoding it.

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
# The record Scheduler emits: read_temp/scheduler.py RECORD_KEYS. Keep in step.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    # A write cut off by a power cut leaves no newline: start a fresh line,
    # so this reading is not glued onto the broken one.
    if not _ends_with_newline(path):
        line = b"\n" + line
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def _is_reading(record):
    if not isinstance(record, dict):
        return False
    for key in RECORD_KEYS:
        if key not in record:
            return False
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            if not raw.strip():
                continue
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            if _is_reading(record):
                readings.append(record)
            else:
                skipped += 1
    finally:
        f.close()
    return readings, skipped
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_blank_lines_are_ignored_and_not_counted ... ok
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 7 tests in 0.014s
 
OK
```

### Yellow

Added the blank-line rule to the load_readings() docstring. No logic change; all 7 tests pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
# The record Scheduler emits: read_temp/scheduler.py RECORD_KEYS. Keep in step.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    line = json.dumps(record).encode() + b"\n"
    # A write cut off by a power cut leaves no newline: start a fresh line,
    # so this reading is not glued onto the broken one.
    if not _ends_with_newline(path):
        line = b"\n" + line
    f = open(path, "ab")
    try:
        f.write(line)  # one write per reading
    finally:
        f.close()  # the reading reaches flash when the file is closed
    return True
 
 
def _is_reading(record):
    if not isinstance(record, dict):
        return False
    for key in RECORD_KEYS:
        if key not in record:
            return False
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    Blank lines are ignored and not counted. A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            if not raw.strip():
                continue
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            if _is_reading(record):
                readings.append(record)
            else:
                skipped += 1
    finally:
        f.close()
    return readings, skipped
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_blank_lines_are_ignored_and_not_counted ... ok
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 7 tests in 0.017s
 
OK
```

## Test Case Number: TC-08

**Test Case Name:** Storage problem returns False and never raises (`test_storage_problem_returns_false_and_never_raises`)

**Expected output:** False for a path that is a folder; False for a record that cannot be written as JSON; no exception; the file stays empty

### Red

Opening a folder as a file raised PermissionError out of append_reading(). Scheduler does not catch exceptions from emit, so this would stop the box from reading (003-1 AC2).

*Test written first:*

```text
def test_storage_problem_returns_false_and_never_raises(self):
    # Scheduler does not catch exceptions from emit, so a storage problem
    # must not stop the box from reading (003-1 AC2).
    self.assertFalse(append_reading(reading(1, 4.6), self.dir.name))  # a folder, not a file
    self.assertFalse(append_reading({"temp_c": object()}, self.path))  # cannot be written as JSON
    self.assertEqual(load_readings(self.path), ([], 0))
```

*Result: fails*

```text
$ python -m unittest -v test_storage
test_blank_lines_are_ignored_and_not_counted ... ok
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_storage_problem_returns_false_and_never_raises ... ERROR
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
========================================
ERROR: test_storage_problem_returns_false_and_never_raises
----------------------------------------
Traceback (most recent call last):
  File "test_storage.py", line 97, in test_storage_problem_returns_false_and_never_raises
    self.assertFalse(append_reading(reading(1, 4.6), self.dir.name))  # a folder, not a file
  File "storage.py", line 36, in append_reading
    f = open(path, "ab")
PermissionError: [Errno 13] Permission denied: 'C:\\Users\\USER\\AppData\\Local\\Temp\\tmpv_p7wwep'
 
----------------------------------------
Ran 8 tests in 0.014s
 
FAILED (errors=1)
```

### Green

Wrap the whole append in try/except Exception and return False. Exception, not only OSError, because json.dumps() raises TypeError for a value it cannot write.

*Code in storage.py:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
# The record Scheduler emits: read_temp/scheduler.py RECORD_KEYS. Keep in step.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. True means it was stored."""
    try:
        line = json.dumps(record).encode() + b"\n"
        # A write cut off by a power cut leaves no newline: start a fresh line,
        # so this reading is not glued onto the broken one.
        if not _ends_with_newline(path):
            line = b"\n" + line
        f = open(path, "ab")
        try:
            f.write(line)  # one write per reading
        finally:
            f.close()  # the reading reaches flash when the file is closed
        return True
    except Exception:
        return False
 
 
def _is_reading(record):
    if not isinstance(record, dict):
        return False
    for key in RECORD_KEYS:
        if key not in record:
            return False
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    Blank lines are ignored and not counted. A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            if not raw.strip():
                continue
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            if _is_reading(record):
                readings.append(record)
            else:
                skipped += 1
    finally:
        f.close()
    return readings, skipped
```

*Result: passes*

```text
$ python -m unittest -v test_storage
test_blank_lines_are_ignored_and_not_counted ... ok
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_storage_problem_returns_false_and_never_raises ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 8 tests in 0.017s
 
OK
```

### Yellow

Updated the append_reading() docstring to state the contract: it never raises, and False means the reading was not stored. This is the version on GitHub (store_readings/storage.py). All 8 tests pass.

*Code after refactoring:*

```text
# On-box storage for readings (story 003-2). Owners: Pun, Gramma.
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Format: store_readings/FORMAT.md. One reading per line (JSON Lines), appended
# at the end and never rewritten, so a power cut can only break the last line.
# Files are always opened in binary mode, so Windows never writes "\r\n".
import json
import os
 
READINGS_PATH = "readings.jsonl"
 
# The record Scheduler emits: read_temp/scheduler.py RECORD_KEYS. Keep in step.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")
 
 
def _ends_with_newline(path):
    """True when the file is missing, empty, or its last byte is a newline."""
    try:
        size = os.stat(path)[6]
    except OSError:
        return True
    if size == 0:
        return True
    with open(path, "rb") as f:
        f.seek(size - 1)
        return f.read(1) == b"\n"
 
 
def append_reading(record, path=READINGS_PATH):
    """Append one record as one line. Never raises: False means it was not stored."""
    try:
        line = json.dumps(record).encode() + b"\n"
        # A write cut off by a power cut leaves no newline: start a fresh line,
        # so this reading is not glued onto the broken one.
        if not _ends_with_newline(path):
            line = b"\n" + line
        f = open(path, "ab")
        try:
            f.write(line)  # one write per reading
        finally:
            f.close()  # the reading reaches flash when the file is closed
        return True
    except Exception:
        return False
 
 
def _is_reading(record):
    if not isinstance(record, dict):
        return False
    for key in RECORD_KEYS:
        if key not in record:
            return False
    return True
 
 
def load_readings(path=READINGS_PATH):
    """Return (readings, skipped): records in file order, and broken lines skipped.
 
    Blank lines are ignored and not counted. A missing file gives ([], 0).
    """
    readings = []
    skipped = 0
    try:
        f = open(path, "rb")
    except OSError:
        return readings, skipped
    try:
        while True:
            raw = f.readline()  # one line at a time: the file can be larger than RAM
            if not raw:
                break
            if not raw.strip():
                continue
            try:
                record = json.loads(raw.decode())
            except ValueError:  # bad JSON or bad UTF-8, on both runtimes
                skipped += 1
                continue
            if _is_reading(record):
                readings.append(record)
            else:
                skipped += 1
    finally:
        f.close()
    return readings, skipped
```

*Result: still passes*

```text
$ python -m unittest -v test_storage
test_blank_lines_are_ignored_and_not_counted ... ok
test_every_reading_is_stored_in_order ... ok
test_line_that_is_not_a_reading_is_skipped ... ok
test_lines_end_with_newline_only ... ok
test_missing_file_gives_no_readings ... ok
test_reading_after_power_cut_starts_a_new_line ... ok
test_storage_problem_returns_false_and_never_raises ... ok
test_torn_last_line_is_skipped_and_earlier_readings_kept ... ok
 
----------------------------------------
Ran 8 tests in 0.021s
 
OK
```
