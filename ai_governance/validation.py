"""Validation routines to ensure data integrity of governance assessment inputs."""

from dataclasses import dataclass

from .models import AssessmentResult, GovernanceControl, GovernanceDomain


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
