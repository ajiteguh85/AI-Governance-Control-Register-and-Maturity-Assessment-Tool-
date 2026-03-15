"""Tests for the assessment engine with template loading."""

import unittest
from pathlib import Path

from ai_governance.assessment import build_assessment_from_template, run_assessment

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


if __name__ == "__main__":
    unittest.main()
