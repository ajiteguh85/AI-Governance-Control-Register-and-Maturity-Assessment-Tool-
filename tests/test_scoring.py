"""Tests for scoring algorithms and heat map generation."""

import unittest

from ai_governance.models import (
    AssessmentResult,
    GovernanceControl,
    GovernanceDomain,
)
from ai_governance.scoring import (
    compute_domain_scores,
    compute_gap_analysis,
    generate_heat_map_data,
    rank_domains,
    render_text_heat_map,
)


def _make_assessment() -> AssessmentResult:
    c1 = GovernanceControl("C1", "Ctrl1", "D", "D1", score=2)
    c2 = GovernanceControl("C2", "Ctrl2", "D", "D1", score=4)
    c3 = GovernanceControl("C3", "Ctrl3", "D", "D2", score=5)
    d1 = GovernanceDomain("D1", "Domain1", "Desc", [c1, c2])
    d2 = GovernanceDomain("D2", "Domain2", "Desc", [c3])
    return AssessmentResult("A1", "TestOrg", "TestFramework", [d1, d2])


class TestComputeDomainScores(unittest.TestCase):
    def test_scores(self):
        result = _make_assessment()
        scores = compute_domain_scores(result)
        self.assertAlmostEqual(scores["D1"], 3.0)
        self.assertAlmostEqual(scores["D2"], 5.0)


class TestGapAnalysis(unittest.TestCase):
    def test_gap_below_target(self):
        result = _make_assessment()
        gaps = compute_gap_analysis(result, target_level=4)
        self.assertAlmostEqual(gaps["D1"]["gap"], 1.0)
        self.assertFalse(gaps["D1"]["meets_target"])

    def test_gap_meets_target(self):
        result = _make_assessment()
        gaps = compute_gap_analysis(result, target_level=3)
        self.assertTrue(gaps["D1"]["meets_target"])
        self.assertTrue(gaps["D2"]["meets_target"])


class TestHeatMapData(unittest.TestCase):
    def test_heat_map_entries(self):
        result = _make_assessment()
        hm = generate_heat_map_data(result)
        self.assertEqual(len(hm), 3)
        severities = {e["severity"] for e in hm}
        self.assertTrue(severities.issubset({"critical", "warning", "acceptable", "strong"}))


class TestTextHeatMap(unittest.TestCase):
    def test_renders_without_error(self):
        result = _make_assessment()
        text = render_text_heat_map(result)
        self.assertIn("TestOrg", text)
        self.assertIn("Domain1", text)


class TestRankDomains(unittest.TestCase):
    def test_ranking_order(self):
        result = _make_assessment()
        ranked = rank_domains(result)
        self.assertEqual(ranked[0].domain_id, "D1")
        self.assertEqual(ranked[1].domain_id, "D2")


if __name__ == "__main__":
    unittest.main()
