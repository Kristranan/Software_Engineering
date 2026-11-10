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
