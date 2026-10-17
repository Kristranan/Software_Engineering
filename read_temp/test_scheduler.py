import os
import tempfile
import unittest

import config
from scheduler import RECORD_KEYS, Scheduler


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

    def __init__(self, start=1000):
        self.now = start
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class SchedulerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "config.json")
        self.time = FakeTime()
        self.records = []

    def tearDown(self):
        self.dir.cleanup()

    def make(self, values):
        return Scheduler(FakeSensor(values).read, self.records.append,
                         "BOX-001", "SHP-1001",
                         clock=self.time.clock, sleep=self.time.sleep,
                         config_path=self.path)

    # AC: Temperature is read at a configurable interval
    def test_reads_at_configured_interval(self):
        config.save({"interval_s": 60}, self.path)
        self.make([4.5, 4.6, 4.7]).run(max_reads=3)
        self.assertEqual(self.time.sleeps, [60, 60, 60])
        self.assertEqual([r["timestamp_s"] for r in self.records], [1000, 1060, 1120])
        self.assertEqual([r["temp_c"] for r in self.records], [4.5, 4.6, 4.7])

    def test_changing_config_changes_interval_without_code_change(self):
        config.save({"interval_s": 120}, self.path)
        self.make([4.5, 4.6]).run(max_reads=2)
        self.assertEqual(self.time.sleeps, [120, 120])

    def test_uses_default_interval_when_no_config_file(self):
        self.make([4.5]).run(max_reads=1)
        self.assertEqual(self.time.sleeps, [config.DEFAULTS["interval_s"]])

    # AC: Reading continues without external power or network
    def test_after_power_cut_box_reloads_interval_and_keeps_reading(self):
        config.save({"interval_s": 60}, self.path)
        self.make([4.5, 4.6]).run(max_reads=2)
        # Power cut: everything in memory is gone; a new scheduler starts on boot.
        self.make([4.7, 4.8]).run(max_reads=2)
        self.assertEqual(self.time.sleeps, [60, 60, 60, 60])
        self.assertEqual([r["temp_c"] for r in self.records], [4.5, 4.6, 4.7, 4.8])

    def test_seq_restarts_at_1_after_power_cut(self):
        # Documented Sprint 1 limit: keeping seq needs on-box storage (003-2).
        self.make([4.5, 4.6]).run(max_reads=2)
        self.make([4.7]).run(max_reads=1)
        self.assertEqual([r["seq"] for r in self.records], [1, 2, 1])

    def test_failed_read_is_emitted_and_reading_continues(self):
        self.make([4.5, OSError("sensor_timeout"), 4.7]).run(max_reads=3)
        self.assertEqual([r["ok"] for r in self.records], [True, False, True])
        failed = self.records[1]
        self.assertIsNone(failed["temp_c"])
        self.assertEqual(failed["error"], "sensor_timeout")
        self.assertEqual(failed["seq"], 2)

    def test_failed_read_without_message_uses_exception_name(self):
        self.make([OSError()]).run(max_reads=1)
        self.assertEqual(self.records[0]["error"], "OSError")

    # Record shape (alert_depot/contracts.py names)
    def test_record_has_agreed_fields(self):
        self.make([4.5]).run(max_reads=1)
        self.assertEqual(self.records[0], {
            "device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 1,
            "timestamp_s": 1000, "temp_c": 4.5, "ok": True, "error": None,
        })
        self.assertEqual(tuple(self.records[0]), RECORD_KEYS)

    def test_timestamp_is_whole_seconds(self):
        self.time.now = 1000.75
        self.make([4.5]).run(max_reads=1)
        self.assertEqual(self.records[0]["timestamp_s"], 1000)


if __name__ == "__main__":
    unittest.main()
