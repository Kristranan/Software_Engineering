# Tests for profile_loader.py (004-3: load the vaccine profile on the box).
# No hardware, clock or network: every test uses a temporary folder.
import os
import tempfile
import unittest

import profile_loader as loader

HERE = os.path.dirname(os.path.abspath(__file__))


class ProfileLoaderTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "profile.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    # TC01
    def test_valid_profile_returns_both_limits(self):
        self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
        self.assertEqual(loader.load_profile(self.path),
                         {"heat_limit_s": 7200, "freeze_limit_s": 1800})

    # TC02
    def test_missing_file_raises_profile_error(self):
        with self.assertRaises(loader.ProfileError):
            loader.load_profile(self.path)

    # TC03
    def test_broken_json_or_not_an_object_raises_profile_error(self):
        for text in ("{heat", "[7200, 1800]"):
            with self.subTest(text=text):
                self.write_raw(text)
                with self.assertRaises(loader.ProfileError):
                    loader.load_profile(self.path)

    # TC04
    def test_missing_limit_raises_profile_error(self):
        for text in ('{"freeze_limit_s": 1800}', '{"heat_limit_s": 7200}'):
            with self.subTest(text=text):
                self.write_raw(text)
                with self.assertRaises(loader.ProfileError):
                    loader.load_profile(self.path)

    # TC05
    def test_bad_limit_value_raises_profile_error(self):
        for value in ("-1", "7200.5", '"7200"', "true"):
            with self.subTest(value=value):
                self.write_raw('{"heat_limit_s": %s, "freeze_limit_s": 1800}' % value)
                with self.assertRaises(loader.ProfileError):
                    loader.load_profile(self.path)

    # TC06
    def test_profile_file_in_repo_loads(self):
        profile = loader.load_profile(os.path.join(HERE, "profile.json"))
        self.assertIn("heat_limit_s", profile)
        self.assertIn("freeze_limit_s", profile)


if __name__ == "__main__":
    unittest.main()
