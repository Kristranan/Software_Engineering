import os
import tempfile
import unittest

import config


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "config.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    def test_missing_file_uses_defaults(self):
        self.assertEqual(config.load(self.path), config.DEFAULTS)

    def test_save_then_load_roundtrip(self):
        config.save({"interval_s": 60}, self.path)
        self.assertEqual(config.load(self.path), {"interval_s": 60})

    def test_save_overwrites_and_leaves_no_temp_file(self):
        config.save({"interval_s": 60}, self.path)
        config.save({"interval_s": 120}, self.path)
        self.assertEqual(config.load(self.path)["interval_s"], 120)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_save_rejects_invalid_values(self):
        for bad in (9, 3601, "60", 60.0, True, None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                config.save({"interval_s": bad}, self.path)

    def test_rejected_save_keeps_previous_config(self):
        config.save({"interval_s": 60}, self.path)
        with self.assertRaises(ValueError):
            config.save({"interval_s": 0}, self.path)
        self.assertEqual(config.load(self.path)["interval_s"], 60)

    def test_corrupt_or_invalid_file_falls_back_to_defaults(self):
        for text in ("{not json", "[1, 2]", '{"interval_s": 0}', ""):
            self.write_raw(text)
            self.assertEqual(config.load(self.path), config.DEFAULTS, text)

    def test_missing_key_uses_default(self):
        self.write_raw("{}")
        self.assertEqual(config.load(self.path), config.DEFAULTS)

    def test_leftover_temp_file_from_power_cut_is_ignored(self):
        config.save({"interval_s": 60}, self.path)
        with open(self.path + ".tmp", "w") as f:
            f.write('{"interval_s": 9')  # half-written
        self.assertEqual(config.load(self.path)["interval_s"], 60)
        config.save({"interval_s": 90}, self.path)
        self.assertEqual(config.load(self.path)["interval_s"], 90)


if __name__ == "__main__":
    unittest.main()
