"""Tests for scoring algorithms, heat map generation, and ML prediction."""

import unittest

from ai_governance.models import (
    AIUseCase,
    AssessmentResult,
    GovernanceControl,
    GovernanceDomain,
    RiskLevel,
    UseCaseStatus,
)
from ai_governance.scoring import (
    MaturityPredictor,
    compute_domain_scores,
    compute_gap_analysis,
    compute_use_case_priority_score,
    compute_weighted_domain_scores,
    generate_domain_heat_map,
    generate_heat_map_data,
    rank_domains,
    rank_use_cases,
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


class TestWeightedDomainScores(unittest.TestCase):
    def test_weighted(self):
        c1 = GovernanceControl("C1", "A", "D", "D1", score=2, weight=1.0)
        c2 = GovernanceControl("C2", "B", "D", "D1", score=4, weight=3.0)
        d1 = GovernanceDomain("D1", "Domain1", "Desc", [c1, c2])
        result = AssessmentResult("A1", "Org", "FW", [d1])
        scores = compute_weighted_domain_scores(result)
        self.assertAlmostEqual(scores["D1"], 3.5)


class TestGapAnalysis(unittest.TestCase):
    def test_gap_below_target(self):
        result = _make_assessment()
        gaps = compute_gap_analysis(result, target_level=4)
        self.assertAlmostEqual(gaps["D1"]["gap"], 1.0)
        self.assertFalse(gaps["D1"]["meets_target"])
        self.assertEqual(gaps["D1"]["priority"], "high")

    def test_gap_meets_target(self):
        result = _make_assessment()
        gaps = compute_gap_analysis(result, target_level=3)
        self.assertTrue(gaps["D1"]["meets_target"])
        self.assertTrue(gaps["D2"]["meets_target"])

    def test_critical_gap(self):
        c1 = GovernanceControl("C1", "A", "D", "D1", score=1)
        d1 = GovernanceDomain("D1", "D", "D", [c1])
        result = AssessmentResult("A1", "Org", "FW", [d1])
        gaps = compute_gap_analysis(result, target_level=4)
        self.assertEqual(gaps["D1"]["priority"], "critical")


class TestHeatMapData(unittest.TestCase):
    def test_heat_map_entries(self):
        result = _make_assessment()
        hm = generate_heat_map_data(result)
        self.assertEqual(len(hm), 3)
        severities = {e["severity"] for e in hm}
        self.assertTrue(severities.issubset({"critical", "warning", "acceptable", "strong"}))

    def test_domain_heat_map(self):
        result = _make_assessment()
        dhm = generate_domain_heat_map(result)
        self.assertEqual(len(dhm), 2)
        self.assertIn("completion_rate", dhm[0])
        self.assertIn("severity", dhm[0])


class TestTextHeatMap(unittest.TestCase):
    def test_renders_without_error(self):
        result = _make_assessment()
        text = render_text_heat_map(result)
        self.assertIn("TestOrg", text)
        self.assertIn("Domain1", text)
        self.assertIn("Controls Assessed", text)


class TestRankDomains(unittest.TestCase):
    def test_ranking_order(self):
        result = _make_assessment()
        ranked = rank_domains(result)
        self.assertEqual(ranked[0].domain_id, "D1")
        self.assertEqual(ranked[1].domain_id, "D2")


# ---------------------------------------------------------------------------
# ML Maturity Prediction Tests
# ---------------------------------------------------------------------------

class TestMaturityPredictor(unittest.TestCase):
    def test_fit_and_predict(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [1.5, 2.0, 2.5, 3.0])
        self.assertTrue(pred._fitted)
        self.assertGreater(pred.slope, 0)
        result = pred.predict(5)
        self.assertGreater(result, 3.0)

    def test_predict_clamped(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [4.0, 4.5, 4.8, 5.0])
        result = pred.predict(100)
        self.assertLessEqual(result, 5.0)

    def test_time_to_target(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [1.5, 2.0, 2.5, 3.0])
        t = pred.time_to_target(4.0)
        self.assertIsNotNone(t)
        self.assertGreater(t, 4)

    def test_time_to_target_unreachable(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [3.0, 2.5, 2.0, 1.5])
        t = pred.time_to_target(4.0)
        self.assertIsNone(t)

    def test_trend_direction(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(pred.trend_direction, "improving")

    def test_declining_trend(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [4.0, 3.0, 2.0, 1.0])
        self.assertEqual(pred.trend_direction, "declining")

    def test_r_squared(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(pred.r_squared, 1.0)

    def test_summary(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3], [1.0, 2.0, 3.0])
        s = pred.summary()
        self.assertIn("slope", s)
        self.assertIn("r_squared", s)
        self.assertTrue(s["fitted"])

    def test_predict_batch(self):
        pred = MaturityPredictor()
        pred.fit([1, 2, 3, 4], [1.0, 2.0, 3.0, 4.0])
        results = pred.predict_batch([5, 6, 7])
        self.assertEqual(len(results), 3)
        self.assertGreater(results[0], results[1] - 2)  # reasonable progression

    def test_insufficient_data(self):
        pred = MaturityPredictor()
        with self.assertRaises(ValueError):
            pred.fit([1], [2])

    def test_unfitted_predict(self):
        pred = MaturityPredictor()
        with self.assertRaises(RuntimeError):
            pred.predict(5)


# ---------------------------------------------------------------------------
# Use Case Priority Scoring Tests
# ---------------------------------------------------------------------------

class TestUseCasePriorityScoring(unittest.TestCase):
    def test_basic_scoring(self):
        uc = AIUseCase(
            "UC1", "Test", "Desc", "BU", "safety",
            status=UseCaseStatus.PILOTING,
            risk_level=RiskLevel.LOW,
            expected_benefit="safety improvement and cost_reduction",
            governance_controls=["C1", "C2", "C3"],
        )
        result = compute_use_case_priority_score(uc)
        self.assertIn("composite_score", result)
        self.assertGreater(result["composite_score"], 0)
        self.assertIn("recommendation", result)

    def test_rank_use_cases(self):
        uc1 = AIUseCase(
            "UC1", "Low", "Desc", "BU", "safety",
            status=UseCaseStatus.PROPOSED, risk_level=RiskLevel.CRITICAL,
        )
        uc2 = AIUseCase(
            "UC2", "High", "Desc", "BU", "safety",
            status=UseCaseStatus.DEPLOYED, risk_level=RiskLevel.LOW,
            expected_benefit="safety and cost_reduction",
            governance_controls=["C1", "C2", "C3", "C4", "C5"],
        )
        ranked = rank_use_cases([uc1, uc2])
        self.assertEqual(ranked[0]["use_case_id"], "UC2")
        self.assertGreater(ranked[0]["composite_score"], ranked[1]["composite_score"])

    def test_fast_track_recommendation(self):
        uc = AIUseCase(
            "UC1", "Great", "Desc", "BU", "safety",
            status=UseCaseStatus.DEPLOYED,
            risk_level=RiskLevel.LOW,
            expected_benefit="safety improvement",
            governance_controls=["C1", "C2", "C3", "C4", "C5"],
        )
        result = compute_use_case_priority_score(uc)
        self.assertIn("FAST-TRACK", result["recommendation"])


if __name__ == "__main__":
    unittest.main()
