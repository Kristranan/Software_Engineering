"""Run the actual flat board file layout with simulated sensor/time on CPython."""
import unittest

from demo_main import run_simulation


class BoxPipelineAcceptanceTest(unittest.TestCase):
    def test_offline_trip_stores_failures_compares_totals_and_restores_after_restart(self):
        result = run_simulation([9.0, 9.0, 1.0, 1.0, 4.0, "error", 4.0],
                                {"heat_limit_s": 119, "freeze_limit_s": 120}, restart=True)
        snapshots = result["snapshots"]
        self.assertEqual([s["freeze_s"] for s in snapshots], [0, 0, 0, 60, 120, 120, 120])
        self.assertEqual(snapshots[-1]["heat_s"], 120)
        self.assertEqual(snapshots[-1]["comparison"], {
            "status": "compared", "heat_exceeded": True, "freeze_exceeded": False,
        })
        self.assertEqual(snapshots[5]["comparison"]["status"], "unknown")
        self.assertEqual(result["restored"], {"heat_s": 120, "freeze_s": 120})
        self.assertEqual(result["after_restart"]["heat_s"], 120)
        self.assertEqual(result["after_restart"]["freeze_s"], 120)
        self.assertEqual(result["after_restart"]["comparison"]["status"], "compared")
        self.assertEqual(len(result["stored"]), 8)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["stored"], result["serial"])
        self.assertFalse(result["stored"][5]["ok"])
        self.assertEqual(result["stored"][5]["error"], "sensor_timeout")
        self.assertEqual(result["saved_heat_s"], 120)
        self.assertEqual(result["saved_freeze_s"], 120)

    def test_each_saved_total_below_at_and_above_its_own_profile_limit(self):
        for heat_s in (58, 59, 60):
            for freeze_s in (58, 59, 60):
                with self.subTest(heat_s=heat_s, freeze_s=freeze_s):
                    result = run_simulation([4.0], {
                        "heat_limit_s": 59, "freeze_limit_s": 59,
                    }, initial_heat_s=heat_s, initial_freeze_s=freeze_s)
                    snapshot = result["snapshots"][0]
                    self.assertEqual(snapshot["heat_s"], heat_s)
                    self.assertEqual(snapshot["freeze_s"], freeze_s)
                    self.assertEqual(snapshot["comparison"], {
                        "status": "compared",
                        "heat_exceeded": heat_s == 60,
                        "freeze_exceeded": freeze_s == 60,
                    })

    def test_broken_profile_is_unknown_and_readings_are_still_stored(self):
        result = run_simulation([4.0, 4.0], {"heat_limit_s": 59})
        self.assertEqual(len(result["stored"]), 2)
        for snapshot in result["snapshots"]:
            self.assertEqual(snapshot["comparison"]["status"], "unknown")
            self.assertIsNone(snapshot["comparison"]["heat_exceeded"])
            self.assertIsNone(snapshot["comparison"]["freeze_exceeded"])


if __name__ == "__main__":
    unittest.main()
