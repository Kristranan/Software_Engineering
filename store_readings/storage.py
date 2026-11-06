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
