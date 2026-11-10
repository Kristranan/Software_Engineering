# Tests for profile_check.py (004-3: load the profile and compare on the box).
# No hardware, clock or network: every test uses a temporary folder.
import os
import tempfile
import unittest
from unittest import mock

import profile_check as check


class ProfileCheckTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "profile.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    # TC07
    def test_uses_limits_from_profile_file(self):
        self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
        self.assertEqual(check.check_exposure(7201, 1800, self.path),
                         {"heat_exceeded": True, "freeze_exceeded": False})

    # TC08
    def test_without_a_path_reads_profile_json_in_the_box_folder(self):
        self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')
        here = os.getcwd()
        os.chdir(self.dir.name)
        try:
            result = check.check_exposure(0, 1801)
        finally:
            os.chdir(here)
        self.assertEqual(result, {"heat_exceeded": False, "freeze_exceeded": True})

    # TC09
    def test_broken_profile_raises_profile_error_instead_of_a_result(self):
        self.write_raw('{"heat_limit_s": 7200}')
        with self.assertRaises(check.ProfileError):
            check.check_exposure(0, 0, self.path)

    # TC10
    def test_runs_with_no_network(self):
        self.write_raw('{"heat_limit_s": 7200, "freeze_limit_s": 1800}')

        def no_network(*args, **kwargs):
            raise OSError("network used")

        with mock.patch("socket.socket", no_network), \
                mock.patch("socket.create_connection", no_network), \
                mock.patch("socket.getaddrinfo", no_network):
            result = check.check_exposure(7200, 1800, self.path)
        self.assertEqual(result, {"heat_exceeded": False, "freeze_exceeded": False})


if __name__ == "__main__":
    unittest.main()
