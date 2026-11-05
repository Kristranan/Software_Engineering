# Tests for freeze_increment_s (004-2, rule R1 in FREEZE_DESIGN.md).
# No hardware, clock or network: records are plain dicts made up in the test.
import copy
import unittest

from freeze_exposure import freeze_increment_s, is_good_reading

LIMIT = 2.0


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
        self.assertTrue(is_good_reading(reading(0, 4.0)))
        self.assertTrue(is_good_reading(reading(0, -1)))

    def test_not_good(self):
        self.assertFalse(is_good_reading(None))
        self.assertFalse(is_good_reading(failed(0)))
        self.assertFalse(is_good_reading(dict(reading(0, 4.0), temp_c=None)))
        self.assertFalse(is_good_reading(dict(reading(0, 4.0), temp_c=True)))
        self.assertFalse(is_good_reading(dict(reading(0, 4.0), ok=1)))


class FreezeIncrementTest(unittest.TestCase):
    def test_first_reading_adds_nothing(self):
        self.assertEqual(freeze_increment_s(None, reading(0, 0.5), LIMIT), 0)

    def test_earlier_reading_below_limit_counts_the_whole_gap(self):
        self.assertEqual(freeze_increment_s(reading(300, 1.5), reading(600, 0.5), LIMIT), 300)

    def test_counted_by_the_earlier_reading_not_the_new_one(self):
        # Earlier 4.0 (not freeze), new 1.5 (freeze): nothing yet.
        self.assertEqual(freeze_increment_s(reading(0, 4.0), reading(300, 1.5), LIMIT), 0)
        # Earlier 0.5 (freeze), new 3.0 (warm again): the gap still counts.
        self.assertEqual(freeze_increment_s(reading(600, 0.5), reading(900, 3.0), LIMIT), 300)

    def test_exactly_at_limit_is_not_freeze(self):
        self.assertEqual(freeze_increment_s(reading(0, 2.0), reading(300, 2.0), LIMIT), 0)
        self.assertEqual(freeze_increment_s(reading(0, 1.9), reading(300, 2.0), LIMIT), 300)

    def test_too_warm_is_not_freeze(self):
        self.assertEqual(freeze_increment_s(reading(0, 9.0), reading(300, 4.0), LIMIT), 0)

    def test_uses_the_limit_it_is_given(self):
        self.assertEqual(freeze_increment_s(reading(0, 1.0), reading(300, 1.0), 0.0), 0)
        self.assertEqual(freeze_increment_s(reading(0, -0.6), reading(300, 1.0), -0.5), 300)

    def test_gap_follows_timestamps_not_interval(self):
        self.assertEqual(freeze_increment_s(reading(0, 1.0), reading(60, 1.0), LIMIT), 60)
        self.assertEqual(freeze_increment_s(reading(0, 1.0), reading(7200, 1.0), LIMIT), 7200)

    def test_failed_read_adds_nothing(self):
        self.assertEqual(freeze_increment_s(reading(0, 0.5), failed(300), LIMIT), 0)

    def test_last_good_must_be_good(self):
        self.assertEqual(freeze_increment_s(failed(0), reading(300, 0.5), LIMIT), 0)

    def test_gap_over_failed_reads_counted_at_next_good_reading(self):
        # 0.5 at 0, failed at 300 and 600, good at 900: last good is still the 0.5.
        self.assertEqual(freeze_increment_s(reading(0, 0.5), reading(900, 4.0), LIMIT), 900)

    def test_same_timestamp_adds_nothing(self):
        self.assertEqual(freeze_increment_s(reading(300, 0.5), reading(300, 0.5), LIMIT), 0)

    def test_time_going_backwards_adds_nothing(self):
        # After a power cut without an RTC, the clock can restart.
        self.assertEqual(freeze_increment_s(reading(5000, 0.5), reading(10, 0.5), LIMIT), 0)

    def test_result_is_never_negative_and_always_int(self):
        temps = (-5.0, 0.5, 1.9, 2.0, 4.0, 9.0)
        times = (0, 1, 300, -300)
        for t1 in temps:
            for t2 in temps:
                for dt in times:
                    added = freeze_increment_s(reading(1000, t1), reading(1000 + dt, t2), LIMIT)
                    self.assertIsInstance(added, int)
                    self.assertGreaterEqual(added, 0)

    def test_does_not_change_its_inputs(self):
        a, b = reading(0, 0.5), reading(300, 1.0)
        a0, b0 = copy.deepcopy(a), copy.deepcopy(b)
        freeze_increment_s(a, b, LIMIT)
        self.assertEqual((a, b), (a0, b0))

    def test_design_example_adds_up_to_600_and_warming_never_lowers_it(self):
        # The table in FREEZE_DESIGN.md section 2 (interval_s = 300).
        temps = (4.0, 1.5, 0.5, 3.0, 9.0, 4.0)
        expected_total = (0, 0, 300, 600, 600, 600)
        last_good, total = None, 0
        for i, temp in enumerate(temps):
            record = reading(i * 300, temp)
            total += freeze_increment_s(last_good, record, LIMIT)
            self.assertEqual(total, expected_total[i], "at timestamp_s %d" % (i * 300))
            last_good = record


if __name__ == "__main__":
    unittest.main()
