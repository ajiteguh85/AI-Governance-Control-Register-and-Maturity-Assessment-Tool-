"""Data models for AI governance assessments."""

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

    @property
    def maturity_level(self) -> Optional[MaturityLevel]:
        if self.score is None:
            return None
        clamped = max(1, min(5, self.score))
        return MaturityLevel(clamped)


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
    def maturity_level(self) -> Optional[MaturityLevel]:
        avg = self.average_score
        if avg is None:
            return None
        return MaturityLevel(round(avg))


@dataclass
class AssessmentResult:
    """Complete result of a governance assessment."""

    assessment_id: str
    organization: str
    framework: str
    domains: list[GovernanceDomain] = field(default_factory=list)

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
