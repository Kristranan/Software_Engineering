import unittest

from exposure_comparison import update_and_compare

class ExposureComparisonTest(unittest.TestCase):
  def test_heat_total_in_seconds_reaches_comparison(self):
    profile = {
      "heat_limit_s" : 59,
      "freeze_limit_s" : 120,
    }

    first = {"timestamp_s" : 0, "temp_c" : 9.0, "ok": True}
    second = {"timestamp_s": 60, "temp_c": 9.0, "ok": True}

    state, result = update_and_compare(
        None, first, profile,
        upper_limit_c=8.0,
        lower_limit_c=2.0,
    )

    state, result = update_and_compare(
        state, second, profile,
        upper_limit_c=8.0,
        lower_limit_c=2.0,
    )

    self.assertEqual(state["heat_s"], 60)
    self.assertEqual(state["freeze_s"], 0)
    self.assertTrue(result["heat_exceeded"])
    self.assertFalse(result["freeze_exceeded"])

  def test_freeze_total_in_seconds_reaches_comparison(self):
    profile = {
      "heat_limit_s": 120,
      "freeze_limit_s": 59,
    }

    first = {"timestamp_s": 0, "temp_c": 1.0, "ok": True}
    second = {"timestamp_s": 60, "temp_c": 1.0, "ok": True}

    state, result = update_and_compare(
        None, first, profile,
        upper_limit_c=8.0,
        lower_limit_c=2.0,
    )

    state, result = update_and_compare(
        state, second, profile,
        upper_limit_c=8.0,
        lower_limit_c=2.0,
    )

    self.assertEqual(state["heat_s"], 0)
    self.assertEqual(state["freeze_s"], 60)
    self.assertFalse(result["heat_exceeded"])
    self.assertTrue(result["freeze_exceeded"])

  def test_later_warming_does_not_cancel_freeze(self):
    profile = {
      "heat_limit_s": 59,
      "freeze_limit_s": 59,
    }

    readings = [
      {"timestamp_s": 0, "temp_c": 1.0, "ok": True},
      {"timestamp_s": 60, "temp_c": 9.0, "ok": True},
      {"timestamp_s": 120, "temp_c": 9.0, "ok": True},
    ]

    state = None

    for record in readings:
      state, result = update_and_compare(
          state, record, profile,
          upper_limit_c=8.0,
          lower_limit_c=2.0,
      )

    self.assertEqual(state["heat_s"], 60)
    self.assertEqual(state["freeze_s"], 60)
    self.assertTrue(result["heat_exceeded"])
    self.assertTrue(result["freeze_exceeded"])


if __name__ == "__main__":
    unittest.main()