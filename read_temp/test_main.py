import importlib
import io
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

import config
from scheduler import Scheduler
from test_scheduler import FakeTime


class FakeDHT22:
    """Returns the given temperatures in order; an exception in the list is raised by measure()."""

    def __init__(self, values):
        self.values = list(values)
        self.current = None

    def measure(self):
        self.current = self.values.pop(0)
        if isinstance(self.current, Exception):
            raise self.current

    def temperature(self):
        return self.current


def load_main(values):
    """Import main.py with fake machine and dht modules, so no hardware is needed."""
    pins = []
    sensor = FakeDHT22(values)
    fakes = {
        "machine": types.SimpleNamespace(Pin=lambda number: pins.append(number) or number),
        "dht": types.SimpleNamespace(DHT22=lambda pin: sensor),
    }
    with mock.patch.dict(sys.modules, fakes):
        sys.modules.pop("main", None)
        main = importlib.import_module("main")
    return main, pins


class DriverTest(unittest.TestCase):
    def test_read_returns_temperature(self):
        main, _ = load_main([4.5])
        self.assertEqual(main.read(), 4.5)

    def test_read_raises_when_sensor_fails(self):
        main, _ = load_main([OSError("sensor_timeout")])
        with self.assertRaises(OSError):
            main.read()

    def test_sensor_is_on_pin_4(self):
        # diagram.json wires esp:4 to dht1:SDA.
        _, pins = load_main([])
        self.assertEqual(pins, [4])

    def test_main_runs_scheduler_with_driver(self):
        main, _ = load_main([])
        with mock.patch.object(main, "Scheduler") as scheduler:
            main.main()
        scheduler.assert_called_once_with(main.read, main.emit, "BOX-001", "SHP-1001")
        scheduler.return_value.run.assert_called_once_with()


class BoxTest(unittest.TestCase):
    """The real driver (with a fake sensor) plugged into the Scheduler, as main() does."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "config.json")
        self.time = FakeTime()

    def tearDown(self):
        self.dir.cleanup()

    def run_box(self, values):
        main, _ = load_main(values)
        out = io.StringIO()
        with redirect_stdout(out):
            Scheduler(main.read, main.emit, main.DEVICE_ID, main.SHIPMENT_ID,
                      clock=self.time.clock, sleep=self.time.sleep,
                      config_path=self.path).run(max_reads=len(values))
        return [json.loads(line) for line in out.getvalue().splitlines()]

    # AC: Temperature is read at a configurable interval
    def test_reads_at_interval_from_config(self):
        config.save({"interval_s": 60}, self.path)
        records = self.run_box([4.5, 4.6, 4.7])
        self.assertEqual(self.time.sleeps, [60, 60, 60])
        self.assertEqual([r["temp_c"] for r in records], [4.5, 4.6, 4.7])
        self.assertEqual([r["timestamp_s"] for r in records], [1000, 1060, 1120])

    def test_healthy_sensor_never_logs_a_failure(self):
        records = self.run_box([4.5] * 5)
        self.assertTrue(all(r["ok"] for r in records))

    # AC: Failed reads are logged, not silently skipped
    def test_failed_read_is_logged_as_record_and_reading_continues(self):
        records = self.run_box([4.5, OSError("sensor_timeout"), 4.7])
        self.assertEqual([r["ok"] for r in records], [True, False, True])
        self.assertEqual(records[1], {
            "device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 2,
            "timestamp_s": 1300, "temp_c": None, "ok": False, "error": "sensor_timeout",
        })


if __name__ == "__main__":
    unittest.main()
