"""Entry-point wiring tests: real dependencies are exercised separately in acceptance tests."""
import io
import json
import types
import unittest
from contextlib import redirect_stdout
from unittest import mock

from test_main import FakeProfileError, load_main


class MainPipelineTest(unittest.TestCase):
    def test_failed_read_is_unknown_and_next_good_reading_is_compared(self):
        check = mock.Mock(return_value={"heat_exceeded": False, "freeze_exceeded": False})
        main, _ = load_main([], modules={
            "profile_check": types.SimpleNamespace(
                ProfileError=FakeProfileError, check_exposure=check),
        })
        self.assertEqual(main.comparison_result["status"], "unknown")
        with redirect_stdout(io.StringIO()):
            main.emit({"timestamp_s": 0, "temp_c": None, "ok": False})
            self.assertEqual(main.comparison_result["status"], "unknown")
            self.assertIsNone(main.comparison_result["heat_exceeded"])
            check.assert_not_called()
            main.emit({"timestamp_s": 60, "temp_c": 4.0, "ok": True})
        check.assert_called_once_with(0, 0)
        self.assertEqual(main.comparison_result["status"], "compared")

    def test_comparison_errors_are_unknown_and_next_reading_can_recover(self):
        for error in (FakeProfileError("missing freeze limit"), ValueError("bad total")):
            with self.subTest(error=type(error).__name__):
                check = mock.Mock(side_effect=[error, {
                    "heat_exceeded": False, "freeze_exceeded": True,
                }])
                main, _ = load_main([], modules={
                    "profile_check": types.SimpleNamespace(
                        ProfileError=FakeProfileError, check_exposure=check),
                })
                with redirect_stdout(io.StringIO()):
                    main.emit({"timestamp_s": 0, "temp_c": 4.0, "ok": True})
                    self.assertEqual(main.comparison_result["status"], "unknown")
                    self.assertIsNone(main.comparison_result["heat_exceeded"])
                    self.assertIsNone(main.comparison_result["freeze_exceeded"])
                    self.assertIn(str(error), main.comparison_result["reason"])
                    main.emit({"timestamp_s": 60, "temp_c": 4.0, "ok": True})
                self.assertEqual(main.comparison_result["status"], "compared")
                self.assertTrue(main.comparison_result["freeze_exceeded"])

    def test_comparison_uses_new_heat_and_freeze_totals(self):
        check = mock.Mock(return_value={"heat_exceeded": True, "freeze_exceeded": False})
        main, _ = load_main([], modules={
            "heat_state": types.SimpleNamespace(
                load_heat_state=lambda shipment: None,
                heat_on_reading=lambda state, record, limit: {"heat_s": 120}),
            "freeze_state": types.SimpleNamespace(
                load_freeze_state=lambda shipment: None,
                freeze_on_reading=lambda state, record, limit: {"freeze_s": 60}),
            "profile_check": types.SimpleNamespace(
                ProfileError=FakeProfileError, check_exposure=check),
        })
        with redirect_stdout(io.StringIO()):
            main.emit({"timestamp_s": 60, "temp_c": 9.0, "ok": True})
        check.assert_called_once_with(120, 60)
        self.assertEqual(main.comparison_result, {
            "status": "compared", "heat_exceeded": True, "freeze_exceeded": False,
        })

    def test_heat_restores_at_boot_and_updates_with_its_own_threshold(self):
        saved = {"heat_s": 60, "last_good": None}
        updated = {"heat_s": 120, "last_good": None}
        load = mock.Mock(return_value=saved)
        update = mock.Mock(return_value=updated)
        main, _ = load_main([], modules={
            "exposure_limits": types.SimpleNamespace(
                load=lambda: {"upper_limit_c": 10.0, "lower_limit_c": 1.0}),
            "heat_state": types.SimpleNamespace(load_heat_state=load, heat_on_reading=update),
        })
        load.assert_called_once_with(main.SHIPMENT_ID)
        record = {"timestamp_s": 60, "temp_c": 11.0, "ok": True}
        with redirect_stdout(io.StringIO()):
            main.emit(record)
        update.assert_called_once_with(saved, record, 10.0)
        self.assertIs(main.heat, updated)

    def test_all_readings_are_stored_and_storage_false_does_not_stop_emit(self):
        append = mock.Mock(side_effect=[False, True])
        freeze_update = mock.Mock(return_value={"freeze_s": 0, "last_good": None})
        main, _ = load_main([], modules={
            "storage": types.SimpleNamespace(append_reading=append),
            "freeze_state": types.SimpleNamespace(
                load_freeze_state=lambda shipment: None,
                freeze_on_reading=freeze_update),
        })
        good = {"timestamp_s": 0, "temp_c": 4.0, "ok": True}
        failed = {"timestamp_s": 60, "temp_c": None, "ok": False}
        output = io.StringIO()
        with redirect_stdout(output):
            main.emit(good)
            main.emit(failed)
        self.assertEqual(append.call_args_list, [mock.call(good), mock.call(failed)])
        self.assertEqual(freeze_update.call_count, 2)
        self.assertEqual([json.loads(line) for line in output.getvalue().splitlines()],
                         [good, failed])


if __name__ == "__main__":
    unittest.main()
