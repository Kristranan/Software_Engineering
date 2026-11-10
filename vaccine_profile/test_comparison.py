import unittest

from comparison import compare_exposure

PROFILE = {
    "heat_limit_s": 7200,
    "freeze_limit_s": 1800,
}


class CompareExposureTest(unittest.TestCase):
    def test_heat_equal_to_limit_is_not_exceeded(self):
        result = compare_exposure(
            heat_s=7200,
            freeze_s=0,
            profile=PROFILE,
        )
        self.assertFalse(result["heat_exceeded"])

    def test_heat_above_limit_is_exceeded(self):
        result = compare_exposure(
            heat_s=7201,
            freeze_s=0,
            profile=PROFILE,
        )
        self.assertTrue(result["heat_exceeded"])

    def test_freeze_equal_to_limit_is_not_exceeded(self):
        result = compare_exposure(
            heat_s=0,
            freeze_s=1800,
            profile=PROFILE,
        )
        self.assertFalse(result["freeze_exceeded"])

    def test_freeze_above_limit_is_exceeded(self):
        result = compare_exposure(
            heat_s=0,
            freeze_s=1801,
            profile=PROFILE,
        )
        self.assertTrue(result["freeze_exceeded"])

    def test_heat_and_freeze_are_compared_independently(self):
        result = compare_exposure(
            heat_s=7201,   # เกิน limit 7200
            freeze_s=1800, # เท่ากับ limit 1800 จึงยังไม่เกิน
            profile=PROFILE,
        )

        self.assertTrue(result["heat_exceeded"])
        self.assertFalse(result["freeze_exceeded"])

if __name__ == "__main__":
    unittest.main()

