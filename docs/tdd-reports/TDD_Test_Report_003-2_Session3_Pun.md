# TDD Test Report

Smart Cold Box · Sprint 2 · Story 003-2 Store readings locally · Session 3: restart and power cut on the ESP32 (Wokwi, MicroPython v1.28.0)

| Feature | Expected output | Test Case Number | Test Case Name | Dev | Test Date |
| --- | --- | --- | --- | --- | --- |
| 003-2 Store readings locally | After the board restarts, loading gives the same 3 records back in order (a failed read included), 0 skipped (part of AC3 on the ESP32: a restart, not a power cut during a write) | TC-10 | Readings survive a restart | Witthayut P. (Pun) | 11 Nov 2026 |

**How it runs:** store_readings/on_box_check.py runs on the ESP32 in a separate Wokwi project (MicroPython on ESP32), with main.py set to `import on_box_check`. MicroPython has no unittest module, so the check prints PASS or FAIL. Session 2 (TDD_Test_Report_003-2_Session2_Pun.md) has TC-09 and the free-space measurement.

## Test Case Number: TC-10

**Test Case Name:** Readings survive a restart (`tc10_before_restart`, `tc10_after_restart`)

**Expected output:** after the board restarts, loading gives the same 3 records back in order (a failed read included), 0 skipped (part of AC3 on the ESP32: a restart, not a power cut during a write)

### Red

No Red step: this is a confirmation test. The whole test was written first (save 3 readings, `machine.reset()`, load them back) and run on the board. It passed on the first run, because `storage.py` already closes the file after every reading (Session 1, TC-02), so the readings are on flash before the restart. A failure was not staged.

The first boot is a power-on (`reset_cause()` 1): it saves the readings and restarts the board. The next boot (`reset_cause()` 2, which is `machine.HARD_RESET`; the boot line shows `SW_CPU_RESET`) loads and checks them. `os.listdir()` is printed after the restart, so a file lost by the board would show there.

The free space in this run (2,076,672 bytes) is 4,096 bytes (one block) less than in TC-09 (Session 2, 2,080,768 bytes), because on_box_check.py grew when TC-10 was added. The TC-09 number is the one used for AC2.

*Test written first (store_readings/on_box_check.py):*

```text
def tc10_before_restart():
    """TC-10, first boot: save 3 readings, then restart the board."""
    import machine
    from storage import append_reading

    remove(RESTART_PATH)
    records = [reading(1, 4.6), failed(2), reading(3, 5.1)]
    stored = [append_reading(record, RESTART_PATH) for record in records]
    if stored != [True, True, True]:
        remove(RESTART_PATH)
        print("TC-10 Readings survive a restart: FAIL (could not save before the restart)")
        print("  stored:", stored)
        return False
    print("TC-10 saved 3 readings, restarting the board")
    machine.reset()
    return None  # not reached on the board: machine.reset() does not return

def tc10_after_restart():
    """TC-10, after the restart. Expected: loading gives the same 3 records
    back in order, with 0 skipped."""
    from storage import load_readings

    records = [reading(1, 4.6), failed(2), reading(3, 5.1)]
    print("Files after the restart:", os.listdir())
    try:
        got = load_readings(RESTART_PATH)
    finally:
        remove(RESTART_PATH)  # never leave the check file on the board

    passed = got == (records, 0)
    print("TC-10 Readings survive a restart:", "PASS" if passed else "FAIL")
    if not passed:
        print("  got:", got)
    return passed

def main():
    import machine

    cause = machine.reset_cause()
    print("Reset cause: %d (power-on is %d)" % (cause, machine.PWRON_RESET))
    if cause == machine.PWRON_RESET:
        # First boot after the simulation starts: measure, TC-09, then TC-10
        # saves its readings and restarts the board.
        measure_free_space()
        tc09_storage_works_on_the_board()
        tc10_before_restart()
    else:
        # The boot after machine.reset(). Do not restart by hand (Ctrl-D)
        # instead: that would check a file that was never saved.
        tc10_after_restart()


main()
```

*Files on the board: main.py, on_box_check.py, storage.py (and diagram.json, which Wokwi puts on the board). main.py:*

```text
import on_box_check
```

*Result: passes on the first run*

```text
Wokwi Serial Monitor (ESP32 boot lines left out, except the reset reason)

rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
Reset cause: 1 (power-on is 1)
Free space: 2076672 bytes (estimate)
72-hour trip at 300 s needs: 138240 bytes
Shortest interval for a 72-hour trip: 20 s (estimate)
TC-09 Storage works on the board: PASS
TC-10 saved 3 readings, restarting the board
rst:0xc (SW_CPU_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
Reset cause: 2 (power-on is 1)
Files after the restart: ['diagram.json', 'main.py', 'on_box_check.py', 'restart_readings.jsonl', 'storage.py']
TC-10 Readings survive a restart: PASS
MicroPython v1.28.0 on 2026-04-06; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```

### Green

No code change: the test passed on the first run (output above). TC-10 confirms that readings survive a restart on the ESP32. A restart is not a power cut in the middle of a write: that is TC-11.

### Yellow

The same 3 records were written out in 3 places (TC-09, and both halves of TC-10). They now come from one helper, `three_records()`, which builds a new list on every call. No change in behaviour; TC-09 and TC-10 still pass.

*Code after refactoring:*

```text
def three_records():
    """The 3 records TC-09 and TC-10 save: good, failed, good."""
    return [reading(1, 4.6), failed(2), reading(3, 5.1)]

# used in tc09_storage_works_on_the_board(), tc10_before_restart()
# and tc10_after_restart():
    records = three_records()
```

*Result: still passes*

```text
Wokwi Serial Monitor (ESP32 boot lines left out, except the reset reason)

rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
Reset cause: 1 (power-on is 1)
Free space: 2076672 bytes (estimate)
72-hour trip at 300 s needs: 138240 bytes
Shortest interval for a 72-hour trip: 20 s (estimate)
TC-09 Storage works on the board: PASS
TC-10 saved 3 readings, restarting the board
rst:0xc (SW_CPU_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
Reset cause: 2 (power-on is 1)
Files after the restart: ['diagram.json', 'main.py', 'on_box_check.py', 'restart_readings.jsonl', 'storage.py']
TC-10 Readings survive a restart: PASS
MicroPython v1.28.0 on 2026-04-06; Generic ESP32 module with ESP32
Type "help()" for more information.
>>>
```
