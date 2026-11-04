# Tests for exposure_limits.py (004-2: lower temperature limit in the config file).
# No hardware, clock or network: every test uses a temporary folder.
import os
import tempfile
import unittest

import exposure_limits as limits

HERE = os.path.dirname(os.path.abspath(__file__))


class ExposureLimitsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "exposure_limits.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    def test_default_lower_limit_is_bottom_of_2_to_8_profile(self):
        self.assertEqual(limits.DEFAULTS["lower_limit_c"], 2.0)

    def test_missing_file_uses_defaults(self):
        self.assertEqual(limits.load(self.path), limits.DEFAULTS)

    def test_file_in_repo_is_valid(self):
        path = os.path.join(HERE, "exposure_limits.json")
        self.assertEqual(limits.validate(limits.load(path)), limits.load(path))
        with open(path) as f:
            self.assertIn("lower_limit_c", f.read())

    def test_save_then_load_roundtrip(self):
        limits.save({"lower_limit_c": 1.5}, self.path)
        self.assertEqual(limits.load(self.path), {"lower_limit_c": 1.5})

    def test_negative_and_whole_number_limits_are_accepted(self):
        limits.save({"lower_limit_c": -0.5}, self.path)
        self.assertEqual(limits.load(self.path)["lower_limit_c"], -0.5)
        limits.save({"lower_limit_c": 0}, self.path)
        value = limits.load(self.path)["lower_limit_c"]
        self.assertEqual(value, 0.0)
        self.assertIsInstance(value, float)

    def test_limit_changes_without_code_change(self):
        self.write_raw('{"lower_limit_c": 1.0}')
        self.assertEqual(limits.load(self.path)["lower_limit_c"], 1.0)

    def test_save_rejects_invalid_values(self):
        for bad in ("2", True, None, [], float("nan"), float("inf"), -40.1, 80.1):
            with self.assertRaises(ValueError, msg=repr(bad)):
                limits.save({"lower_limit_c": bad}, self.path)

    def test_save_rejects_misspelled_key(self):
        with self.assertRaises(ValueError):
            limits.save({"lower_limt_c": 1.0}, self.path)

    def test_rejected_save_keeps_previous_limits(self):
        limits.save({"lower_limit_c": 1.0}, self.path)
        with self.assertRaises(ValueError):
            limits.save({"lower_limit_c": "cold"}, self.path)
        self.assertEqual(limits.load(self.path)["lower_limit_c"], 1.0)

    def test_corrupt_file_falls_back_to_defaults(self):
        for text in ("{not json", "[1, 2]", "", "NaN"):
            self.write_raw(text)
            self.assertEqual(limits.load(self.path), limits.DEFAULTS, text)

    def test_bad_value_in_file_falls_back_to_default(self):
        for text in ('{"lower_limit_c": "2"}', '{"lower_limit_c": 999}',
                     '{"lower_limit_c": NaN}', '{"lower_limit_c": null}'):
            self.write_raw(text)
            self.assertEqual(limits.load(self.path)["lower_limit_c"], 2.0, text)

    def test_leftover_temp_file_from_power_cut_is_ignored(self):
        limits.save({"lower_limit_c": 1.0}, self.path)
        self.write_tmp('{"lower_limit_c": 0.')  # half-written
        self.assertEqual(limits.load(self.path)["lower_limit_c"], 1.0)
        limits.save({"lower_limit_c": 1.5}, self.path)
        self.assertEqual(limits.load(self.path)["lower_limit_c"], 1.5)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def write_tmp(self, text):
        with open(self.path + ".tmp", "w") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
