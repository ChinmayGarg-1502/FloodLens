
import unittest
from datetime import datetime, timezone, timedelta

from intelligence import (
    is_outdated,
    calculate_trust_score,
    classify_hazard_risk,
    verify_report
)

from hotspots import find_hotspots


class TestFloodLens(unittest.TestCase):

    def test_new_report_is_not_outdated(self):
        now = datetime.now(timezone.utc).isoformat()
        self.assertFalse(is_outdated(now))

    def test_old_report_is_outdated(self):
        old_time = (
            datetime.now(timezone.utc) - timedelta(hours=72)
        ).isoformat()
        self.assertTrue(is_outdated(old_time))

    def test_trust_score(self):
        score = calculate_trust_score(
            confirmations=4,
            disputes=1,
            has_photo=True
        )
        self.assertEqual(score, 62)

    def test_high_severity_risk(self):
        result = classify_hazard_risk(
            severity="high",
            trust_score=62,
            confirmations=4
        )
        self.assertEqual(result["risk_level"], "HIGH")

    def test_community_verification(self):
        result = verify_report(confirmations=4, disputes=1)
        self.assertEqual(
            result["verification_status"],
            "COMMUNITY_SUPPORTED"
        )

    def test_hotspot_detection(self):
        reports = [
            {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "hazard_type": "pothole"
            },
            {
                "latitude": 28.6140,
                "longitude": 77.2091,
                "hazard_type": "pothole"
            },
            {
                "latitude": 28.6141,
                "longitude": 77.2092,
                "hazard_type": "waterlogging"
            }
        ]

        hotspots = find_hotspots(
            reports,
            radius_meters=500,
            min_reports=3
        )

        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0]["report_count"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

