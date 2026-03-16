"""Data models for AI governance assessments.

Supports governance control registers, maturity assessments, AI-ML use case
tracking, and mining/extractive industry safety domains.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class MaturityLevel(IntEnum):
    """Maturity levels for governance controls (1-5 scale)."""

    INITIAL = 1
    DEVELOPING = 2
    DEFINED = 3
    MANAGED = 4
    OPTIMIZING = 5


class RiskLevel(IntEnum):
    """Risk classification for AI-ML use cases."""

    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4


class UseCaseStatus(IntEnum):
    """Lifecycle status for AI-ML use cases."""

    PROPOSED = 1
    EVALUATING = 2
    PILOTING = 3
    DEPLOYED = 4
    RETIRED = 5


@dataclass
class GovernanceControl:
    """A single governance control within a domain."""

    control_id: str
    name: str
    description: str
    domain: str
    score: Optional[int] = None
    evidence: str = ""
    recommendations: str = ""
    weight: float = 1.0

    @property
    def maturity_level(self) -> Optional[MaturityLevel]:
        if self.score is None:
            return None
        clamped = max(1, min(5, self.score))
        return MaturityLevel(clamped)

    @property
    def weighted_score(self) -> Optional[float]:
        if self.score is None:
            return None
        return self.score * self.weight


@dataclass
class GovernanceDomain:
    """A domain grouping related governance controls."""

    domain_id: str
    name: str
    description: str
    controls: list[GovernanceControl] = field(default_factory=list)

    @property
    def average_score(self) -> Optional[float]:
        scored = [c.score for c in self.controls if c.score is not None]
        if not scored:
            return None
        return sum(scored) / len(scored)

    @property
    def weighted_average_score(self) -> Optional[float]:
        scored = [(c.weighted_score, c.weight) for c in self.controls if c.weighted_score is not None]
        if not scored:
            return None
        total_weighted = sum(s for s, _ in scored)
        total_weight = sum(w for _, w in scored)
        return total_weighted / total_weight if total_weight > 0 else None

    @property
    def maturity_level(self) -> Optional[MaturityLevel]:
        avg = self.average_score
        if avg is None:
            return None
        return MaturityLevel(round(avg))

    @property
    def completion_rate(self) -> float:
        if not self.controls:
            return 0.0
        scored = sum(1 for c in self.controls if c.score is not None)
        return scored / len(self.controls)


@dataclass
class AssessmentResult:
    """Complete result of a governance assessment."""

    assessment_id: str
    organization: str
    framework: str
    domains: list[GovernanceDomain] = field(default_factory=list)
    assessor: str = ""
    assessment_date: str = ""
    notes: str = ""

    @property
    def overall_score(self) -> Optional[float]:
        scores = [d.average_score for d in self.domains if d.average_score is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)

    @property
    def overall_maturity(self) -> Optional[MaturityLevel]:
        score = self.overall_score
        if score is None:
            return None
        return MaturityLevel(round(score))

    @property
    def total_controls(self) -> int:
        return sum(len(d.controls) for d in self.domains)

    @property
    def scored_controls(self) -> int:
        return sum(1 for d in self.domains for c in d.controls if c.score is not None)


@dataclass
class AIUseCase:
    """An AI-ML use case tracked in the governance register.

    Designed for extractive/mining industry scenarios such as predictive
    maintenance, ore grade optimization, safety incident prediction, etc.
    """

    use_case_id: str
    name: str
    description: str
    business_unit: str
    category: str  # e.g. "predictive_maintenance", "safety", "process_optimization"
    status: UseCaseStatus = UseCaseStatus.PROPOSED
    risk_level: RiskLevel = RiskLevel.MODERATE
    owner: str = ""
    ai_techniques: list[str] = field(default_factory=list)
    data_sources: list[str] = field(default_factory=list)
    expected_benefit: str = ""
    maturity_score: Optional[int] = None
    governance_controls: list[str] = field(default_factory=list)


@dataclass
class SafetyIncidentRecord:
    """Record of an AI-related safety event for tracking and governance."""

    incident_id: str
    use_case_id: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    root_cause: str = ""
    corrective_action: str = ""
    is_resolved: bool = False
