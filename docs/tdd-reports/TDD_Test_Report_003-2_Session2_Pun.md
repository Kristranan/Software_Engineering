# TDD Test Report

Smart Cold Box · Sprint 2 · Story 003-2 Store readings locally · Session 2: storage on the ESP32 (Wokwi, MicroPython v1.28.0)

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 003-2 Store readings locally | append_reading() returns True 3 times; load gives the 3 records back in order (a failed read included), 0 skipped (AC1 on the ESP32) | TC-09 | Storage works on the board | Witthayut P. (Pun) | 10 Nov 2026 |

**How it runs:** store_readings/on_box_check.py runs on the ESP32 in a separate Wokwi project (MicroPython on ESP32), with main.py set to `import on_box_check`. MicroPython has no unittest module, so the check prints PASS or FAIL.

**Measurement (not a test case):** free space on the board with storage.py on it: 2,080,768 bytes. A 72-hour trip at 300 s needs 138,240 bytes, so it fits. The shortest interval that fits a 72-hour trip is 20 s. This number is for TC-12 (AC2).

## Test Case Number: TC-09

**Test Case Name:** Storage works on the board (`tc09_storage_works_on_the_board`)

**Expected output:** append_reading() returns True 3 times; load gives the 3 records back in order (a failed read included), 0 skipped (AC1 on the ESP32)

### Red

TC-09 checks the storage code from Session 1 on a new platform: MicroPython on the ESP32. Wrote the check first and ran it on a board that did not have storage.py yet, so the import failed.

*Test written first (store_readings/on_box_check.py):*

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
 
def remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
 
def tc09_storage_works_on_the_board():
    """Expected: append_reading() returns True 3 times, and loading gives the
    3 records back in order (a failed read included) with 0 skipped."""
    from storage import append_reading, load_readings
 
    remove(CHECK_PATH)
    records = [reading(1, 4.6), failed(2), reading(3, 5.1)]
    try:
        stored = [append_reading(record, CHECK_PATH) for record in records]
        got = load_readings(CHECK_PATH)
    finally:
        remove(CHECK_PATH)  # never leave the check file on the board
 
    passed = stored == [True, True, True] and got == (records, 0)
    print("TC-09 Storage works on the board:", "PASS" if passed else "FAIL")
    if not passed:
        print("  stored:", stored)
        print("  got:", got)
    return passed
```

*Files on the board: main.py, on_box_check.py (no storage.py yet). main.py:*

```text
import on_box_check
```

*Result: fails*

```text
Wokwi Serial Monitor (ESP32 boot lines left out)
 
Free space: 2084864 bytes (estimate)
72-hour trip at 300 s needs: 138240 bytes
Shortest interval for a 72-hour trip: 20 s (estimate)
Traceback (most recent call last):
  File "main.py", line 1, in <module>
  File "on_box_check.py", line 81, in <module>
  File "on_box_check.py", line 62, in tc09_storage_works_on_the_board
ImportError: no module named 'storage'
MicroPython v1.28.0 on 2026-04-06; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```

### Green

Added storage.py to the board (the same file as store_readings/storage.py, no change). It works on MicroPython without any change: all 3 records come back.

*Files on the board: main.py, on_box_check.py, storage.py. main.py:*

```text
import on_box_check
import storage
```

*Result: passes*

```text
Wokwi Serial Monitor (ESP32 boot lines left out)
 
Free space: 2080768 bytes (estimate)
72-hour trip at 300 s needs: 138240 bytes
Shortest interval for a 72-hour trip: 20 s (estimate)
TC-09 Storage works on the board: PASS
MicroPython v1.28.0 on 2026-04-06; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```

### Yellow

main.py also imported storage, which is not needed: on_box_check.py imports it itself. Removed that line. The check still passes.

*main.py after refactoring:*

```text
import on_box_check
```

*Result: still passes*

```text
Wokwi Serial Monitor (ESP32 boot lines left out)
 
Free space: 2080768 bytes (estimate)
72-hour trip at 300 s needs: 138240 bytes
Shortest interval for a 72-hour trip: 20 s (estimate)
TC-09 Storage works on the board: PASS
MicroPython v1.28.0 on 2026-04-06; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```
