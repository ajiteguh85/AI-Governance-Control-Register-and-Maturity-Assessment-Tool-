"""Tests for the ESG & safety dashboard module."""

import unittest
from pathlib import Path

from ai_governance.assessment import build_assessment_from_template
from ai_governance.dashboard import (
    generate_esg_kpi_data,
    generate_executive_summary,
    generate_safety_dashboard_data,
    render_text_dashboard,
)
from ai_governance.mining_use_cases import get_mining_use_case_catalogue
from ai_governance.models import SafetyIncidentRecord

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

ESG_SCORES = {
    "ESG-E-01": 4, "ESG-E-02": 3, "ESG-E-03": 2, "ESG-E-04": 3,
    "ESG-S-01": 3, "ESG-S-02": 3, "ESG-S-03": 2, "ESG-S-04": 3,
    "ESG-G-01": 4, "ESG-G-02": 3, "ESG-G-03": 3, "ESG-G-04": 2,
    "ESG-I-01": 3, "ESG-I-02": 2, "ESG-I-03": 3,
}


def _make_esg_assessment():
    return build_assessment_from_template(
        TEMPLATES_DIR / "esg_ai_monitoring_template.json",
        "TEST-ESG-001", "TestMiningCorp", ESG_SCORES,
    )


def _make_incidents():
    return [
        SafetyIncidentRecord("INC-001", "UC1", "medium", "False positive alert"),
        SafetyIncidentRecord("INC-002", "UC2", "high", "Sensor miscalibration", is_resolved=True),
        SafetyIncidentRecord("INC-003", "UC1", "low", "Delayed prediction", is_resolved=True),
    ]


class TestExecutiveSummary(unittest.TestCase):
    def test_basic_summary(self):
        assessment = _make_esg_assessment()
        summary = generate_executive_summary(assessment)
        self.assertIn("overall_maturity", summary)
        self.assertIn("domain_summary", summary)
        self.assertIn("gap_analysis", summary)
        self.assertEqual(summary["organization"], "TestMiningCorp")

    def test_with_use_cases(self):
        assessment = _make_esg_assessment()
        use_cases = get_mining_use_case_catalogue()
        summary = generate_executive_summary(assessment, use_cases)
        self.assertIn("ai_use_cases", summary)
        self.assertGreater(summary["ai_use_cases"]["total_use_cases"], 0)

    def test_with_incidents(self):
        assessment = _make_esg_assessment()
        incidents = _make_incidents()
        summary = generate_executive_summary(assessment, incidents=incidents)
        self.assertIn("safety_overview", summary)
        self.assertEqual(summary["safety_overview"]["total_incidents"], 3)


class TestESGKPIs(unittest.TestCase):
    def test_esg_pillars(self):
        assessment = _make_esg_assessment()
        kpis = generate_esg_kpi_data(assessment)
        self.assertIn("esg_pillars", kpis)
        self.assertIn("overall_esg_score", kpis)

    def test_esg_pillar_scores(self):
        assessment = _make_esg_assessment()
        kpis = generate_esg_kpi_data(assessment)
        pillars = kpis["esg_pillars"]
        # ESG template should map to at least environmental and social
        self.assertTrue(len(pillars) >= 2)


class TestSafetyDashboard(unittest.TestCase):
    def test_safety_dashboard(self):
        use_cases = get_mining_use_case_catalogue()
        incidents = _make_incidents()
        data = generate_safety_dashboard_data(use_cases, incidents)
        self.assertIn("safety_ai_use_cases", data)
        self.assertIn("incident_tracking", data)
        self.assertIn("critical_alerts", data)

    def test_safety_use_case_count(self):
        use_cases = get_mining_use_case_catalogue()
        incidents = []
        data = generate_safety_dashboard_data(use_cases, incidents)
        self.assertGreater(data["safety_ai_use_cases"]["total_safety_related"], 0)


class TestTextDashboard(unittest.TestCase):
    def test_renders(self):
        assessment = _make_esg_assessment()
        use_cases = get_mining_use_case_catalogue()
        incidents = _make_incidents()
        text = render_text_dashboard(assessment, use_cases, incidents)
        self.assertIn("TestMiningCorp", text)
        self.assertIn("MATURITY OVERVIEW", text)
        self.assertIn("DOMAIN HEAT MAP", text)
        self.assertIn("AI-ML USE CASE PORTFOLIO", text)
        self.assertIn("SAFETY INCIDENT OVERVIEW", text)

    def test_renders_without_optional(self):
        assessment = _make_esg_assessment()
        text = render_text_dashboard(assessment)
        self.assertIn("TestMiningCorp", text)
        self.assertNotIn("AI-ML USE CASE PORTFOLIO", text)


if __name__ == "__main__":
    unittest.main()
