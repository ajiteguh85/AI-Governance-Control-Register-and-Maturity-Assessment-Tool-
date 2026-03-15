"""Automated scoring algorithms and heat map generation for governance assessments."""

from typing import Any

from .models import AssessmentResult, GovernanceDomain, MaturityLevel


def compute_domain_scores(result: AssessmentResult) -> dict[str, float]:
    """Compute average maturity scores per domain.

    Returns a mapping of domain_id to average score.
    """
    scores: dict[str, float] = {}
    for domain in result.domains:
        avg = domain.average_score
        if avg is not None:
            scores[domain.domain_id] = round(avg, 2)
    return scores


def compute_gap_analysis(result: AssessmentResult, target_level: int = 3) -> dict[str, dict[str, Any]]:
    """Identify gaps between current scores and a target maturity level.

    Returns per-domain gap details including current score, target, and gap size.
    """
    gaps: dict[str, dict[str, Any]] = {}
    for domain in result.domains:
        avg = domain.average_score
        if avg is None:
            continue
        gap = max(0.0, target_level - avg)
        gaps[domain.domain_id] = {
            "domain_name": domain.name,
            "current_score": round(avg, 2),
            "target_level": target_level,
            "gap": round(gap, 2),
            "meets_target": gap == 0.0,
        }
    return gaps


def generate_heat_map_data(result: AssessmentResult) -> list[dict[str, Any]]:
    """Generate heat map data mapping controls to maturity levels.

    Returns a list of records suitable for visualization, with each record
    containing the domain, control, score, maturity level, and a severity
    category (critical / warning / acceptable / strong).
    """
    heat_map: list[dict[str, Any]] = []
    for domain in result.domains:
        for control in domain.controls:
            if control.score is None:
                continue
            severity = _score_to_severity(control.score)
            heat_map.append({
                "domain_id": domain.domain_id,
                "domain_name": domain.name,
                "control_id": control.control_id,
                "control_name": control.name,
                "score": control.score,
                "maturity_level": control.maturity_level.name if control.maturity_level else None,
                "severity": severity,
            })
    return heat_map


def _score_to_severity(score: int) -> str:
    """Map a numeric score to a severity category."""
    if score <= 1:
        return "critical"
    elif score <= 2:
        return "warning"
    elif score <= 3:
        return "acceptable"
    else:
        return "strong"


def render_text_heat_map(result: AssessmentResult) -> str:
    """Render a text-based heat map of the assessment results.

    Uses block characters to visually represent maturity levels.
    """
    BLOCKS = {1: "█", 2: "▓", 3: "▒", 4: "░", 5: " "}
    LABELS = {1: "INITIAL", 2: "DEVELOPING", 3: "DEFINED", 4: "MANAGED", 5: "OPTIMIZING"}

    lines: list[str] = []
    lines.append(f"{'='*70}")
    lines.append(f"  AI GOVERNANCE HEAT MAP — {result.organization}")
    lines.append(f"  Framework: {result.framework}")
    lines.append(f"{'='*70}")

    for domain in result.domains:
        avg = domain.average_score
        level_str = LABELS.get(domain.maturity_level, "N/A") if domain.maturity_level else "N/A"
        avg_str = f"{avg:.1f}" if avg is not None else "N/A"
        lines.append(f"\n  [{domain.domain_id}] {domain.name}  (avg: {avg_str} — {level_str})")
        lines.append(f"  {'-'*60}")

        for control in domain.controls:
            if control.score is None:
                bar = "  ?  "
            else:
                block = BLOCKS.get(control.score, "?")
                bar = block * control.score + "." * (5 - control.score)
            lines.append(f"    {control.control_id:12s} |{bar}| {control.score or '?'}/5  {control.name}")

    overall = result.overall_score
    overall_str = f"{overall:.2f}" if overall is not None else "N/A"
    lines.append(f"\n{'='*70}")
    lines.append(f"  Overall Maturity Score: {overall_str}/5.00")
    lines.append(f"{'='*70}")
    return "\n".join(lines)


def rank_domains(result: AssessmentResult) -> list[GovernanceDomain]:
    """Return domains sorted by average score (lowest first) for prioritization."""
    scored = [d for d in result.domains if d.average_score is not None]
    return sorted(scored, key=lambda d: d.average_score)  # type: ignore[arg-type]
