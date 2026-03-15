"""Tests for data models."""

import unittest

from ai_governance.models import (
    AssessmentResult,
    GovernanceControl,
    GovernanceDomain,
    MaturityLevel,
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


class TestAssessmentResult(unittest.TestCase):
    def test_overall_score(self):
        c1 = GovernanceControl("C1", "A", "D", "D1", score=2)
        c2 = GovernanceControl("C2", "B", "D", "D2", score=4)
        d1 = GovernanceDomain("D1", "Dom1", "D", [c1])
        d2 = GovernanceDomain("D2", "Dom2", "D", [c2])
        result = AssessmentResult("A1", "Org", "Framework", [d1, d2])
        self.assertAlmostEqual(result.overall_score, 3.0)


if __name__ == "__main__":
    unittest.main()
