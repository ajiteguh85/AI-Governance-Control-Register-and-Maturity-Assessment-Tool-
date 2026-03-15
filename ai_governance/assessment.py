"""Core AI governance assessment engine.

Orchestrates loading templates, running assessments, scoring, validation,
and report generation.
"""

import json
from pathlib import Path
from typing import Any, Optional

from .models import AssessmentResult, GovernanceControl, GovernanceDomain
from .scoring import (
    compute_domain_scores,
    compute_gap_analysis,
    generate_heat_map_data,
    render_text_heat_map,
)
from .validation import validate_assessment

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def load_template(template_path: Path) -> list[dict[str, Any]]:
    """Load a governance assessment template from a JSON file."""
    with open(template_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["domains"]


def build_assessment_from_template(
    template_path: Path,
    assessment_id: str,
    organization: str,
    scores: Optional[dict[str, int]] = None,
) -> AssessmentResult:
    """Build an AssessmentResult from a template file and optional scores.

    Args:
        template_path: Path to the JSON template.
        assessment_id: Unique identifier for this assessment.
        organization: Name of the organization being assessed.
        scores: Optional mapping of control_id -> score (1-5).

    Returns:
        A fully populated AssessmentResult.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    framework = data.get("framework", "Unknown")
    scores = scores or {}

    domains: list[GovernanceDomain] = []
    for d in data["domains"]:
        controls: list[GovernanceControl] = []
        for c in d["controls"]:
            cid = c["control_id"]
            controls.append(
                GovernanceControl(
                    control_id=cid,
                    name=c["name"],
                    description=c["description"],
                    domain=d["domain_id"],
                    score=scores.get(cid),
                )
            )
        domains.append(
            GovernanceDomain(
                domain_id=d["domain_id"],
                name=d["name"],
                description=d["description"],
                controls=controls,
            )
        )

    return AssessmentResult(
        assessment_id=assessment_id,
        organization=organization,
        framework=framework,
        domains=domains,
    )


def run_assessment(
    template_name: str,
    assessment_id: str,
    organization: str,
    scores: dict[str, int],
) -> dict[str, Any]:
    """Run a complete governance assessment and return a structured report.

    Args:
        template_name: Filename of the template (e.g. "iso_42001_template.json").
        assessment_id: Unique assessment identifier.
        organization: Organization being assessed.
        scores: Mapping of control_id to maturity score (1-5).

    Returns:
        A dictionary containing the full assessment report.
    """
    template_path = TEMPLATES_DIR / template_name
    result = build_assessment_from_template(template_path, assessment_id, organization, scores)

    validation = validate_assessment(result)
    domain_scores = compute_domain_scores(result)
    gaps = compute_gap_analysis(result, target_level=3)
    heat_map = generate_heat_map_data(result)
    text_heat_map = render_text_heat_map(result)

    return {
        "assessment_id": assessment_id,
        "organization": organization,
        "framework": result.framework,
        "is_valid": validation.is_valid,
        "validation_errors": [
            {"field": e.field, "message": e.message, "severity": e.severity}
            for e in validation.errors
        ],
        "overall_score": round(result.overall_score, 2) if result.overall_score else None,
        "overall_maturity": result.overall_maturity.name if result.overall_maturity else None,
        "domain_scores": domain_scores,
        "gap_analysis": gaps,
        "heat_map_data": heat_map,
        "text_heat_map": text_heat_map,
    }
