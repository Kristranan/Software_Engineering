# On-box check for story 003-2 (TDD Session 2). Owner: Pun.
# Runs on the ESP32 in Wokwi, not in the unit tests: it needs the board's own
# file system. MicroPython has no unittest module, so each check prints PASS
# or FAIL.
#
# How to run: use a separate Wokwi project (MicroPython on ESP32), not the
# read_temp project, so read_temp/main.py does not run and write readings.jsonl.
# Put this file and storage.py on the board, and set main.py to:
#     import on_box_check
#
# 1. Measurement only (no PASS/FAIL): the free space on the board, for AC2
#    (#13). Gramma's TC-12 uses this number. The two script files themselves
#    take a few KB of the space measured.
# 2. TC-09: storage works on the board. Saves 3 readings and loads them back.
# 3. TC-10: readings survive a restart. The first boot (power-on) saves 3
#    readings and calls machine.reset(); the next boot loads and checks them.
#    A restart is not a power cut in the middle of a write: that is TC-11.
import os

CHECK_PATH = "check_readings.jsonl"  # not readings.jsonl: real readings are never touched
RESTART_PATH = "restart_readings.jsonl"  # TC-10 only
TRIP_S = 72 * 3600  # longest transit cycle, from #16
LINE_BYTES = 160  # planned size of one stored line, FORMAT.md section 5


def free_bytes():
    s = os.statvfs("/")
    return s[1] * s[4]  # fragment size x blocks free for use


def measure_free_space():
    free = free_bytes()
    print("Free space:", free, "bytes (estimate)")
    print("72-hour trip at 300 s needs:", TRIP_S // 300 * LINE_BYTES, "bytes")
    if free <= 0:
        print("No free space: a 72-hour trip does not fit at any interval")
        return
    # interval_s >= TRIP_S * LINE_BYTES / free, rounded up
    print("Shortest interval for a 72-hour trip:", -(-TRIP_S * LINE_BYTES // free), "s (estimate)")


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


def three_records():
    """The 3 records TC-09 and TC-10 save: good, failed, good."""
    return [reading(1, 4.6), failed(2), reading(3, 5.1)]


def remove(path):
    try:
        os.remove(path)
    except OSError:
        pass  # the file was not there


def tc09_storage_works_on_the_board():
    """Expected: append_reading() returns True 3 times, and loading gives the
    3 records back in order (a failed read included) with 0 skipped."""
    from storage import append_reading, load_readings

    remove(CHECK_PATH)
    records = three_records()
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


def tc10_before_restart():
    """TC-10, first boot: save 3 readings, then restart the board."""
    import machine
    from storage import append_reading

    remove(RESTART_PATH)
    records = three_records()
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

    records = three_records()
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
