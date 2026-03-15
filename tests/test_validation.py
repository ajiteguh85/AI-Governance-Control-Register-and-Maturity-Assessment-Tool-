"""Tests for validation routines."""

import unittest

from ai_governance.models import (
    AssessmentResult,
    GovernanceControl,
    GovernanceDomain,
)
from ai_governance.validation import (
    validate_assessment,
    validate_control,
    validate_domain,
    validate_score_input,
)


class TestValidateControl(unittest.TestCase):
    def test_valid_control(self):
        ctrl = GovernanceControl("C1", "Name", "Desc", "D1", score=3, evidence="docs")
        result = validate_control(ctrl)
        self.assertTrue(result.is_valid)

    def test_empty_control_id(self):
        ctrl = GovernanceControl("", "Name", "Desc", "D1")
        result = validate_control(ctrl)
        self.assertFalse(result.is_valid)

    def test_score_out_of_range(self):
        ctrl = GovernanceControl("C1", "Name", "Desc", "D1", score=6)
        result = validate_control(ctrl)
        self.assertFalse(result.is_valid)

    def test_score_without_evidence_warns(self):
        ctrl = GovernanceControl("C1", "Name", "Desc", "D1", score=3)
        result = validate_control(ctrl)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 1)


class TestValidateDomain(unittest.TestCase):
    def test_duplicate_control_ids(self):
        c1 = GovernanceControl("C1", "A", "D", "D1")
        c2 = GovernanceControl("C1", "B", "D", "D1")
        domain = GovernanceDomain("D1", "Domain", "Desc", [c1, c2])
        result = validate_domain(domain)
        self.assertFalse(result.is_valid)

    def test_empty_controls_warns(self):
        domain = GovernanceDomain("D1", "Domain", "Desc", [])
        result = validate_domain(domain)
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)


class TestValidateAssessment(unittest.TestCase):
    def test_valid_assessment(self):
        ctrl = GovernanceControl("C1", "Name", "Desc", "D1", score=3, evidence="e")
        domain = GovernanceDomain("D1", "Domain", "Desc", [ctrl])
        assessment = AssessmentResult("A1", "Org", "Framework", [domain])
        result = validate_assessment(assessment)
        self.assertTrue(result.is_valid)

    def test_empty_domains(self):
        assessment = AssessmentResult("A1", "Org", "Framework", [])
        result = validate_assessment(assessment)
        self.assertFalse(result.is_valid)

    def test_empty_assessment_id(self):
        assessment = AssessmentResult("", "Org", "Framework", [])
        result = validate_assessment(assessment)
        self.assertFalse(result.is_valid)


class TestValidateScoreInput(unittest.TestCase):
    def test_valid_integer(self):
        valid, msg = validate_score_input(3)
        self.assertTrue(valid)

    def test_out_of_range(self):
        valid, msg = validate_score_input(7)
        self.assertFalse(valid)

    def test_boolean_rejected(self):
        valid, msg = validate_score_input(True)
        self.assertFalse(valid)

    def test_valid_string(self):
        valid, msg = validate_score_input("4")
        self.assertTrue(valid)

    def test_none_allowed(self):
        valid, msg = validate_score_input(None)
        self.assertTrue(valid)

    def test_float_with_decimal(self):
        valid, msg = validate_score_input(3.5)
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
