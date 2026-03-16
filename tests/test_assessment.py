"""Tests for the assessment engine with template loading and maturity prediction."""

import unittest
from pathlib import Path

from ai_governance.assessment import (
    build_assessment_from_template,
    run_assessment,
    run_maturity_prediction,
)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class TestBuildFromTemplate(unittest.TestCase):
    def test_iso_42001_template(self):
        path = TEMPLATES_DIR / "iso_42001_template.json"
        result = build_assessment_from_template(path, "TEST-001", "TestCorp")
        self.assertEqual(result.framework, "ISO/IEC 42001 AI Management Systems")
        self.assertEqual(len(result.domains), 7)
        self.assertIsNone(result.overall_score)

    def test_esg_template(self):
        path = TEMPLATES_DIR / "esg_ai_monitoring_template.json"
        result = build_assessment_from_template(path, "TEST-002", "GreenCorp")
        self.assertEqual(result.framework, "AI-Based ESG Monitoring Governance")
        self.assertEqual(len(result.domains), 4)

    def test_with_scores(self):
        path = TEMPLATES_DIR / "iso_42001_template.json"
        scores = {"D1-C01": 3, "D1-C02": 4, "D1-C03": 2}
        result = build_assessment_from_template(path, "TEST-003", "ScoredCorp", scores)
        d1 = result.domains[0]
        self.assertAlmostEqual(d1.average_score, 3.0)

    def test_controls_count(self):
        path = TEMPLATES_DIR / "iso_42001_template.json"
        result = build_assessment_from_template(path, "TEST-004", "Corp")
        self.assertEqual(result.total_controls, 21)
        self.assertEqual(result.scored_controls, 0)


class TestRunAssessment(unittest.TestCase):
    def test_full_run_iso(self):
        scores = {
            "D1-C01": 3, "D1-C02": 4, "D1-C03": 2,
            "D2-C01": 3, "D2-C02": 3, "D2-C03": 4,
            "D3-C01": 2, "D3-C02": 2, "D3-C03": 3,
            "D4-C01": 4, "D4-C02": 3, "D4-C03": 3,
            "D5-C01": 3, "D5-C02": 2, "D5-C03": 3, "D5-C04": 2,
            "D6-C01": 4, "D6-C02": 3, "D6-C03": 3,
            "D7-C01": 3, "D7-C02": 4,
        }
        report = run_assessment("iso_42001_template.json", "RUN-001", "AcmeCorp", scores)
        self.assertTrue(report["is_valid"])
        self.assertIsNotNone(report["overall_score"])
        self.assertIn("heat_map_data", report)
        self.assertIn("text_heat_map", report)
        self.assertIn("AcmeCorp", report["text_heat_map"])
        self.assertIn("domain_heat_map", report)
        self.assertIn("weighted_domain_scores", report)
        self.assertEqual(report["controls_assessed"], 21)
        self.assertEqual(report["controls_total"], 21)

    def test_full_run_esg(self):
        scores = {
            "ESG-E-01": 4, "ESG-E-02": 3, "ESG-E-03": 2, "ESG-E-04": 3,
            "ESG-S-01": 2, "ESG-S-02": 3, "ESG-S-03": 2, "ESG-S-04": 3,
            "ESG-G-01": 4, "ESG-G-02": 3, "ESG-G-03": 3, "ESG-G-04": 2,
            "ESG-I-01": 3, "ESG-I-02": 2, "ESG-I-03": 3,
        }
        report = run_assessment("esg_ai_monitoring_template.json", "RUN-002", "GreenCorp", scores)
        self.assertTrue(report["is_valid"])
        self.assertIsNotNone(report["overall_score"])

    def test_custom_target_level(self):
        scores = {"D1-C01": 3, "D1-C02": 4, "D1-C03": 3}
        report = run_assessment("iso_42001_template.json", "RUN-003", "Corp", scores, target_level=5)
        for gap in report["gap_analysis"].values():
            if gap["current_score"] < 5:
                self.assertFalse(gap["meets_target"])


class TestMaturityPrediction(unittest.TestCase):
    def test_prediction_output(self):
        historical = [(1, 1.5), (2, 2.0), (3, 2.5), (4, 3.0)]
        result = run_maturity_prediction(historical, forecast_periods=3, target_level=4.0)
        self.assertIn("model_summary", result)
        self.assertIn("forecasts", result)
        self.assertEqual(len(result["forecasts"]), 3)
        self.assertIsNotNone(result["time_to_target"])

    def test_prediction_improving_trend(self):
        historical = [(1, 1.0), (2, 2.0), (3, 3.0), (4, 4.0)]
        result = run_maturity_prediction(historical)
        self.assertEqual(result["model_summary"]["trend"], "improving")

    def test_prediction_forecasts_bounded(self):
        historical = [(1, 4.0), (2, 4.5), (3, 4.8), (4, 5.0)]
        result = run_maturity_prediction(historical, forecast_periods=10)
        for f in result["forecasts"]:
            self.assertLessEqual(f["predicted_score"], 5.0)
            self.assertGreaterEqual(f["predicted_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
