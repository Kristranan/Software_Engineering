# Tests for on-box reading storage (003-2, store_readings/FORMAT.md).
# No hardware, clock or network: files go in a temporary folder, records are
# plain dicts made up in the test.
import json
import os
import tempfile
import unittest

from storage import append_reading, load_readings


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


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "readings.jsonl")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, data):
        with open(self.path, "ab") as f:
            f.write(data)

    def torn_line(self, record):
        """The first half of a line, as left by a power cut during the write."""
        line = json.dumps(record).encode()
        return line[:len(line) // 2]

    def test_missing_file_gives_no_readings(self):
        self.assertEqual(load_readings(self.path), ([], 0))

    def test_every_reading_is_stored_in_order(self):
        # AC1: every reading, failed reads too, comes back in the order written.
        records = [reading(1, 4.6), failed(2), reading(3, 5.1)]
        for record in records:
            self.assertTrue(append_reading(record, self.path))
        self.assertEqual(load_readings(self.path), (records, 0))

    def test_lines_end_with_newline_only(self):
        # FORMAT.md section 3: one record per line, "\n" only (no "\r\n" on Windows).
        append_reading(reading(1, 4.6), self.path)
        with open(self.path, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"}\n"))

    def test_torn_last_line_is_skipped_and_earlier_readings_kept(self):
        # AC3: a power cut can only break the line being written.
        append_reading(reading(1, 4.6), self.path)
        append_reading(reading(2, 4.8), self.path)
        self.write_raw(self.torn_line(reading(3, 5.0)))
        self.assertEqual(load_readings(self.path),
                         ([reading(1, 4.6), reading(2, 4.8)], 1))

    def test_reading_after_power_cut_starts_a_new_line(self):
        # AC3: the next reading is not glued onto the broken line.
        append_reading(reading(1, 4.6), self.path)
        self.write_raw(self.torn_line(reading(2, 4.8)))
        self.assertTrue(append_reading(reading(3, 5.0), self.path))
        self.assertEqual(load_readings(self.path),
                         ([reading(1, 4.6), reading(3, 5.0)], 1))

    def test_line_that_is_not_a_reading_is_skipped(self):
        # Valid JSON but not a reading: not an object, or a key is missing.
        no_error_key = reading(2, 4.8)
        del no_error_key["error"]
        append_reading(reading(1, 4.6), self.path)
        self.write_raw(b"[1, 2]\n" + json.dumps(no_error_key).encode() + b"\n")
        append_reading(reading(3, 5.0), self.path)
        self.assertEqual(load_readings(self.path),
                         ([reading(1, 4.6), reading(3, 5.0)], 2))

    def test_blank_lines_are_ignored_and_not_counted(self):
        append_reading(reading(1, 4.6), self.path)
        self.write_raw(b"\n  \n")
        append_reading(reading(2, 4.8), self.path)
        self.assertEqual(load_readings(self.path),
                         ([reading(1, 4.6), reading(2, 4.8)], 0))

    def test_storage_problem_returns_false_and_never_raises(self):
        # Scheduler does not catch exceptions from emit, so a storage problem
        # must not stop the box from reading (003-1 AC2).
        self.assertFalse(append_reading(reading(1, 4.6), self.dir.name))  # a folder, not a file
        self.assertFalse(append_reading({"temp_c": object()}, self.path))  # cannot be written as JSON
        self.assertEqual(load_readings(self.path), ([], 0))


if __name__ == "__main__":
    unittest.main()
