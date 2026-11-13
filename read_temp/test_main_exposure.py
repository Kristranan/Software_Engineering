import importlib.util
import io
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

from test_main import load_main


class MainExposureTest(unittest.TestCase):
    def test_boot_loads_freeze_state_for_current_shipment(self):
        load_state = mock.Mock(return_value=None)
        load_limits = mock.Mock(return_value={
            "upper_limit_c": 8.0,
            "lower_limit_c": 2.0,
        })

        fakes = {
            "exposure_limits": types.SimpleNamespace(
                load=load_limits,
            ),
            "freeze_state": types.SimpleNamespace(
                load_freeze_state=load_state,
                freeze_on_reading=mock.Mock(),
            ),
        }

        main, _ = load_main([], modules=fakes)

        load_limits.assert_called_once_with()
        load_state.assert_called_once_with(main.SHIPMENT_ID)
        self.assertIsNone(main.freeze)

    def test_emit_updates_freeze_for_good_and_failed_readings(self):
        saved = {"freeze_s": 60, "last_good": None}
        after_good = {"freeze_s": 120, "last_good": None}
        after_failed = {"freeze_s": 120, "last_good": None}
        update = mock.Mock(side_effect=[after_good, after_failed])
        main, _ = load_main([], modules={
            "exposure_limits": types.SimpleNamespace(
                load=lambda: {"upper_limit_c": 8.0, "lower_limit_c": 0.0}),
            "freeze_state": types.SimpleNamespace(
                load_freeze_state=lambda shipment_id: saved,
                freeze_on_reading=update),
        })
        good = {"timestamp_s": 60, "temp_c": -1.0, "ok": True}
        failed = {"timestamp_s": 120, "temp_c": None, "ok": False}
        output = io.StringIO()

        with redirect_stdout(output):
            main.emit(good)
            self.assertIs(main.freeze, after_good)
            main.emit(failed)

        self.assertEqual(update.call_args_list, [
            mock.call(saved, good, 0.0),
            mock.call(after_good, failed, 0.0),
        ])
        self.assertIs(main.freeze, after_failed)
        self.assertEqual([json.loads(line) for line in output.getvalue().splitlines()],
                         [good, failed])

    def test_real_freeze_total_survives_warming_and_program_reload(self):
        exposure_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exposure"))

        def load_module(name, filename):
            spec = importlib.util.spec_from_file_location(
                name, os.path.join(exposure_dir, filename))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        accumulator = load_module("_test_freeze_exposure", "freeze_exposure.py")
        with mock.patch.dict(sys.modules, {"freeze_exposure": accumulator}):
            persistence = load_module("_test_freeze_state", "freeze_state.py")

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "freeze_state.json")
            modules = {
                "freeze_state": types.SimpleNamespace(
                    load_freeze_state=lambda shipment: persistence.load_freeze_state(shipment, path),
                    freeze_on_reading=lambda state, record, lower: persistence.freeze_on_reading(
                        state, record, lower, path)),
            }
            main, _ = load_main([], modules=modules)
            self.assertIsNone(main.freeze)

            with redirect_stdout(io.StringIO()):
                for timestamp, temp, expected in ((0, 1.0, 0), (60, 9.0, 60), (120, 9.0, 60)):
                    main.emit({"timestamp_s": timestamp, "temp_c": temp,
                               "ok": True, "shipment_id": main.SHIPMENT_ID})
                    self.assertEqual(main.freeze["freeze_s"], expected)

            with open(path) as saved:
                self.assertEqual(json.load(saved)["freeze_s"], 60)

            restarted, _ = load_main([], modules=modules)
            self.assertEqual(restarted.freeze["freeze_s"], 60)
            self.assertEqual(restarted.freeze["last_good"]["timestamp_s"], 120)
            with redirect_stdout(io.StringIO()):
                restarted.emit({"timestamp_s": 180, "temp_c": 9.0,
                                "ok": True, "shipment_id": restarted.SHIPMENT_ID})
            self.assertEqual(restarted.freeze["freeze_s"], 60)


if __name__ == "__main__":
    unittest.main()
