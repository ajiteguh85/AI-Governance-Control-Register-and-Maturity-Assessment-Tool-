"""Tests for validation routines and deployment test protocols."""

import unittest

from ai_governance.models import (
    AIUseCase,
    AssessmentResult,
    GovernanceControl,
    GovernanceDomain,
    RiskLevel,
    UseCaseStatus,
)
from ai_governance.validation import (
    create_standard_test_protocol,
    render_protocol_report,
    validate_assessment,
    validate_control,
    validate_domain,
    validate_score_input,
    validate_test_protocol,
    validate_use_case,
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

    def test_negative_weight(self):
        ctrl = GovernanceControl("C1", "Name", "Desc", "D1", weight=-1.0)
        result = validate_control(ctrl)
        self.assertFalse(result.is_valid)


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


# ---------------------------------------------------------------------------
# AI-ML Use Case Validation
# ---------------------------------------------------------------------------

class TestValidateUseCase(unittest.TestCase):
    def test_valid_use_case(self):
        uc = AIUseCase(
            "UC1", "Test", "Desc", "Mining Ops", "safety",
            ai_techniques=["random_forest"], data_sources=["sensors"],
        )
        result = validate_use_case(uc)
        self.assertTrue(result.is_valid)

    def test_empty_id(self):
        uc = AIUseCase("", "Test", "Desc", "BU", "safety")
        result = validate_use_case(uc)
        self.assertFalse(result.is_valid)

    def test_nonstandard_category_warns(self):
        uc = AIUseCase(
            "UC1", "Test", "Desc", "BU", "custom_category",
            ai_techniques=["nn"], data_sources=["db"],
        )
        result = validate_use_case(uc)
        self.assertTrue(result.is_valid)  # warning only
        self.assertTrue(len(result.warnings) > 0)

    def test_no_techniques_warns(self):
        uc = AIUseCase("UC1", "Test", "Desc", "BU", "safety", data_sources=["db"])
        result = validate_use_case(uc)
        self.assertTrue(result.is_valid)
        self.assertTrue(any("technique" in w.message.lower() for w in result.warnings))

    def test_invalid_maturity_score(self):
        uc = AIUseCase("UC1", "Test", "Desc", "BU", "safety", maturity_score=7)
        result = validate_use_case(uc)
        self.assertFalse(result.is_valid)


# ---------------------------------------------------------------------------
# Deployment Test Protocol
# ---------------------------------------------------------------------------

class TestDeploymentTestProtocol(unittest.TestCase):
    def test_create_standard_protocol(self):
        protocol = create_standard_test_protocol(
            "TP-001", "UC-001", "TestModel", "1.0",
        )
        self.assertEqual(protocol.protocol_id, "TP-001")
        self.assertGreater(len(protocol.steps), 10)
        self.assertFalse(protocol.is_complete)

    def test_protocol_pass(self):
        protocol = create_standard_test_protocol(
            "TP-002", "UC-002", "Model", "1.0",
        )
        for step in protocol.steps:
            step.passed = True
        self.assertTrue(protocol.is_complete)
        self.assertTrue(protocol.is_passed)
        self.assertAlmostEqual(protocol.pass_rate, 1.0)

    def test_protocol_fail_mandatory(self):
        protocol = create_standard_test_protocol(
            "TP-003", "UC-003", "Model", "1.0",
        )
        for step in protocol.steps:
            step.passed = True
        # Fail a mandatory step
        protocol.steps[0].passed = False
        self.assertTrue(protocol.is_complete)
        self.assertFalse(protocol.is_passed)

    def test_protocol_completion_rate(self):
        protocol = create_standard_test_protocol(
            "TP-004", "UC-004", "Model", "1.0",
        )
        total = len(protocol.steps)
        protocol.steps[0].passed = True
        self.assertAlmostEqual(protocol.completion_rate, 1 / total)

    def test_render_report(self):
        protocol = create_standard_test_protocol(
            "TP-005", "UC-005", "SAG Mill Model", "2.0",
        )
        for step in protocol.steps:
            step.passed = True
        report = render_protocol_report(protocol)
        self.assertIn("SAG Mill Model", report)
        self.assertIn("PASS", report)
        self.assertIn("PASSED", report)

    def test_validate_protocol_incomplete(self):
        protocol = create_standard_test_protocol(
            "TP-006", "UC-006", "Model", "1.0",
        )
        result = validate_test_protocol(protocol)
        self.assertTrue(result.is_valid)  # warnings only
        self.assertTrue(len(result.warnings) > 0)

    def test_validate_protocol_failed(self):
        protocol = create_standard_test_protocol(
            "TP-007", "UC-007", "Model", "1.0",
        )
        for step in protocol.steps:
            step.passed = True
        protocol.steps[0].passed = False  # mandatory fail
        result = validate_test_protocol(protocol)
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
