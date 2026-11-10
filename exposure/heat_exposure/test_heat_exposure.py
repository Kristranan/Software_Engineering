# Tests for heat_increment_s (004-1, mirroring rule R1 in FREEZE_DESIGN.md).
# No hardware, clock or network: records are plain dicts made up in the test.
import copy
import unittest

from heat_exposure import heat_increment_s, is_good_reading

LIMIT = 8.0


def reading(ts, temp_c):
    """A good reading, shaped like the records Scheduler emits."""
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 1,
            "timestamp_s": ts, "temp_c": temp_c, "ok": True, "error": None}


def failed(ts):
    """A failed read: ok is False and temp_c is None."""
    return {"device_id": "BOX-001", "shipment_id": "SHP-1001", "seq": 1,
            "timestamp_s": ts, "temp_c": None, "ok": False, "error": "sensor_timeout"}


class IsGoodReadingTest(unittest.TestCase):
    def test_good_reading(self):
        self.assertTrue(is_good_reading(reading(0, 5.0)))
        self.assertTrue(is_good_reading(reading(0, 10.5)))

    def test_not_good(self):
        self.assertFalse(is_good_reading(None))
        self.assertFalse(is_good_reading(failed(0)))
        self.assertFalse(is_good_reading(dict(reading(0, 5.0), temp_c=None)))
        self.assertFalse(is_good_reading(dict(reading(0, 5.0), temp_c=True)))
        self.assertFalse(is_good_reading(dict(reading(0, 5.0), ok=1)))


class HeatIncrementTest(unittest.TestCase):
    def test_first_reading_adds_nothing(self):
        self.assertEqual(heat_increment_s(None, reading(0, 9.0), LIMIT), 0)

    def test_earlier_reading_above_limit_counts_the_whole_gap(self):
        self.assertEqual(heat_increment_s(reading(300, 9.0), reading(600, 5.0), LIMIT), 300)

    def test_counted_by_the_earlier_reading_not_the_new_one(self):
        # Earlier 5.0 (not heat), new 9.0 (heat): nothing yet.
        self.assertEqual(heat_increment_s(reading(0, 5.0), reading(300, 9.0), LIMIT), 0)
        # Earlier 9.0 (heat), new 5.0 (safe again): the gap still counts.
        self.assertEqual(heat_increment_s(reading(600, 9.0), reading(900, 5.0), LIMIT), 300)

    def test_exactly_at_limit_is_not_heat(self):
        self.assertEqual(heat_increment_s(reading(0, 8.0), reading(300, 8.0), LIMIT), 0)
        self.assertEqual(heat_increment_s(reading(0, 8.1), reading(300, 8.0), LIMIT), 300)

    def test_too_cold_is_not_heat(self):
        self.assertEqual(heat_increment_s(reading(0, 2.0), reading(300, 5.0), LIMIT), 0)

    def test_uses_the_limit_it_is_given(self):
        self.assertEqual(heat_increment_s(reading(0, 7.0), reading(300, 5.0), 8.0), 0)
        self.assertEqual(heat_increment_s(reading(0, 8.5), reading(300, 5.0), 8.0), 300)

    def test_gap_follows_timestamps_not_interval(self):
        self.assertEqual(heat_increment_s(reading(0, 9.0), reading(60, 5.0), LIMIT), 60)
        self.assertEqual(heat_increment_s(reading(0, 9.0), reading(7200, 5.0), LIMIT), 7200)

    def test_failed_read_adds_nothing(self):
        self.assertEqual(heat_increment_s(reading(0, 9.0), failed(300), LIMIT), 0)

    def test_last_good_must_be_good(self):
        self.assertEqual(heat_increment_s(failed(0), reading(300, 9.0), LIMIT), 0)

    def test_gap_over_failed_reads_counted_at_next_good_reading(self):
        # 9.0 at 0, failed at 300 and 600, good at 900: last good is still the 9.0.
        self.assertEqual(heat_increment_s(reading(0, 9.0), reading(900, 5.0), LIMIT), 900)

    def test_same_timestamp_adds_nothing(self):
        self.assertEqual(heat_increment_s(reading(300, 9.0), reading(300, 5.0), LIMIT), 0)

    def test_time_going_backwards_adds_nothing(self):
        # After a power cut without an RTC, the clock can restart.
        self.assertEqual(heat_increment_s(reading(5000, 9.0), reading(10, 5.0), LIMIT), 0)

    def test_result_is_never_negative_and_always_int(self):
        temps = (2.0, 5.0, 8.0, 8.1, 10.0, 15.0)
        times = (0, 1, 300, -300)
        for t1 in temps:
            for t2 in temps:
                for dt in times:
                    added = heat_increment_s(reading(1000, t1), reading(1000 + dt, t2), LIMIT)
                    self.assertIsInstance(added, int)
                    self.assertGreaterEqual(added, 0)

    def test_does_not_change_its_inputs(self):
        a, b = reading(0, 9.0), reading(300, 5.0)
        a0, b0 = copy.deepcopy(a), copy.deepcopy(b)
        heat_increment_s(a, b, LIMIT)
        self.assertEqual((a, b), (a0, b0))

    def test_design_example_adds_up_to_600_and_cooling_never_lowers_it(self):
        temps = (5.0, 9.0, 10.0, 7.0, 4.0, 9.0)
        expected_total = (0, 0, 300, 600, 600, 600)
        last_good, total = None, 0
        for i, temp in enumerate(temps):
            record = reading(i * 300, temp)
            total += heat_increment_s(last_good, record, LIMIT)
            self.assertEqual(total, expected_total[i], "at timestamp_s %d" % (i * 300))
            last_good = record


if __name__ == "__main__":
    unittest.main()