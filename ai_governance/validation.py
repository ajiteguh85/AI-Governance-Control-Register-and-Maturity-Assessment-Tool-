"""Validation routines and testing protocols for AI governance assessments.

Ensures data integrity, reliability, and compliance readiness of governance
assessment inputs. Includes protocols for validating AI-ML model deployments.
"""

from dataclasses import dataclass, field
from typing import Any

from .models import AIUseCase, AssessmentResult, GovernanceControl, GovernanceDomain


@dataclass
class ValidationError:
    """A single validation error."""

    field: str
    message: str
    severity: str = "error"  # "error" or "warning"


class ValidationResult:
    """Collection of validation errors for an assessment."""

    def __init__(self) -> None:
        self.errors: list[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)

    @property
    def warnings(self) -> list[ValidationError]:
        return [e for e in self.errors if e.severity == "warning"]

    def add_error(self, field: str, message: str) -> None:
        self.errors.append(ValidationError(field=field, message=message, severity="error"))

    def add_warning(self, field: str, message: str) -> None:
        self.errors.append(ValidationError(field=field, message=message, severity="warning"))

    def __repr__(self) -> str:
        return f"ValidationResult(valid={self.is_valid}, errors={len(self.errors)})"


# ---------------------------------------------------------------------------
# Core governance validation
# ---------------------------------------------------------------------------

def validate_control(control: GovernanceControl) -> ValidationResult:
    """Validate a single governance control."""
    result = ValidationResult()

    if not control.control_id or not control.control_id.strip():
        result.add_error("control_id", "Control ID must not be empty.")

    if not control.name or not control.name.strip():
        result.add_error("name", "Control name must not be empty.")

    if not control.domain or not control.domain.strip():
        result.add_error("domain", "Control domain must not be empty.")

    if control.score is not None:
        if not isinstance(control.score, int):
            result.add_error("score", f"Score must be an integer, got {type(control.score).__name__}.")
        elif control.score < 1 or control.score > 5:
            result.add_error("score", f"Score must be between 1 and 5, got {control.score}.")

    if control.score is not None and not control.evidence.strip():
        result.add_warning("evidence", "Scored controls should include supporting evidence.")

    if control.weight <= 0:
        result.add_error("weight", f"Control weight must be positive, got {control.weight}.")

    return result


def validate_domain(domain: GovernanceDomain) -> ValidationResult:
    """Validate a governance domain and all its controls."""
    result = ValidationResult()

    if not domain.domain_id or not domain.domain_id.strip():
        result.add_error("domain_id", "Domain ID must not be empty.")

    if not domain.name or not domain.name.strip():
        result.add_error("name", "Domain name must not be empty.")

    if not domain.controls:
        result.add_warning("controls", f"Domain '{domain.domain_id}' has no controls.")

    seen_ids: set[str] = set()
    for control in domain.controls:
        if control.control_id in seen_ids:
            result.add_error(
                "control_id",
                f"Duplicate control ID '{control.control_id}' in domain '{domain.domain_id}'.",
            )
        seen_ids.add(control.control_id)

        ctrl_result = validate_control(control)
        result.errors.extend(ctrl_result.errors)

    return result


def validate_assessment(assessment: AssessmentResult) -> ValidationResult:
    """Validate a complete governance assessment."""
    result = ValidationResult()

    if not assessment.assessment_id or not assessment.assessment_id.strip():
        result.add_error("assessment_id", "Assessment ID must not be empty.")

    if not assessment.organization or not assessment.organization.strip():
        result.add_error("organization", "Organization name must not be empty.")

    if not assessment.framework or not assessment.framework.strip():
        result.add_error("framework", "Framework name must not be empty.")

    if not assessment.domains:
        result.add_error("domains", "Assessment must contain at least one domain.")

    seen_domain_ids: set[str] = set()
    for domain in assessment.domains:
        if domain.domain_id in seen_domain_ids:
            result.add_error(
                "domain_id",
                f"Duplicate domain ID '{domain.domain_id}' in assessment.",
            )
        seen_domain_ids.add(domain.domain_id)

        domain_result = validate_domain(domain)
        result.errors.extend(domain_result.errors)

    return result


def validate_score_input(value: object) -> tuple[bool, str]:
    """Validate a raw score input value before conversion.

    Returns (is_valid, error_message).
    """
    if value is None:
        return True, ""

    if isinstance(value, bool):
        return False, "Score must be an integer, not a boolean."

    if isinstance(value, int):
        if 1 <= value <= 5:
            return True, ""
        return False, f"Score must be between 1 and 5, got {value}."

    if isinstance(value, float):
        if value != int(value):
            return False, f"Score must be a whole number, got {value}."
        int_val = int(value)
        if 1 <= int_val <= 5:
            return True, ""
        return False, f"Score must be between 1 and 5, got {int_val}."

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return True, ""
        try:
            int_val = int(stripped)
        except ValueError:
            return False, f"Score must be a numeric value, got '{stripped}'."
        if 1 <= int_val <= 5:
            return True, ""
        return False, f"Score must be between 1 and 5, got {int_val}."

    return False, f"Unsupported score type: {type(value).__name__}."


# ---------------------------------------------------------------------------
# AI-ML use case validation
# ---------------------------------------------------------------------------

def validate_use_case(use_case: AIUseCase) -> ValidationResult:
    """Validate an AI-ML use case registration."""
    result = ValidationResult()

    if not use_case.use_case_id or not use_case.use_case_id.strip():
        result.add_error("use_case_id", "Use case ID must not be empty.")

    if not use_case.name or not use_case.name.strip():
        result.add_error("name", "Use case name must not be empty.")

    if not use_case.business_unit or not use_case.business_unit.strip():
        result.add_error("business_unit", "Business unit must not be specified.")

    if not use_case.category or not use_case.category.strip():
        result.add_error("category", "Use case category must not be empty.")

    valid_categories = {
        "predictive_maintenance", "process_optimization", "safety",
        "environmental_monitoring", "quality_control", "supply_chain",
        "workforce_analytics", "energy_management", "exploration",
        "autonomous_systems", "reporting", "compliance",
    }
    if use_case.category and use_case.category not in valid_categories:
        result.add_warning(
            "category",
            f"Category '{use_case.category}' is not in the standard set: {sorted(valid_categories)}.",
        )

    if use_case.maturity_score is not None:
        if not isinstance(use_case.maturity_score, int) or use_case.maturity_score < 1 or use_case.maturity_score > 5:
            result.add_error("maturity_score", "Maturity score must be an integer between 1 and 5.")

    if not use_case.ai_techniques:
        result.add_warning("ai_techniques", "Use case should specify at least one AI technique.")

    if not use_case.data_sources:
        result.add_warning("data_sources", "Use case should specify at least one data source.")

    return result


# ---------------------------------------------------------------------------
# AI-ML deployment testing & validation protocols
# ---------------------------------------------------------------------------

@dataclass
class TestProtocolStep:
    """A single step in a testing/validation protocol."""

    step_id: str
    name: str
    description: str
    validation_type: str  # "data_quality", "model_performance", "bias", "security", "integration"
    is_mandatory: bool = True
    passed: bool | None = None
    notes: str = ""


@dataclass
class DeploymentTestProtocol:
    """Testing and validation protocol for AI-ML model deployment.

    Ensures AI-ML applications meet quality, safety, and governance
    standards before production deployment — critical for mining/extractive
    industry AI systems where safety and reliability are paramount.
    """

    protocol_id: str
    use_case_id: str
    model_name: str
    model_version: str
    steps: list[TestProtocolStep] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return all(s.passed is not None for s in self.steps)

    @property
    def is_passed(self) -> bool:
        mandatory = [s for s in self.steps if s.is_mandatory]
        return all(s.passed is True for s in mandatory)

    @property
    def completion_rate(self) -> float:
        if not self.steps:
            return 0.0
        tested = sum(1 for s in self.steps if s.passed is not None)
        return tested / len(self.steps)

    @property
    def pass_rate(self) -> float:
        tested = [s for s in self.steps if s.passed is not None]
        if not tested:
            return 0.0
        return sum(1 for s in tested if s.passed) / len(tested)


def create_standard_test_protocol(
    protocol_id: str,
    use_case_id: str,
    model_name: str,
    model_version: str,
) -> DeploymentTestProtocol:
    """Create a standard AI-ML deployment test protocol.

    Returns a protocol with industry-standard validation steps covering
    data quality, model performance, bias/fairness, security, and integration.
    """
    steps = [
        TestProtocolStep(
            step_id="DQ-01",
            name="Input Data Completeness",
            description="Verify that all required input data fields are present and within expected ranges.",
            validation_type="data_quality",
        ),
        TestProtocolStep(
            step_id="DQ-02",
            name="Data Distribution Validation",
            description="Check that input data distribution matches training data profile (no significant drift).",
            validation_type="data_quality",
        ),
        TestProtocolStep(
            step_id="DQ-03",
            name="Outlier and Anomaly Check",
            description="Identify and flag statistical outliers that may affect model reliability.",
            validation_type="data_quality",
        ),
        TestProtocolStep(
            step_id="MP-01",
            name="Model Accuracy Benchmark",
            description="Validate model meets minimum accuracy thresholds on holdout test data.",
            validation_type="model_performance",
        ),
        TestProtocolStep(
            step_id="MP-02",
            name="Model Robustness Test",
            description="Test model performance under edge cases, noise, and adversarial inputs.",
            validation_type="model_performance",
        ),
        TestProtocolStep(
            step_id="MP-03",
            name="Performance Regression Check",
            description="Ensure new model version does not degrade performance vs. previous version.",
            validation_type="model_performance",
        ),
        TestProtocolStep(
            step_id="BF-01",
            name="Bias and Fairness Assessment",
            description="Evaluate model for demographic and operational bias across protected groups.",
            validation_type="bias",
        ),
        TestProtocolStep(
            step_id="BF-02",
            name="Explainability Validation",
            description="Verify model outputs can be explained and justified for governance reporting.",
            validation_type="bias",
        ),
        TestProtocolStep(
            step_id="SC-01",
            name="Data Privacy Compliance",
            description="Confirm model does not expose or leak sensitive/personal data.",
            validation_type="security",
        ),
        TestProtocolStep(
            step_id="SC-02",
            name="Access Control Verification",
            description="Validate that model API endpoints enforce proper authentication and authorization.",
            validation_type="security",
        ),
        TestProtocolStep(
            step_id="IT-01",
            name="System Integration Test",
            description="Verify model integrates correctly with upstream data sources and downstream consumers.",
            validation_type="integration",
        ),
        TestProtocolStep(
            step_id="IT-02",
            name="Failover and Recovery Test",
            description="Test graceful degradation and recovery procedures when model service is unavailable.",
            validation_type="integration",
        ),
        TestProtocolStep(
            step_id="IT-03",
            name="Monitoring and Alerting Validation",
            description="Confirm that model performance monitoring and alert mechanisms are operational.",
            validation_type="integration",
            is_mandatory=False,
        ),
    ]

    return DeploymentTestProtocol(
        protocol_id=protocol_id,
        use_case_id=use_case_id,
        model_name=model_name,
        model_version=model_version,
        steps=steps,
    )


def validate_test_protocol(protocol: DeploymentTestProtocol) -> ValidationResult:
    """Validate a deployment test protocol for completeness and correctness."""
    result = ValidationResult()

    if not protocol.protocol_id.strip():
        result.add_error("protocol_id", "Protocol ID must not be empty.")

    if not protocol.model_name.strip():
        result.add_error("model_name", "Model name must not be empty.")

    if not protocol.steps:
        result.add_error("steps", "Protocol must contain at least one test step.")

    if not protocol.is_complete:
        untested = [s.step_id for s in protocol.steps if s.passed is None]
        result.add_warning(
            "completion",
            f"Protocol is incomplete: {len(untested)} steps not yet tested ({', '.join(untested[:5])}).",
        )

    if protocol.is_complete and not protocol.is_passed:
        failed = [s.step_id for s in protocol.steps if s.is_mandatory and not s.passed]
        result.add_error(
            "mandatory_failures",
            f"Mandatory test steps failed: {', '.join(failed)}.",
        )

    return result


def render_protocol_report(protocol: DeploymentTestProtocol) -> str:
    """Render a text report of the test protocol results."""
    lines: list[str] = []
    lines.append(f"{'='*72}")
    lines.append(f"  AI-ML DEPLOYMENT TEST PROTOCOL REPORT")
    lines.append(f"  Protocol: {protocol.protocol_id}")
    lines.append(f"  Model: {protocol.model_name} v{protocol.model_version}")
    lines.append(f"  Use Case: {protocol.use_case_id}")
    lines.append(f"{'='*72}")

    status_icon = {True: "PASS", False: "FAIL", None: " -- "}
    grouped: dict[str, list[TestProtocolStep]] = {}
    for step in protocol.steps:
        grouped.setdefault(step.validation_type, []).append(step)

    type_labels = {
        "data_quality": "Data Quality",
        "model_performance": "Model Performance",
        "bias": "Bias & Fairness",
        "security": "Security & Privacy",
        "integration": "Integration",
    }

    for vtype, steps in grouped.items():
        label = type_labels.get(vtype, vtype.title())
        lines.append(f"\n  --- {label} ---")
        for step in steps:
            icon = status_icon[step.passed]
            mandatory = "*" if step.is_mandatory else " "
            lines.append(f"    [{icon}] {step.step_id:8s} {mandatory} {step.name}")
            if step.notes:
                lines.append(f"           Notes: {step.notes}")

    lines.append(f"\n{'='*72}")
    pct = f"{protocol.completion_rate*100:.0f}%"
    pass_pct = f"{protocol.pass_rate*100:.0f}%"
    overall = "PASSED" if protocol.is_passed else ("INCOMPLETE" if not protocol.is_complete else "FAILED")
    lines.append(f"  Completion: {pct}  |  Pass Rate: {pass_pct}  |  Result: {overall}")
    lines.append(f"  (* = mandatory step)")
    lines.append(f"{'='*72}")
    return "\n".join(lines)
