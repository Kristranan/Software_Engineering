# TDD Test Report

Smart Cold Box · Sprint 2 · Story 003-2 Store readings locally · Session 2 (Gramma): Scheduler end to end (TC-12, TC-13, TC-14)

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 003-2 Store readings locally | All 3 records from Scheduler are in the file, in order (seq 1, 2, 3); the failed read is stored with ok false and error "sensor_timeout"; 0 skipped (AC1) | TC-13 | End to end, every reading is stored | Nattanita E. (Gramma) | 10 Nov 2026 |
| 003-2 Store readings locally | The 2 readings before the power cut are kept; the half-written 3rd line is skipped (1 skipped); the first reading after the reboot is on its own new line (AC3) | TC-14 | Power cut during a run keeps earlier readings | Nattanita E. (Gramma) | 10 Nov 2026 |
| 003-2 Store readings locally | A full 72-hour trip at the default 300 s is 864 readings; with every read failed (the longest lines) the file is at most 864 × 160 = 138,240 bytes (the plan) and less than the 2,080,768 bytes free on the box; all 864 load back, 0 skipped (AC2) | TC-12 | A 72-hour trip fits | Nattanita E. (Gramma) | 11 Nov 2026 |

*Full test run after the last refactor (3 tests in store_readings/test_store_end_to_end.py, 8 in store_readings/test_storage.py):* `Ran 11 tests in 0.153s OK`

*read_temp tests still pass after this session:* `Ran 24 tests OK`

*TC-12 (AC2, a 72-hour trip fits) was added on 11 Nov 2026, using the free space Pun measured on the ESP32 in Wokwi (2,080,768 bytes, Pun's Session 2 report, #13).*

## Test Case Number: TC-13

**Test Case Name:** End to end, every reading is stored (`test_tc13_every_reading_from_scheduler_is_stored_in_order`)

**Expected output:** All 3 records from Scheduler are in the file, in order (seq 1, 2, 3); the failed read is stored with ok false and error "sensor_timeout"; 0 skipped (AC1)

### Red

Wrote the test first, in a new file. It runs the real Scheduler (read_temp/scheduler.py) with a fake sensor (4.6, then a sensor_timeout error, then 5.1) and a fake clock, and its emit() calls append_reading(), as main.py will (FORMAT.md section 7).

storage.py from Session 1 already stores every record, so the test passed at once. To show that the test can fail, it was run once against a copy of storage.py in which append_reading() returns True without writing anything (one line marked RED CHECK ONLY). The file stayed empty, so the test failed.

*Test written first (store_readings/test_store_end_to_end.py):*

```text
# End-to-end tests for 003-2: Scheduler (read_temp/scheduler.py) emits each
# reading straight into append_reading, then the file is read back.
# No hardware, real clock or network: fake sensor, fake clock, temporary folder.
import os
import sys
import tempfile
import unittest
 
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "read_temp"))
 
from scheduler import Scheduler  # noqa: E402
from storage import append_reading, load_readings  # noqa: E402
 
 
class FakeSensor:
    """Returns the given values in order; an exception in the list is raised."""
 
    def __init__(self, values):
        self.values = list(values)
 
    def read(self):
        value = self.values.pop(0)
        if isinstance(value, Exception):
            raise value
        return value
 
 
class FakeTime:
    """A clock that only moves when sleep() is called."""
 
    def __init__(self, start=1793100000):
        self.now = start
 
    def clock(self):
        return self.now
 
    def sleep(self, seconds):
        self.now += seconds
 
 
class StoreEndToEndTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "readings.jsonl")
        # No config file in the folder: Scheduler uses the default interval (300 s).
        self.config_path = os.path.join(self.dir.name, "config.json")
        self.time = FakeTime()
        self.emitted = []
 
    def tearDown(self):
        self.dir.cleanup()
 
    def emit(self, record):
        """What main.py's emit() does for 003-2 (FORMAT.md section 7): store it."""
        self.emitted.append(record)
        append_reading(record, self.path)
 
    def make(self, values):
        return Scheduler(FakeSensor(values).read, self.emit, "BOX-001", "SHP-1001",
                         clock=self.time.clock, sleep=self.time.sleep,
                         config_path=self.config_path)
 
    def test_tc13_every_reading_from_scheduler_is_stored_in_order(self):
        # TC-13 (AC1): 3 reads, the second one fails. All 3 are in the file, in order.
        self.make([4.6, Exception("sensor_timeout"), 5.1]).run(max_reads=3)
 
        readings, skipped = load_readings(self.path)
        self.assertEqual(skipped, 0)
        self.assertEqual(readings, self.emitted)
        self.assertEqual([r["seq"] for r in readings], [1, 2, 3])
        self.assertEqual([r["timestamp_s"] for r in readings],
                         [1793100000, 1793100300, 1793100600])
        self.assertEqual([r["ok"] for r in readings], [True, False, True])
        self.assertEqual([r["temp_c"] for r in readings], [4.6, None, 5.1])
        self.assertEqual(readings[1]["error"], "sensor_timeout")
 
 
if __name__ == "__main__":
    unittest.main()
```

*Result: fails (storage switched off)*

```text
$ python -m unittest -v test_store_end_to_end
test_tc13_every_reading_from_scheduler_is_stored_in_order ... FAIL
 
========================================
FAIL: test_tc13_every_reading_from_scheduler_is_stored_in_order
----------------------------------------
Traceback (most recent call last):
  File "test_store_end_to_end.py", line 69, in test_tc13_every_reading_from_scheduler_is_stored_in_order
    self.assertEqual(readings, self.emitted)
AssertionError: Lists differ: [] != [{'device_id': 'BOX-001', 'shipment_id': '[363 chars]one}]
 
Second list contains 3 additional elements.
First extra element 0:
{'device_id': 'BOX-001', 'shipment_id': 'SHP-1001', 'seq': 1, 'timestamp_s': 1793100000, 'temp_c': 4.6, 'ok': True, 'error': None}
 
- []
+ [{'device_id': 'BOX-001',
+   'error': None,
+   'ok': True,
+   'seq': 1,
+   'shipment_id': 'SHP-1001',
+   'temp_c': 4.6,
+   'timestamp_s': 1793100000},
+  {'device_id': 'BOX-001',
+   'error': 'sensor_timeout',
+   'ok': False,
+   'seq': 2,
+   'shipment_id': 'SHP-1001',
+   'temp_c': None,
+   'timestamp_s': 1793100300},
+  {'device_id': 'BOX-001',
+   'error': None,
+   'ok': True,
+   'seq': 3,
+   'shipment_id': 'SHP-1001',
+   'temp_c': 5.1,
+   'timestamp_s': 1793100600}]
 
----------------------------------------
Ran 1 test in 0.005s
 
FAILED (failures=1)
```

### Green

Ran the same test against the real storage.py. No change to storage.py or scheduler.py was needed: Scheduler emits every read, failed reads too, and append_reading() writes each one as one line.

*Code in storage.py (unchanged from Session 1; the function TC-13 uses):*

```text
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
```

*Result: passes*

```text
$ python -m unittest -v test_store_end_to_end
test_tc13_every_reading_from_scheduler_is_stored_in_order ... ok
 
----------------------------------------
Ran 1 test in 0.004s
 
OK
```

### Yellow

No refactoring at this step. The copied fakes (FakeSensor, FakeTime) are cleaned up after TC-14.

## Test Case Number: TC-14

**Test Case Name:** Power cut during a run keeps earlier readings (`test_tc14_power_cut_during_a_run_keeps_earlier_readings`)

**Expected output:** The 2 readings before the power cut are kept; the half-written 3rd line is skipped (1 skipped); the first reading after the reboot is on its own new line (AC3)

### Red

Wrote the test first. emit_with_power_cut_on(3) stores the first 2 readings, writes half of the 3rd line and then raises PowerCut, so run() stops in the middle of a write, like the box losing power. A new Scheduler on the same file is the next boot (seq starts at 1 again). make() now takes an optional emit, and import json was added at the top.

storage.py already handles a torn last line (TC-05), so the test passed at once. To show that the test can fail, it was run once against a copy of storage.py in which \_ends_with_newline() always returns True (one line marked RED CHECK ONLY). The first reading after the reboot was glued onto the torn line and lost, so the test failed.

*Test written first (new parts of store_readings/test_store_end_to_end.py):*

```text
class PowerCut(Exception):
    """The box loses power: nothing after this runs until the next boot."""
 
 
    def make(self, values, emit=None):
        return Scheduler(FakeSensor(values).read, emit or self.emit, "BOX-001", "SHP-1001",
                         clock=self.time.clock, sleep=self.time.sleep,
                         config_path=self.config_path)
 
    def emit_with_power_cut_on(self, cut_at):
        """emit() that loses power while writing reading number cut_at.
 
        Half of that line reaches the file, then the run stops (PowerCut),
        like the box dying in the middle of a write.
        """
        calls = []
 
        def emit(record):
            calls.append(record)
            if len(calls) < cut_at:
                self.emit(record)
                return
            line = json.dumps(record).encode()
            with open(self.path, "ab") as f:
                f.write(line[:len(line) // 2])
            raise PowerCut()
 
        return emit
 
    def test_tc14_power_cut_during_a_run_keeps_earlier_readings(self):
        # TC-14 (AC3): power is lost while the 3rd reading is being written.
        with self.assertRaises(PowerCut):
            self.make([4.6, 4.8, 5.0, 5.2],
                      emit=self.emit_with_power_cut_on(3)).run(max_reads=4)
        before_cut = list(self.emitted)
        self.assertEqual(len(before_cut), 2)
 
        # Next boot: a new Scheduler on the same file (seq starts at 1 again).
        self.make([3.9]).run(max_reads=1)
        after_boot = self.emitted[2]
 
        # Earlier readings are kept, the torn line is skipped, the new one is stored.
        readings, skipped = load_readings(self.path)
        self.assertEqual(readings, before_cut + [after_boot])
        self.assertEqual(skipped, 1)
        self.assertEqual(after_boot["seq"], 1)
 
        # The new reading is on its own line, not glued onto the torn one.
        with open(self.path, "rb") as f:
            lines = f.read().split(b"\n")
        self.assertEqual(lines[-1], b"")  # the file ends with a newline
        self.assertEqual(len(lines), 5)   # 2 kept, 1 torn, 1 new, then ""
        self.assertEqual(json.loads(lines[3].decode()), after_boot)
```

*Result: fails (power-cut check switched off)*

```text
$ python -m unittest -v test_store_end_to_end
test_tc13_every_reading_from_scheduler_is_stored_in_order ... ok
test_tc14_power_cut_during_a_run_keeps_earlier_readings ... FAIL
 
========================================
FAIL: test_tc14_power_cut_during_a_run_keeps_earlier_readings
----------------------------------------
Traceback (most recent call last):
  File "test_store_end_to_end.py", line 116, in test_tc14_power_cut_during_a_run_keeps_earlier_readings
    self.assertEqual(readings, before_cut + [after_boot])
AssertionError: Lists differ: [{'de[253 chars]None}] != [{'de[253 chars]None}, {'device_id': 'BOX-001', 'shipment_id':[87 chars]one}]
 
Second list contains 1 additional elements.
First extra element 2:
{'device_id': 'BOX-001', 'shipment_id': 'SHP-1001', 'seq': 1, 'timestamp_s': 1793100600, 'temp_c': 3.9, 'ok': True, 'error': None}
 
  [{'device_id': 'BOX-001',
    'error': None,
    'ok': True,
    'seq': 1,
    'shipment_id': 'SHP-1001',
    'temp_c': 4.6,
    'timestamp_s': 1793100000},
   {'device_id': 'BOX-001',
    'error': None,
    'ok': True,
    'seq': 2,
    'shipment_id': 'SHP-1001',
    'temp_c': 4.8,
-   'timestamp_s': 1793100300}]
?                             ^
 
+   'timestamp_s': 1793100300},
?                             ^
 
+  {'device_id': 'BOX-001',
+   'error': None,
+   'ok': True,
+   'seq': 1,
+   'shipment_id': 'SHP-1001',
+   'temp_c': 3.9,
+   'timestamp_s': 1793100600}]
 
----------------------------------------
Ran 2 tests in 0.006s
 
FAILED (failures=1)
```

### Green

Ran the same tests against the real storage.py. No change to storage.py: before every append, \_ends_with_newline() reads the last byte, and after the power cut it is not a newline, so the new reading starts on a fresh line. load_readings() skips the torn line and counts it.

*Code in storage.py (unchanged from Session 1; the check TC-14 relies on):*

```text
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
```

*Result: passes*

```text
$ python -m unittest -v test_store_end_to_end
test_tc13_every_reading_from_scheduler_is_stored_in_order ... ok
test_tc14_power_cut_during_a_run_keeps_earlier_readings ... ok
 
----------------------------------------
Ran 2 tests in 0.005s
 
OK
```

### Yellow

FakeSensor and FakeTime were copies of the fakes in read_temp/test_scheduler.py. They are now imported from there, so the 003-1 and 003-2 tests use the same fakes and stay in step with Scheduler. FakeTime(start=1793100000) keeps the timestamps the same as in test_storage.py. Both tests still pass.

*Code after refactoring (store_readings/test_store_end_to_end.py):*

```text
# End-to-end tests for 003-2: Scheduler (read_temp/scheduler.py) emits each
# reading straight into append_reading, then the file is read back.
# No hardware, real clock or network: fake sensor, fake clock, temporary folder.
import json
import os
import sys
import tempfile
import unittest
 
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "read_temp"))
 
from scheduler import Scheduler  # noqa: E402
from storage import append_reading, load_readings  # noqa: E402
# The same fakes as the 003-1 Scheduler tests, so both stay in step with Scheduler.
from test_scheduler import FakeSensor, FakeTime  # noqa: E402
 
 
class PowerCut(Exception):
    """The box loses power: nothing after this runs until the next boot."""
 
 
class StoreEndToEndTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "readings.jsonl")
        # No config file in the folder: Scheduler uses the default interval (300 s).
        self.config_path = os.path.join(self.dir.name, "config.json")
        self.time = FakeTime(start=1793100000)
        self.emitted = []
 
    def tearDown(self):
        self.dir.cleanup()
 
    def emit(self, record):
        """What main.py's emit() does for 003-2 (FORMAT.md section 7): store it."""
        self.emitted.append(record)
        append_reading(record, self.path)
 
    def make(self, values, emit=None):
        return Scheduler(FakeSensor(values).read, emit or self.emit, "BOX-001", "SHP-1001",
                         clock=self.time.clock, sleep=self.time.sleep,
                         config_path=self.config_path)
 
    def emit_with_power_cut_on(self, cut_at):
        """emit() that loses power while writing reading number cut_at.
 
        Half of that line reaches the file, then the run stops (PowerCut),
        like the box dying in the middle of a write.
        """
        calls = []
 
        def emit(record):
            calls.append(record)
            if len(calls) < cut_at:
                self.emit(record)
                return
            line = json.dumps(record).encode()
            with open(self.path, "ab") as f:
                f.write(line[:len(line) // 2])
            raise PowerCut()
 
        return emit
 
    def test_tc13_every_reading_from_scheduler_is_stored_in_order(self):
        # TC-13 (AC1): 3 reads, the second one fails. All 3 are in the file, in order.
        self.make([4.6, Exception("sensor_timeout"), 5.1]).run(max_reads=3)
 
        readings, skipped = load_readings(self.path)
        self.assertEqual(skipped, 0)
        self.assertEqual(readings, self.emitted)
        self.assertEqual([r["seq"] for r in readings], [1, 2, 3])
        self.assertEqual([r["timestamp_s"] for r in readings],
                         [1793100000, 1793100300, 1793100600])
        self.assertEqual([r["ok"] for r in readings], [True, False, True])
        self.assertEqual([r["temp_c"] for r in readings], [4.6, None, 5.1])
        self.assertEqual(readings[1]["error"], "sensor_timeout")
 
    def test_tc14_power_cut_during_a_run_keeps_earlier_readings(self):
        # TC-14 (AC3): power is lost while the 3rd reading is being written.
        with self.assertRaises(PowerCut):
            self.make([4.6, 4.8, 5.0, 5.2],
                      emit=self.emit_with_power_cut_on(3)).run(max_reads=4)
        before_cut = list(self.emitted)
        self.assertEqual(len(before_cut), 2)
 
        # Next boot: a new Scheduler on the same file (seq starts at 1 again).
        self.make([3.9]).run(max_reads=1)
        after_boot = self.emitted[2]
 
        # Earlier readings are kept, the torn line is skipped, the new one is stored.
        readings, skipped = load_readings(self.path)
        self.assertEqual(readings, before_cut + [after_boot])
        self.assertEqual(skipped, 1)
        self.assertEqual(after_boot["seq"], 1)
 
        # The new reading is on its own line, not glued onto the torn one.
        with open(self.path, "rb") as f:
            lines = f.read().split(b"\n")
        self.assertEqual(lines[-1], b"")  # the file ends with a newline
        self.assertEqual(len(lines), 5)   # 2 kept, 1 torn, 1 new, then ""
        self.assertEqual(json.loads(lines[3].decode()), after_boot)
 
 
if __name__ == "__main__":
    unittest.main()
```

*Result: still passes*

```text
$ python -m unittest -v test_store_end_to_end
test_tc13_every_reading_from_scheduler_is_stored_in_order ... ok
test_tc14_power_cut_during_a_run_keeps_earlier_readings ... ok
 
----------------------------------------
Ran 2 tests in 0.005s
 
OK
```

## Test Case Number: TC-12

**Test Case Name:** A 72-hour trip fits (`test_tc12_a_72_hour_trip_fits`)

**Expected output:** A full 72-hour trip at the default 300 s is 864 readings; with every read failed (the longest lines) the file is at most 864 × 160 = 138,240 bytes (the plan) and less than the 2,080,768 bytes free on the box; all 864 load back, 0 skipped (AC2)

### Red

Wrote the test first, in the same file as TC-13 and TC-14. It runs the real Scheduler for one full trip: 72 h ÷ 300 s = 864 reads, with a fake clock, so it takes well under a second. The fake sensor fails every read with `[Errno 110] ETIMEDOUT`, a real sensor error, so every line is as long as it gets (FORMAT.md section 5). The test then checks the file size against the plan (160 bytes per line) and against the free space Pun measured on the board.

storage.py from Session 1 already writes each reading as one short JSON line, so the test passed at once. To show that the test can fail, it was run once against a copy of storage.py that writes pretty-printed JSON, `json.dumps(record, indent=2)` (one line marked RED CHECK ONLY). The file grew to 146,772 bytes, more than the 138,240 planned, so TC-12 failed. TC-13 and TC-14 failed too, because each record was split over several lines.

*Test written first (new parts of store_readings/test_store_end_to_end.py):*

```text
# AC2 numbers, from store_readings/FORMAT.md section 5.
TRIP_S = 72 * 3600     # one full transit cycle is up to 72 hours (#16)
LINE_BYTES = 160       # planned size of one stored line
FREE_BYTES = 2080768   # free space Pun measured on the ESP32 in Wokwi (#13)
 
    def test_tc12_a_72_hour_trip_fits(self):
        # TC-12 (AC2): one full 72-hour trip at the default interval fits on the box.
        # Worst case: every read fails with a real sensor error, so every line is
        # as long as it gets.
        scheduler = self.make([OSError(110, "ETIMEDOUT")] * 864)
        self.assertEqual(scheduler.interval_s, 300)  # the default: no config file
        scheduler.run(max_reads=TRIP_S // scheduler.interval_s)  # 864 reads
 
        size = os.stat(self.path)[6]
        self.assertLessEqual(size, 864 * LINE_BYTES)  # 138,240 bytes, the plan
        self.assertLess(size, FREE_BYTES)
        self.assertEqual(load_readings(self.path), (self.emitted, 0))
```

*Result: fails (pretty-printed JSON)*

```text
$ python -m unittest -v test_store_end_to_end
test_tc12_a_72_hour_trip_fits ... FAIL
test_tc13_every_reading_from_scheduler_is_stored_in_order ... FAIL
test_tc14_power_cut_during_a_run_keeps_earlier_readings ... FAIL
 
========================================
FAIL: test_tc12_a_72_hour_trip_fits
----------------------------------------
Traceback (most recent call last):
  File "test_store_end_to_end.py", line 117, in test_tc12_a_72_hour_trip_fits
    self.assertLessEqual(size, 864 * LINE_BYTES)  # 138,240 bytes, the plan
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 146772 not less than or equal to 138240
 
========================================
FAIL: test_tc13_every_reading_from_scheduler_is_stored_in_order
----------------------------------------
Traceback (most recent call last):
  File "test_store_end_to_end.py", line 74, in test_tc13_every_reading_from_scheduler_is_stored_in_order
    self.assertEqual(skipped, 0)
AssertionError: 27 != 0
 
========================================
FAIL: test_tc14_power_cut_during_a_run_keeps_earlier_readings
----------------------------------------
Traceback (most recent call last):
  File "test_store_end_to_end.py", line 97, in test_tc14_power_cut_during_a_run_keeps_earlier_readings
    self.assertEqual(readings, before_cut + [after_boot])
AssertionError: Lists differ: [] != [{'device_id': 'BOX-001', 'shipment_id': '[349 chars]one}]
 
Second list contains 3 additional elements.
First extra element 0:
{'device_id': 'BOX-001', 'shipment_id': 'SHP-1001', 'seq': 1, 'timestamp_s': 1793100000, 'temp_c': 4.6, 'ok': True, 'error': None}
 
- []
+ [{'device_id': 'BOX-001',
+   'error': None,
+   'ok': True,
+   'seq': 1,
+   'shipment_id': 'SHP-1001',
+   'temp_c': 4.6,
+   'timestamp_s': 1793100000},
+  {'device_id': 'BOX-001',
+   'error': None,
+   'ok': True,
+   'seq': 2,
+   'shipment_id': 'SHP-1001',
+   'temp_c': 4.8,
+   'timestamp_s': 1793100300},
+  {'device_id': 'BOX-001',
+   'error': None,
+   'ok': True,
+   'seq': 1,
+   'shipment_id': 'SHP-1001',
+   'temp_c': 3.9,
+   'timestamp_s': 1793100600}]
 
----------------------------------------
Ran 3 tests in 0.238s
 
FAILED (failures=3)
```

### Green

Ran the same tests against the real storage.py. No change to storage.py: `append_reading()` writes `json.dumps(record)` and one `\n`, so a line is 152 to 154 bytes in this trip. The whole trip took 132,948 bytes: within the 138,240-byte plan, and about 6% of the 2,080,768 bytes free on the box.

*Code in storage.py (unchanged from Session 1; the function TC-12 measures):*

```text
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
```

*Result: passes*

```text
$ python -m unittest -v test_store_end_to_end
test_tc12_a_72_hour_trip_fits ... ok
test_tc13_every_reading_from_scheduler_is_stored_in_order ... ok
test_tc14_power_cut_during_a_run_keeps_earlier_readings ... ok
 
----------------------------------------
Ran 3 tests in 0.185s
 
OK
```

### Yellow

The number 864 was written twice in the test. It is now worked out once from `TRIP_S` (`reads = TRIP_S // 300`), so the test still reads as "one 72-hour trip" if the trip length in FORMAT.md changes. All 3 tests still pass.

*Code after refactoring (test_tc12_a_72_hour_trip_fits):*

```text
    def test_tc12_a_72_hour_trip_fits(self):
        # TC-12 (AC2): one full 72-hour trip at the default interval fits on the box.
        # Worst case: every read fails with a real sensor error, so every line is
        # as long as it gets.
        reads = TRIP_S // 300  # 864 readings at the default interval
        scheduler = self.make([OSError(110, "ETIMEDOUT")] * reads)
        self.assertEqual(scheduler.interval_s, 300)  # the default: no config file
        scheduler.run(max_reads=reads)
 
        size = os.stat(self.path)[6]
        self.assertLessEqual(size, reads * LINE_BYTES)  # 138,240 bytes, the plan
        self.assertLess(size, FREE_BYTES)
        self.assertEqual(load_readings(self.path), (self.emitted, 0))
```

*Result: still passes*

```text
$ python -m unittest -v test_store_end_to_end
test_tc12_a_72_hour_trip_fits ... ok
test_tc13_every_reading_from_scheduler_is_stored_in_order ... ok
test_tc14_power_cut_during_a_run_keeps_earlier_readings ... ok
 
----------------------------------------
Ran 3 tests in 0.201s
 
OK
```
