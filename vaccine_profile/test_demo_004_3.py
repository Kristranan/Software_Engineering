# Tests for demo_004_3.py (004-3 demo for the Sprint Review).
# No hardware, clock or network: every test uses a temporary folder.
import os
import tempfile
import unittest

import demo_004_3 as demo


class DemoTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "profile.json")

    def tearDown(self):
        self.dir.cleanup()

    def write_raw(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    # TC14
    def test_verdict_names_each_side_with_its_own_result(self):
        self.write_raw('{"heat_limit_s": 119, "freeze_limit_s": 120}')
        self.assertEqual(demo.verdict(120, 120, self.path),
                         "heat: EXCEEDED, freeze: within limit")

    # TC15
    def test_broken_profile_shows_unknown_never_safe(self):
        self.write_raw('{"heat_limit_s": 119}')
        text = demo.verdict(0, 0, self.path)
        self.assertTrue(text.startswith("UNKNOWN"), text)
        self.assertNotIn("within limit", text)


if __name__ == "__main__":
    unittest.main()
