import io
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

MAIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")


class StopLoop(Exception):
    """Raised by the fake sleep to end main.py's endless loop."""


class FakeBoard:
    """Stands in for machine, dht and time, so main.py runs without hardware or a real clock.

    readings: one item per attempt, (temperature, humidity) or an exception that
    dht.measure() raises.
    """

    def __init__(self, readings, start_ms=0):
        self.readings = list(readings)
        self.now_ms = start_ms
        self.pins = []
        self.sleeps = []
        self.current = None

    def modules(self):
        board = self

        class Pin:
            def __init__(self, number):
                board.pins.append(number)

        class DHT22:
            def __init__(self, pin):
                pass

            def measure(self):
                board.current = board.readings.pop(0)
                if isinstance(board.current, Exception):
                    raise board.current

            def temperature(self):
                return board.current[0]

            def humidity(self):
                return board.current[1]

        def sleep(seconds):
            board.sleeps.append(seconds)
            board.now_ms += seconds * 1000
            if not board.readings:
                raise StopLoop()

        def ticks_ms():
            return board.now_ms

        return {
            "machine": types.SimpleNamespace(Pin=Pin),
            "dht": types.SimpleNamespace(DHT22=DHT22),
            "time": types.SimpleNamespace(sleep=sleep, ticks_ms=ticks_ms),
        }


def run_main(board):
    """Run main.py until the readings run out; return what it printed."""
    with open(MAIN_PATH) as f:
        code = compile(f.read(), MAIN_PATH, "exec")
    out = io.StringIO()
    with mock.patch.dict(sys.modules, board.modules()), redirect_stdout(out):
        try:
            exec(code, {"__name__": "__main__"})
        except StopLoop:
            pass
    return out.getvalue().splitlines()


class MainTest(unittest.TestCase):
    # AC: Temperature is read at a configurable interval
    def test_good_read_prints_temperature_and_humidity(self):
        lines = run_main(FakeBoard([(4.5, 60.0)], start_ms=2000))
        self.assertEqual(lines, [
            "Attemp:  1",
            "Temperature: 4.5 Time 2.0",
            "Humidity: 60.0 Time: 2.0",
        ])

    def test_reads_again_after_each_wait(self):
        board = FakeBoard([(4.5, 60.0), (4.6, 61.0)])
        lines = run_main(board)
        self.assertEqual(board.sleeps, [5, 5])
        self.assertIn("Temperature: 4.5 Time 0.0", lines)
        self.assertIn("Temperature: 4.6 Time 5.0", lines)

    def test_sensor_is_on_pin_4(self):
        # diagram.json wires esp:4 to dht1:SDA.
        board = FakeBoard([(4.5, 60.0)])
        run_main(board)
        self.assertEqual(board.pins, [4])

    # AC: Failed reads are logged, not silently skipped
    def test_failed_read_is_logged_with_error_and_time(self):
        lines = run_main(FakeBoard([OSError("sensor_timeout")], start_ms=7000))
        self.assertEqual(lines, [
            "Attemp:  1",
            "ERROR: Sensor read failed sensor_timeout Time 7.0",
        ])

    def test_failed_read_does_not_print_a_temperature(self):
        lines = run_main(FakeBoard([OSError("sensor_timeout")]))
        self.assertFalse(any(line.startswith("Temperature") for line in lines))

    def test_reading_continues_after_a_failed_read(self):
        board = FakeBoard([OSError("sensor_timeout"), (4.6, 61.0)])
        lines = run_main(board)
        self.assertEqual(board.sleeps, [5, 5])
        self.assertEqual(lines[-3:], [
            "Attemp:  2",
            "Temperature: 4.6 Time 5.0",
            "Humidity: 61.0 Time: 5.0",
        ])


if __name__ == "__main__":
    unittest.main()
