"""Automated scoring algorithms, heat map generation, and ML-based maturity prediction.

Includes:
- Domain-level scoring and weighted scoring
- Gap analysis against target maturity levels
- Heat map data generation with severity classification
- Text-based heat map rendering
- ML-based maturity prediction using linear regression
- AI advisory scoring for use case prioritization
"""

import math
from typing import Any, Optional

from .models import (
    AIUseCase,
    AssessmentResult,
    GovernanceDomain,
    MaturityLevel,
    RiskLevel,
    UseCaseStatus,
)


# ---------------------------------------------------------------------------
# Domain scoring
# ---------------------------------------------------------------------------

def compute_domain_scores(result: AssessmentResult) -> dict[str, float]:
    """Compute average maturity scores per domain."""
    scores: dict[str, float] = {}
    for domain in result.domains:
        avg = domain.average_score
        if avg is not None:
            scores[domain.domain_id] = round(avg, 2)
    return scores


def compute_weighted_domain_scores(result: AssessmentResult) -> dict[str, float]:
    """Compute weighted average maturity scores per domain."""
    scores: dict[str, float] = {}
    for domain in result.domains:
        avg = domain.weighted_average_score
        if avg is not None:
            scores[domain.domain_id] = round(avg, 2)
    return scores


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------

def compute_gap_analysis(
    result: AssessmentResult, target_level: int = 3
) -> dict[str, dict[str, Any]]:
    """Identify gaps between current scores and a target maturity level."""
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
            "priority": _gap_to_priority(gap),
        }
    return gaps


def _gap_to_priority(gap: float) -> str:
    """Classify a gap into a remediation priority."""
    if gap >= 2.0:
        return "critical"
    elif gap >= 1.0:
        return "high"
    elif gap > 0.0:
        return "medium"
    return "on_track"


# ---------------------------------------------------------------------------
# Heat map generation
# ---------------------------------------------------------------------------

def generate_heat_map_data(result: AssessmentResult) -> list[dict[str, Any]]:
    """Generate heat map data mapping controls to maturity levels."""
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


def generate_domain_heat_map(result: AssessmentResult) -> list[dict[str, Any]]:
    """Generate a domain-level heat map summary for dashboard display."""
    rows: list[dict[str, Any]] = []
    for domain in result.domains:
        avg = domain.average_score
        if avg is None:
            continue
        rows.append({
            "domain_id": domain.domain_id,
            "domain_name": domain.name,
            "average_score": round(avg, 2),
            "maturity_level": domain.maturity_level.name if domain.maturity_level else None,
            "severity": _score_to_severity(round(avg)),
            "completion_rate": round(domain.completion_rate * 100, 1),
            "control_count": len(domain.controls),
        })
    return rows


# ---------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------

def render_text_heat_map(result: AssessmentResult) -> str:
    """Render a text-based heat map of the assessment results."""
    BLOCKS = {1: "█", 2: "▓", 3: "▒", 4: "░", 5: " "}
    LABELS = {1: "INITIAL", 2: "DEVELOPING", 3: "DEFINED", 4: "MANAGED", 5: "OPTIMIZING"}

    lines: list[str] = []
    lines.append(f"{'='*72}")
    lines.append(f"  AI GOVERNANCE HEAT MAP — {result.organization}")
    lines.append(f"  Framework: {result.framework}")
    if result.assessor:
        lines.append(f"  Assessor: {result.assessor}  |  Date: {result.assessment_date}")
    lines.append(f"{'='*72}")

    for domain in result.domains:
        avg = domain.average_score
        level_str = LABELS.get(domain.maturity_level, "N/A") if domain.maturity_level else "N/A"
        avg_str = f"{avg:.1f}" if avg is not None else "N/A"
        pct = f"{domain.completion_rate*100:.0f}%"
        lines.append(f"\n  [{domain.domain_id}] {domain.name}  (avg: {avg_str} — {level_str})  [{pct} assessed]")
        lines.append(f"  {'-'*62}")

        for control in domain.controls:
            if control.score is None:
                bar = "  ?  "
            else:
                block = BLOCKS.get(control.score, "?")
                bar = block * control.score + "." * (5 - control.score)
            lines.append(f"    {control.control_id:12s} |{bar}| {control.score or '?'}/5  {control.name}")

    overall = result.overall_score
    overall_str = f"{overall:.2f}" if overall is not None else "N/A"
    overall_level = LABELS.get(result.overall_maturity, "N/A") if result.overall_maturity else "N/A"
    lines.append(f"\n{'='*72}")
    lines.append(f"  Overall Maturity Score: {overall_str}/5.00  ({overall_level})")
    lines.append(f"  Controls Assessed: {result.scored_controls}/{result.total_controls}")
    lines.append(f"{'='*72}")
    return "\n".join(lines)


def rank_domains(result: AssessmentResult) -> list[GovernanceDomain]:
    """Return domains sorted by average score (lowest first) for prioritization."""
    scored = [d for d in result.domains if d.average_score is not None]
    return sorted(scored, key=lambda d: d.average_score)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ML-based maturity prediction (linear regression from scratch)
# ---------------------------------------------------------------------------

class MaturityPredictor:
    """Simple linear regression model to predict future maturity scores.

    Uses ordinary least squares regression on historical assessment data
    to forecast maturity trajectory and estimate time to reach a target level.

    This demonstrates AI-advisory modelling capabilities suitable for
    governance dashboards in mining/extractive industry contexts.
    """

    def __init__(self) -> None:
        self.slope: float = 0.0
        self.intercept: float = 0.0
        self.r_squared: float = 0.0
        self._fitted: bool = False

    def fit(self, time_points: list[float], scores: list[float]) -> None:
        """Fit the regression model on historical (time, score) pairs.

        Args:
            time_points: Numeric time values (e.g., month index 1,2,3...).
            scores: Corresponding maturity scores at each time point.
        """
        n = len(time_points)
        if n < 2 or n != len(scores):
            raise ValueError("Need at least 2 matching time-score pairs.")

        mean_x = sum(time_points) / n
        mean_y = sum(scores) / n

        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(time_points, scores))
        ss_xx = sum((x - mean_x) ** 2 for x in time_points)
        ss_yy = sum((y - mean_y) ** 2 for y in scores)

        if ss_xx == 0:
            raise ValueError("All time points are identical.")

        self.slope = ss_xy / ss_xx
        self.intercept = mean_y - self.slope * mean_x

        if ss_yy > 0:
            self.r_squared = (ss_xy ** 2) / (ss_xx * ss_yy)
        else:
            self.r_squared = 1.0

        self._fitted = True

    def predict(self, time_point: float) -> float:
        """Predict the maturity score at a given future time point."""
        if not self._fitted:
            raise RuntimeError("Model must be fitted before prediction.")
        predicted = self.slope * time_point + self.intercept
        return max(1.0, min(5.0, predicted))

    def predict_batch(self, time_points: list[float]) -> list[float]:
        """Predict maturity scores for multiple time points."""
        return [self.predict(t) for t in time_points]

    def time_to_target(self, target: float) -> Optional[float]:
        """Estimate time to reach a target maturity level.

        Returns None if the trend is flat or declining (target unreachable).
        """
        if not self._fitted:
            raise RuntimeError("Model must be fitted before prediction.")
        if self.slope <= 0:
            return None
        t = (target - self.intercept) / self.slope
        return t if t > 0 else None

    @property
    def trend_direction(self) -> str:
        """Return the direction of the maturity trend."""
        if not self._fitted:
            return "unknown"
        if self.slope > 0.05:
            return "improving"
        elif self.slope < -0.05:
            return "declining"
        return "stable"

    def summary(self) -> dict[str, Any]:
        """Return a summary of the model's findings."""
        return {
            "slope": round(self.slope, 4),
            "intercept": round(self.intercept, 4),
            "r_squared": round(self.r_squared, 4),
            "trend": self.trend_direction,
            "fitted": self._fitted,
        }


# ---------------------------------------------------------------------------
# AI advisory scoring for use case prioritization
# ---------------------------------------------------------------------------

def compute_use_case_priority_score(use_case: AIUseCase) -> dict[str, Any]:
    """Score an AI-ML use case for implementation priority.

    Uses a weighted multi-criteria model considering:
    - Business impact (based on expected benefit keywords)
    - Technical readiness (based on status)
    - Risk-adjusted score (lower risk = higher priority for quick wins)
    - Governance readiness (number of mapped controls)

    Returns a priority report with a composite score (0-100).
    """
    # Business impact score (0-25)
    impact_keywords = {
        "cost_reduction": 20, "safety": 25, "efficiency": 18,
        "compliance": 22, "revenue": 15, "sustainability": 20,
        "predictive": 18, "optimization": 17, "automation": 16,
    }
    impact_score = 10.0  # baseline
    benefit_lower = use_case.expected_benefit.lower()
    for keyword, boost in impact_keywords.items():
        if keyword in benefit_lower:
            impact_score = max(impact_score, boost)

    # Technical readiness (0-25)
    readiness_map = {
        UseCaseStatus.PROPOSED: 5,
        UseCaseStatus.EVALUATING: 10,
        UseCaseStatus.PILOTING: 18,
        UseCaseStatus.DEPLOYED: 25,
        UseCaseStatus.RETIRED: 0,
    }
    readiness_score = readiness_map.get(use_case.status, 5)

    # Risk-adjusted score (0-25): lower risk = higher score for prioritization
    risk_penalty = {
        RiskLevel.LOW: 25,
        RiskLevel.MODERATE: 18,
        RiskLevel.HIGH: 10,
        RiskLevel.CRITICAL: 3,
    }
    risk_score = risk_penalty.get(use_case.risk_level, 10)

    # Governance readiness (0-25)
    num_controls = len(use_case.governance_controls)
    governance_score = min(25, num_controls * 5)

    composite = impact_score + readiness_score + risk_score + governance_score

    return {
        "use_case_id": use_case.use_case_id,
        "name": use_case.name,
        "composite_score": round(composite, 1),
        "impact_score": impact_score,
        "readiness_score": readiness_score,
        "risk_score": risk_score,
        "governance_score": governance_score,
        "recommendation": _priority_recommendation(composite),
    }


def _priority_recommendation(score: float) -> str:
    """Map composite score to an implementation recommendation."""
    if score >= 75:
        return "FAST-TRACK: High value, low risk — prioritize for immediate deployment"
    elif score >= 55:
        return "PROCEED: Good candidate — develop with standard governance oversight"
    elif score >= 35:
        return "EVALUATE: Moderate potential — conduct deeper feasibility study"
    return "DEFER: Low readiness or high risk — revisit in next planning cycle"


def rank_use_cases(use_cases: list[AIUseCase]) -> list[dict[str, Any]]:
    """Rank multiple AI-ML use cases by priority score (highest first)."""
    scored = [compute_use_case_priority_score(uc) for uc in use_cases]
    return sorted(scored, key=lambda x: x["composite_score"], reverse=True)
