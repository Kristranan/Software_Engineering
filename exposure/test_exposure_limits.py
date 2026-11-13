# Tests for exposure_limits.py (stories 004-1 and 004-2: temperature limits in the config file).
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

    def test_default_limits_match_profile(self):
        self.assertEqual(limits.DEFAULTS["lower_limit_c"], 2.0)
        self.assertEqual(limits.DEFAULTS["upper_limit_c"], 8.0)

    def test_missing_file_uses_defaults(self):
        self.assertEqual(limits.load(self.path), limits.DEFAULTS)

    def test_file_in_repo_is_valid(self):
        path = os.path.join(HERE, "exposure_limits.json")
        self.assertEqual(limits.validate(limits.load(path)), limits.load(path))
        with open(path) as f:
            content = f.read()
            self.assertIn("lower_limit_c", content)
            self.assertIn("upper_limit_c", content)

    def test_save_then_load_roundtrip(self):
        limits.save({"lower_limit_c": 2.0, "upper_limit_c": 8.0}, self.path)
        self.assertEqual(limits.load(self.path), {"lower_limit_c": 2.0, "upper_limit_c": 8.0})

    def test_valid_custom_limits_are_accepted(self):
        limits.save({"lower_limit_c": 1.5, "upper_limit_c": 7.5}, self.path)
        self.assertEqual(limits.load(self.path), {"lower_limit_c": 1.5, "upper_limit_c": 7.5})

    def test_save_rejects_invalid_values(self):
        for bad in ("2", True, None, [], float("nan"), float("inf"), -40.1, 80.1):
            with self.assertRaises(ValueError, msg=repr(bad)):
                limits.save({"lower_limit_c": bad, "upper_limit_c": 8.0}, self.path)
            with self.assertRaises(ValueError, msg=repr(bad)):
                limits.save({"lower_limit_c": 2.0, "upper_limit_c": bad}, self.path)

    def test_save_rejects_lower_not_less_than_upper(self):
        # lower greater than or equal to upper must be rejected
        for invalid_pair in (
            {"lower_limit_c": 8.0, "upper_limit_c": 2.0},
            {"lower_limit_c": 5.0, "upper_limit_c": 5.0},
        ):
            with self.assertRaises(ValueError):
                limits.save(invalid_pair, self.path)

    def test_save_rejects_misspelled_key(self):
        with self.assertRaises(ValueError):
            limits.save({"lower_limit_c": 2.0, "upper_limt_c": 8.0}, self.path)

    def test_rejected_save_keeps_previous_limits(self):
        limits.save({"lower_limit_c": 2.0, "upper_limit_c": 8.0}, self.path)
        with self.assertRaises(ValueError):
            limits.save({"lower_limit_c": 10.0, "upper_limit_c": 5.0}, self.path)
        self.assertEqual(limits.load(self.path), {"lower_limit_c": 2.0, "upper_limit_c": 8.0})

    def test_corrupt_file_falls_back_to_defaults(self):
        for text in ("{not json", "[1, 2]", "", "NaN"):
            self.write_raw(text)
            self.assertEqual(limits.load(self.path), limits.DEFAULTS, text)

    def test_bad_value_in_file_falls_back_to_default(self):
        for text in ('{"lower_limit_c": "2", "upper_limit_c": 8.0}', 
                     '{"lower_limit_c": 2.0, "upper_limit_c": 999}'):
            self.write_raw(text)
            self.assertEqual(limits.load(self.path), limits.DEFAULTS, text)

    def test_leftover_temp_file_from_power_cut_is_ignored(self):
        limits.save({"lower_limit_c": 2.0, "upper_limit_c": 8.0}, self.path)
        self.write_tmp('{"lower_limit_c": 1.0')  # half-written
        self.assertEqual(limits.load(self.path), {"lower_limit_c": 2.0, "upper_limit_c": 8.0})
        limits.save({"lower_limit_c": 1.5, "upper_limit_c": 7.5}, self.path)
        self.assertEqual(limits.load(self.path), {"lower_limit_c": 1.5, "upper_limit_c": 7.5})
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def write_tmp(self, text):
        with open(self.path + ".tmp", "w") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()