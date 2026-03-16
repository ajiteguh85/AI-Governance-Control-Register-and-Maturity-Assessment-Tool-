"""Tests for data models."""

import unittest

from ai_governance.models import (
    AIUseCase,
    AssessmentResult,
    GovernanceControl,
    GovernanceDomain,
    MaturityLevel,
    RiskLevel,
    SafetyIncidentRecord,
    UseCaseStatus,
)


class TestMaturityLevel(unittest.TestCase):
    def test_values(self):
        self.assertEqual(MaturityLevel.INITIAL, 1)
        self.assertEqual(MaturityLevel.OPTIMIZING, 5)


class TestGovernanceControl(unittest.TestCase):
    def test_maturity_level_with_score(self):
        ctrl = GovernanceControl("C1", "Test", "Desc", "D1", score=3)
        self.assertEqual(ctrl.maturity_level, MaturityLevel.DEFINED)

    def test_maturity_level_without_score(self):
        ctrl = GovernanceControl("C1", "Test", "Desc", "D1")
        self.assertIsNone(ctrl.maturity_level)

    def test_maturity_level_clamped(self):
        ctrl = GovernanceControl("C1", "Test", "Desc", "D1", score=0)
        self.assertEqual(ctrl.maturity_level, MaturityLevel.INITIAL)

    def test_weighted_score(self):
        ctrl = GovernanceControl("C1", "Test", "Desc", "D1", score=3, weight=2.0)
        self.assertAlmostEqual(ctrl.weighted_score, 6.0)

    def test_weighted_score_none(self):
        ctrl = GovernanceControl("C1", "Test", "Desc", "D1")
        self.assertIsNone(ctrl.weighted_score)


class TestGovernanceDomain(unittest.TestCase):
    def test_average_score(self):
        controls = [
            GovernanceControl("C1", "A", "D", "D1", score=2),
            GovernanceControl("C2", "B", "D", "D1", score=4),
        ]
        domain = GovernanceDomain("D1", "Test", "Desc", controls)
        self.assertAlmostEqual(domain.average_score, 3.0)

    def test_average_score_no_scores(self):
        domain = GovernanceDomain("D1", "Test", "Desc", [])
        self.assertIsNone(domain.average_score)

    def test_completion_rate(self):
        controls = [
            GovernanceControl("C1", "A", "D", "D1", score=2),
            GovernanceControl("C2", "B", "D", "D1"),
        ]
        domain = GovernanceDomain("D1", "Test", "Desc", controls)
        self.assertAlmostEqual(domain.completion_rate, 0.5)

    def test_weighted_average(self):
        controls = [
            GovernanceControl("C1", "A", "D", "D1", score=2, weight=1.0),
            GovernanceControl("C2", "B", "D", "D1", score=4, weight=3.0),
        ]
        domain = GovernanceDomain("D1", "Test", "Desc", controls)
        # (2*1 + 4*3) / (1+3) = 14/4 = 3.5
        self.assertAlmostEqual(domain.weighted_average_score, 3.5)


class TestAssessmentResult(unittest.TestCase):
    def test_overall_score(self):
        c1 = GovernanceControl("C1", "A", "D", "D1", score=2)
        c2 = GovernanceControl("C2", "B", "D", "D2", score=4)
        d1 = GovernanceDomain("D1", "Dom1", "D", [c1])
        d2 = GovernanceDomain("D2", "Dom2", "D", [c2])
        result = AssessmentResult("A1", "Org", "Framework", [d1, d2])
        self.assertAlmostEqual(result.overall_score, 3.0)

    def test_total_and_scored_controls(self):
        c1 = GovernanceControl("C1", "A", "D", "D1", score=2)
        c2 = GovernanceControl("C2", "B", "D", "D1")
        d1 = GovernanceDomain("D1", "Dom1", "D", [c1, c2])
        result = AssessmentResult("A1", "Org", "Framework", [d1])
        self.assertEqual(result.total_controls, 2)
        self.assertEqual(result.scored_controls, 1)


class TestAIUseCase(unittest.TestCase):
    def test_defaults(self):
        uc = AIUseCase("UC1", "Test", "Desc", "BU", "safety")
        self.assertEqual(uc.status, UseCaseStatus.PROPOSED)
        self.assertEqual(uc.risk_level, RiskLevel.MODERATE)
        self.assertEqual(uc.ai_techniques, [])

    def test_status_values(self):
        self.assertEqual(UseCaseStatus.PROPOSED, 1)
        self.assertEqual(UseCaseStatus.DEPLOYED, 4)

    def test_risk_values(self):
        self.assertEqual(RiskLevel.LOW, 1)
        self.assertEqual(RiskLevel.CRITICAL, 4)


class TestSafetyIncidentRecord(unittest.TestCase):
    def test_creation(self):
        inc = SafetyIncidentRecord("INC1", "UC1", "high", "Test incident")
        self.assertFalse(inc.is_resolved)
        self.assertEqual(inc.severity, "high")


if __name__ == "__main__":
    unittest.main()
