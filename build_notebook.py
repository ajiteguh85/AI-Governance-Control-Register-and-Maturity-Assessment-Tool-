#!/usr/bin/env python3
"""Build the AI Governance Assessment Jupyter Notebook.

Uses nbformat for proper .ipynb formatting so every cell renders
correctly in Google Colab / Jupyter.
"""

import json
import nbformat

nb = nbformat.v4.new_notebook()
nb.metadata.update({
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.10.0",
    },
    "colab": {
        "provenance": [],
        "name": "AI_Governance_Assessment_Tool.ipynb",
    },
})

cells = []


def md(source):
    cells.append(nbformat.v4.new_markdown_cell(source))


def code(source):
    cells.append(nbformat.v4.new_code_cell(source))


# ══════════════════════════════════════════════════════════════════════
# CELL 0 — Title
# ══════════════════════════════════════════════════════════════════════
md("""\
# AI Governance Control Register & Maturity Assessment Tool
## Mining & Extractive Industry Edition

**A comprehensive Python-based tool for evaluating AI governance compliance
with structured management frameworks.**

### Features
| # | Capability | Description |
|---|-----------|-------------|
| 1 | **Governance Assessment** | ISO/IEC 42001 & ESG monitoring frameworks |
| 2 | **Automated Scoring** | Maturity heat maps, gap analysis, weighted scoring |
| 3 | **ML Prediction** | Linear regression for maturity trend forecasting |
| 4 | **Use Case Registry** | Mining industry AI-ML use case catalogue & prioritization |
| 5 | **ESG & Safety Dashboards** | Executive dashboards with KPI tracking |
| 6 | **Validation Protocols** | Testing protocols for AI-ML model deployments |
| 7 | **Best Practices** | AI adoption standards for extractive industry |

### Context
Designed for the **Senior Specialist, Data Science & AI** role at
**Ma'aden (Saudi Arabian Mining Company)**, aligned with:
- ISO/IEC 42001 AI Management Systems
- Saudi Vision 2030 & Saudi Green Initiative
- ICMM and IRMA governance standards

---
> **How to run:** Execute cells top-to-bottom (`Runtime > Run all` in Colab).
> Only requires `matplotlib` (pre-installed in Colab).
""")

# ══════════════════════════════════════════════════════════════════════
# CELL 1 — Imports
# ══════════════════════════════════════════════════════════════════════
code("""\
# ============================================================
# Setup & Imports
# ============================================================
import json
import math
import statistics
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# Inline plots
%matplotlib inline
plt.style.use("seaborn-v0_8-whitegrid")

print("All imports loaded successfully.")
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 1 — Data Models
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 1: Data Models

Core data structures for governance controls, domains, assessments,
AI use cases, and safety incident records.
""")

code("""\
# ============================================================
# MODULE 1 — DATA MODELS
# ============================================================


class MaturityLevel(IntEnum):
    \"\"\"Maturity levels for governance controls (1-5 scale).\"\"\"
    INITIAL = 1
    DEVELOPING = 2
    DEFINED = 3
    MANAGED = 4
    OPTIMIZING = 5


class RiskLevel(IntEnum):
    \"\"\"Risk classification for AI-ML use cases.\"\"\"
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4


class UseCaseStatus(IntEnum):
    \"\"\"Lifecycle status for AI-ML use cases.\"\"\"
    PROPOSED = 1
    EVALUATING = 2
    PILOTING = 3
    DEPLOYED = 4
    RETIRED = 5


@dataclass
class GovernanceControl:
    \"\"\"A single governance control within a domain.\"\"\"
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
        return MaturityLevel(max(1, min(5, self.score)))

    @property
    def weighted_score(self) -> Optional[float]:
        if self.score is None:
            return None
        return self.score * self.weight


@dataclass
class GovernanceDomain:
    \"\"\"A domain grouping related governance controls.\"\"\"
    domain_id: str
    name: str
    description: str
    controls: list = field(default_factory=list)

    @property
    def average_score(self) -> Optional[float]:
        scored = [c.score for c in self.controls if c.score is not None]
        return sum(scored) / len(scored) if scored else None

    @property
    def weighted_average_score(self) -> Optional[float]:
        scored = [
            (c.weighted_score, c.weight)
            for c in self.controls if c.weighted_score is not None
        ]
        if not scored:
            return None
        total_w = sum(s for s, _ in scored)
        total_wt = sum(w for _, w in scored)
        return total_w / total_wt if total_wt > 0 else None

    @property
    def maturity_level(self) -> Optional[MaturityLevel]:
        avg = self.average_score
        return MaturityLevel(round(avg)) if avg is not None else None

    @property
    def completion_rate(self) -> float:
        if not self.controls:
            return 0.0
        return sum(1 for c in self.controls if c.score is not None) / len(self.controls)


@dataclass
class AssessmentResult:
    \"\"\"Complete result of a governance assessment.\"\"\"
    assessment_id: str
    organization: str
    framework: str
    domains: list = field(default_factory=list)
    assessor: str = ""
    assessment_date: str = ""
    notes: str = ""

    @property
    def overall_score(self) -> Optional[float]:
        scores = [d.average_score for d in self.domains if d.average_score is not None]
        return sum(scores) / len(scores) if scores else None

    @property
    def overall_maturity(self) -> Optional[MaturityLevel]:
        s = self.overall_score
        return MaturityLevel(round(s)) if s is not None else None

    @property
    def total_controls(self) -> int:
        return sum(len(d.controls) for d in self.domains)

    @property
    def scored_controls(self) -> int:
        return sum(1 for d in self.domains for c in d.controls if c.score is not None)


@dataclass
class AIUseCase:
    \"\"\"An AI-ML use case tracked in the governance register.\"\"\"
    use_case_id: str
    name: str
    description: str
    business_unit: str
    category: str
    status: UseCaseStatus = UseCaseStatus.PROPOSED
    risk_level: RiskLevel = RiskLevel.MODERATE
    owner: str = ""
    ai_techniques: list = field(default_factory=list)
    data_sources: list = field(default_factory=list)
    expected_benefit: str = ""
    maturity_score: Optional[int] = None
    governance_controls: list = field(default_factory=list)


@dataclass
class SafetyIncidentRecord:
    \"\"\"Record of an AI-related safety event for tracking and governance.\"\"\"
    incident_id: str
    use_case_id: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    root_cause: str = ""
    corrective_action: str = ""
    is_resolved: bool = False


print("Module 1 loaded: MaturityLevel, RiskLevel, UseCaseStatus,")
print("  GovernanceControl, GovernanceDomain, AssessmentResult,")
print("  AIUseCase, SafetyIncidentRecord")
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 2 — Templates
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 2: Governance Assessment Templates

Inline JSON templates for:
1. **ISO/IEC 42001** AI Management Systems (7 domains, 21 controls)
2. **AI-Based ESG Monitoring** Governance (4 domains, 15 controls)
""")

# Read actual template files and embed them
with open("templates/iso_42001_template.json") as f:
    iso_tmpl = json.load(f)
with open("templates/esg_ai_monitoring_template.json") as f:
    esg_tmpl = json.load(f)

iso_json = json.dumps(iso_tmpl, indent=2)
esg_json = json.dumps(esg_tmpl, indent=2)

code(f"""\
# ============================================================
# MODULE 2 — GOVERNANCE ASSESSMENT TEMPLATES (inline JSON)
# ============================================================

ISO_42001_TEMPLATE = json.loads('''
{iso_json}
''')

ESG_MONITORING_TEMPLATE = json.loads('''
{esg_json}
''')

TEMPLATES = {{
    "iso_42001_template.json": ISO_42001_TEMPLATE,
    "esg_ai_monitoring_template.json": ESG_MONITORING_TEMPLATE,
}}

for name, tmpl in TEMPLATES.items():
    n_domains = len(tmpl["domains"])
    n_controls = sum(len(d["controls"]) for d in tmpl["domains"])
    print(f"Loaded: {{name}}")
    print(f"  Framework : {{tmpl['framework']}}")
    print(f"  Domains   : {{n_domains}}")
    print(f"  Controls  : {{n_controls}}")
    print()
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 3 — Scoring & ML
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 3: Scoring Algorithms & ML-Based Maturity Prediction

- Domain-level scoring and weighted scoring
- Gap analysis against configurable target maturity levels
- Heat map data generation (control-level & domain-level)
- Text-based heat map rendering
- **ML-based maturity prediction** using OLS linear regression
- AI advisory scoring for use case prioritization
""")

code("""\
# ============================================================
# MODULE 3 — SCORING ALGORITHMS & ML PREDICTION
# ============================================================

# ---------------------------------------------------------------------------
# Domain scoring
# ---------------------------------------------------------------------------

def compute_domain_scores(result):
    \"\"\"Compute average maturity scores per domain.\"\"\"
    scores = {}
    for domain in result.domains:
        avg = domain.average_score
        if avg is not None:
            scores[domain.domain_id] = round(avg, 2)
    return scores


def compute_weighted_domain_scores(result):
    \"\"\"Compute weighted average maturity scores per domain.\"\"\"
    scores = {}
    for domain in result.domains:
        avg = domain.weighted_average_score
        if avg is not None:
            scores[domain.domain_id] = round(avg, 2)
    return scores


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------

def _gap_to_priority(gap):
    if gap >= 2.0:
        return "critical"
    elif gap >= 1.0:
        return "high"
    elif gap > 0.0:
        return "medium"
    return "on_track"


def compute_gap_analysis(result, target_level=3):
    \"\"\"Identify gaps between current scores and a target maturity level.\"\"\"
    gaps = {}
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


# ---------------------------------------------------------------------------
# Heat map generation
# ---------------------------------------------------------------------------

def _score_to_severity(score):
    if score <= 1:
        return "critical"
    elif score <= 2:
        return "warning"
    elif score <= 3:
        return "acceptable"
    return "strong"


def generate_heat_map_data(result):
    \"\"\"Generate heat map data mapping controls to maturity levels.\"\"\"
    heat_map = []
    for domain in result.domains:
        for control in domain.controls:
            if control.score is None:
                continue
            heat_map.append({
                "domain_id": domain.domain_id,
                "domain_name": domain.name,
                "control_id": control.control_id,
                "control_name": control.name,
                "score": control.score,
                "maturity_level": control.maturity_level.name if control.maturity_level else None,
                "severity": _score_to_severity(control.score),
            })
    return heat_map


def generate_domain_heat_map(result):
    \"\"\"Generate a domain-level heat map summary for dashboard display.\"\"\"
    rows = []
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

def render_text_heat_map(result):
    \"\"\"Render a text-based heat map of the assessment results.\"\"\"
    BLOCKS = {1: "\\u2588", 2: "\\u2593", 3: "\\u2592", 4: "\\u2591", 5: " "}
    LABELS = {
        1: "INITIAL", 2: "DEVELOPING", 3: "DEFINED",
        4: "MANAGED", 5: "OPTIMIZING",
    }

    lines = []
    lines.append("=" * 72)
    lines.append(f"  AI GOVERNANCE HEAT MAP \\u2014 {result.organization}")
    lines.append(f"  Framework: {result.framework}")
    if result.assessor:
        lines.append(f"  Assessor: {result.assessor}  |  Date: {result.assessment_date}")
    lines.append("=" * 72)

    for domain in result.domains:
        avg = domain.average_score
        level_str = LABELS.get(domain.maturity_level, "N/A") if domain.maturity_level else "N/A"
        avg_str = f"{avg:.1f}" if avg is not None else "N/A"
        pct = f"{domain.completion_rate * 100:.0f}%"
        lines.append(
            f"\\n  [{domain.domain_id}] {domain.name}  "
            f"(avg: {avg_str} \\u2014 {level_str})  [{pct} assessed]"
        )
        lines.append(f"  {'-' * 62}")

        for control in domain.controls:
            if control.score is None:
                bar = "  ?  "
            else:
                block = BLOCKS.get(control.score, "?")
                bar = block * control.score + "." * (5 - control.score)
            score_str = str(control.score) if control.score else "?"
            lines.append(
                f"    {control.control_id:12s} |{bar}| {score_str}/5  {control.name}"
            )

    overall = result.overall_score
    overall_str = f"{overall:.2f}" if overall is not None else "N/A"
    overall_level = LABELS.get(result.overall_maturity, "N/A") if result.overall_maturity else "N/A"
    lines.append(f"\\n{'=' * 72}")
    lines.append(f"  Overall Maturity Score: {overall_str}/5.00  ({overall_level})")
    lines.append(f"  Controls Assessed: {result.scored_controls}/{result.total_controls}")
    lines.append("=" * 72)
    return "\\n".join(lines)


def rank_domains(result):
    \"\"\"Return domains sorted by average score (lowest first).\"\"\"
    scored = [d for d in result.domains if d.average_score is not None]
    return sorted(scored, key=lambda d: d.average_score)


# ---------------------------------------------------------------------------
# ML-based maturity prediction (OLS linear regression from scratch)
# ---------------------------------------------------------------------------

class MaturityPredictor:
    \"\"\"Simple linear regression model to predict future maturity scores.

    Uses ordinary least squares regression on historical assessment data
    to forecast maturity trajectory and estimate time to reach a target level.
    \"\"\"

    def __init__(self):
        self.slope = 0.0
        self.intercept = 0.0
        self.r_squared = 0.0
        self._fitted = False

    def fit(self, time_points, scores):
        \"\"\"Fit the regression model on historical (time, score) pairs.\"\"\"
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
        self.r_squared = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy > 0 else 1.0
        self._fitted = True

    def predict(self, time_point):
        \"\"\"Predict the maturity score at a given future time point.\"\"\"
        if not self._fitted:
            raise RuntimeError("Model must be fitted before prediction.")
        return max(1.0, min(5.0, self.slope * time_point + self.intercept))

    def predict_batch(self, time_points):
        \"\"\"Predict maturity scores for multiple time points.\"\"\"
        return [self.predict(t) for t in time_points]

    def time_to_target(self, target):
        \"\"\"Estimate time to reach a target maturity level.\"\"\"
        if not self._fitted:
            raise RuntimeError("Model must be fitted before prediction.")
        if self.slope <= 0:
            return None
        t = (target - self.intercept) / self.slope
        return t if t > 0 else None

    @property
    def trend_direction(self):
        if not self._fitted:
            return "unknown"
        if self.slope > 0.05:
            return "improving"
        elif self.slope < -0.05:
            return "declining"
        return "stable"

    def summary(self):
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

def compute_use_case_priority_score(use_case):
    \"\"\"Score an AI-ML use case for implementation priority (0-100).\"\"\"
    impact_keywords = {
        "cost_reduction": 20, "safety": 25, "efficiency": 18,
        "compliance": 22, "revenue": 15, "sustainability": 20,
        "predictive": 18, "optimization": 17, "automation": 16,
    }
    impact_score = 10.0
    benefit_lower = use_case.expected_benefit.lower()
    for keyword, boost in impact_keywords.items():
        if keyword in benefit_lower:
            impact_score = max(impact_score, boost)

    readiness_map = {
        UseCaseStatus.PROPOSED: 5, UseCaseStatus.EVALUATING: 10,
        UseCaseStatus.PILOTING: 18, UseCaseStatus.DEPLOYED: 25,
        UseCaseStatus.RETIRED: 0,
    }
    readiness_score = readiness_map.get(use_case.status, 5)

    risk_penalty = {
        RiskLevel.LOW: 25, RiskLevel.MODERATE: 18,
        RiskLevel.HIGH: 10, RiskLevel.CRITICAL: 3,
    }
    risk_score = risk_penalty.get(use_case.risk_level, 10)

    governance_score = min(25, len(use_case.governance_controls) * 5)

    composite = impact_score + readiness_score + risk_score + governance_score

    if composite >= 75:
        rec = "FAST-TRACK: High value, low risk \\u2014 prioritize for immediate deployment"
    elif composite >= 55:
        rec = "PROCEED: Good candidate \\u2014 develop with standard governance oversight"
    elif composite >= 35:
        rec = "EVALUATE: Moderate potential \\u2014 conduct deeper feasibility study"
    else:
        rec = "DEFER: Low readiness or high risk \\u2014 revisit in next planning cycle"

    return {
        "use_case_id": use_case.use_case_id,
        "name": use_case.name,
        "composite_score": round(composite, 1),
        "impact_score": impact_score,
        "readiness_score": readiness_score,
        "risk_score": risk_score,
        "governance_score": governance_score,
        "recommendation": rec,
    }


def rank_use_cases(use_cases):
    \"\"\"Rank multiple AI-ML use cases by priority score (highest first).\"\"\"
    scored = [compute_use_case_priority_score(uc) for uc in use_cases]
    return sorted(scored, key=lambda x: x["composite_score"], reverse=True)


print("Module 3 loaded: scoring, gap analysis, heat maps,")
print("  MaturityPredictor (OLS), use case prioritization")
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 4 — Validation
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 4: Validation & AI-ML Deployment Test Protocols

- Data integrity validation for controls, domains, and assessments
- AI-ML use case registration validation
- Standardized deployment test protocols (13 steps across 5 categories)
""")

code("""\
# ============================================================
# MODULE 4 — VALIDATION & DEPLOYMENT TEST PROTOCOLS
# ============================================================

@dataclass
class ValidationError:
    \"\"\"A single validation error.\"\"\"
    field: str
    message: str
    severity: str = "error"  # "error" or "warning"


class ValidationResult:
    \"\"\"Collection of validation errors for an assessment.\"\"\"

    def __init__(self):
        self.errors = []

    @property
    def is_valid(self):
        return not any(e.severity == "error" for e in self.errors)

    @property
    def warnings(self):
        return [e for e in self.errors if e.severity == "warning"]

    def add_error(self, field, message):
        self.errors.append(ValidationError(field=field, message=message, severity="error"))

    def add_warning(self, field, message):
        self.errors.append(ValidationError(field=field, message=message, severity="warning"))

    def __repr__(self):
        return f"ValidationResult(valid={self.is_valid}, errors={len(self.errors)})"


def validate_control(control):
    \"\"\"Validate a single governance control.\"\"\"
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


def validate_domain(domain):
    \"\"\"Validate a governance domain and all its controls.\"\"\"
    result = ValidationResult()
    if not domain.domain_id or not domain.domain_id.strip():
        result.add_error("domain_id", "Domain ID must not be empty.")
    if not domain.name or not domain.name.strip():
        result.add_error("name", "Domain name must not be empty.")
    if not domain.controls:
        result.add_warning("controls", f"Domain '{domain.domain_id}' has no controls.")
    seen_ids = set()
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


def validate_assessment(assessment):
    \"\"\"Validate a complete governance assessment.\"\"\"
    result = ValidationResult()
    if not assessment.assessment_id or not assessment.assessment_id.strip():
        result.add_error("assessment_id", "Assessment ID must not be empty.")
    if not assessment.organization or not assessment.organization.strip():
        result.add_error("organization", "Organization name must not be empty.")
    if not assessment.framework or not assessment.framework.strip():
        result.add_error("framework", "Framework name must not be empty.")
    if not assessment.domains:
        result.add_error("domains", "Assessment must contain at least one domain.")
    seen = set()
    for domain in assessment.domains:
        if domain.domain_id in seen:
            result.add_error("domain_id", f"Duplicate domain ID '{domain.domain_id}'.")
        seen.add(domain.domain_id)
        domain_result = validate_domain(domain)
        result.errors.extend(domain_result.errors)
    return result


def validate_use_case(use_case):
    \"\"\"Validate an AI-ML use case registration.\"\"\"
    result = ValidationResult()
    if not use_case.use_case_id or not use_case.use_case_id.strip():
        result.add_error("use_case_id", "Use case ID must not be empty.")
    if not use_case.name or not use_case.name.strip():
        result.add_error("name", "Use case name must not be empty.")
    if not use_case.business_unit or not use_case.business_unit.strip():
        result.add_error("business_unit", "Business unit must be specified.")
    if not use_case.category or not use_case.category.strip():
        result.add_error("category", "Use case category must not be empty.")
    if not use_case.ai_techniques:
        result.add_warning("ai_techniques", "Use case should specify at least one AI technique.")
    if not use_case.data_sources:
        result.add_warning("data_sources", "Use case should specify at least one data source.")
    return result


# ---------------------------------------------------------------------------
# AI-ML Deployment Test Protocol
# ---------------------------------------------------------------------------

@dataclass
class TestProtocolStep:
    \"\"\"A single step in a testing/validation protocol.\"\"\"
    step_id: str
    name: str
    description: str
    validation_type: str  # data_quality, model_performance, bias, security, integration
    is_mandatory: bool = True
    passed: object = None  # None = not tested, True/False
    notes: str = ""


@dataclass
class DeploymentTestProtocol:
    \"\"\"Testing and validation protocol for AI-ML model deployment.\"\"\"
    protocol_id: str
    use_case_id: str
    model_name: str
    model_version: str
    steps: list = field(default_factory=list)

    @property
    def is_complete(self):
        return all(s.passed is not None for s in self.steps)

    @property
    def is_passed(self):
        mandatory = [s for s in self.steps if s.is_mandatory]
        return all(s.passed is True for s in mandatory)

    @property
    def completion_rate(self):
        if not self.steps:
            return 0.0
        return sum(1 for s in self.steps if s.passed is not None) / len(self.steps)

    @property
    def pass_rate(self):
        tested = [s for s in self.steps if s.passed is not None]
        if not tested:
            return 0.0
        return sum(1 for s in tested if s.passed) / len(tested)


def create_standard_test_protocol(protocol_id, use_case_id, model_name, model_version):
    \"\"\"Create a standard AI-ML deployment test protocol (13 steps, 5 categories).\"\"\"
    steps = [
        TestProtocolStep("DQ-01", "Input Data Completeness",
            "Verify all required input data fields are present and within expected ranges.",
            "data_quality"),
        TestProtocolStep("DQ-02", "Data Distribution Validation",
            "Check data distribution matches training data profile (no significant drift).",
            "data_quality"),
        TestProtocolStep("DQ-03", "Outlier and Anomaly Check",
            "Identify and flag statistical outliers that may affect model reliability.",
            "data_quality"),
        TestProtocolStep("MP-01", "Model Accuracy Benchmark",
            "Validate model meets minimum accuracy thresholds on holdout test data.",
            "model_performance"),
        TestProtocolStep("MP-02", "Model Robustness Test",
            "Test model performance under edge cases, noise, and adversarial inputs.",
            "model_performance"),
        TestProtocolStep("MP-03", "Performance Regression Check",
            "Ensure new model version does not degrade performance vs. previous version.",
            "model_performance"),
        TestProtocolStep("BF-01", "Bias and Fairness Assessment",
            "Evaluate model for demographic and operational bias across protected groups.",
            "bias"),
        TestProtocolStep("BF-02", "Explainability Validation",
            "Verify model outputs can be explained and justified for governance reporting.",
            "bias"),
        TestProtocolStep("SC-01", "Data Privacy Compliance",
            "Confirm model does not expose or leak sensitive/personal data.",
            "security"),
        TestProtocolStep("SC-02", "Access Control Verification",
            "Validate model API endpoints enforce proper authentication and authorization.",
            "security"),
        TestProtocolStep("IT-01", "System Integration Test",
            "Verify model integrates correctly with upstream data sources and downstream consumers.",
            "integration"),
        TestProtocolStep("IT-02", "Failover and Recovery Test",
            "Test graceful degradation and recovery procedures when model service is unavailable.",
            "integration"),
        TestProtocolStep("IT-03", "Monitoring and Alerting Validation",
            "Confirm model performance monitoring and alert mechanisms are operational.",
            "integration", is_mandatory=False),
    ]
    return DeploymentTestProtocol(protocol_id, use_case_id, model_name, model_version, steps)


print("Module 4 loaded: validation, DeploymentTestProtocol,")
print("  create_standard_test_protocol (13 steps, 5 categories)")
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 5 — Assessment Engine
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 5: Assessment Engine

Orchestrates template loading, assessment building, scoring, validation,
and report generation.
""")

code("""\
# ============================================================
# MODULE 5 — ASSESSMENT ENGINE
# ============================================================

def build_assessment_from_template(template_name, assessment_id, organization, scores=None):
    \"\"\"Build an AssessmentResult from an inline template and optional scores.\"\"\"
    data = TEMPLATES[template_name]
    framework = data.get("framework", "Unknown")
    scores = scores or {}
    domains = []
    for d in data["domains"]:
        controls = []
        for c in d["controls"]:
            cid = c["control_id"]
            controls.append(GovernanceControl(
                control_id=cid,
                name=c["name"],
                description=c["description"],
                domain=d["domain_id"],
                score=scores.get(cid),
            ))
        domains.append(GovernanceDomain(
            domain_id=d["domain_id"],
            name=d["name"],
            description=d["description"],
            controls=controls,
        ))
    return AssessmentResult(
        assessment_id=assessment_id,
        organization=organization,
        framework=framework,
        domains=domains,
    )


def run_assessment(template_name, assessment_id, organization, scores, target_level=3):
    \"\"\"Run a complete governance assessment and return a structured report.\"\"\"
    result = build_assessment_from_template(template_name, assessment_id, organization, scores)
    validation = validate_assessment(result)
    domain_scores = compute_domain_scores(result)
    weighted_scores = compute_weighted_domain_scores(result)
    gaps = compute_gap_analysis(result, target_level=target_level)
    heat_map = generate_heat_map_data(result)
    domain_heat_map = generate_domain_heat_map(result)
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
        "controls_assessed": result.scored_controls,
        "controls_total": result.total_controls,
        "domain_scores": domain_scores,
        "weighted_domain_scores": weighted_scores,
        "gap_analysis": gaps,
        "heat_map_data": heat_map,
        "domain_heat_map": domain_heat_map,
        "text_heat_map": text_heat_map,
        "_result": result,  # keep the object for visualizations
    }


def run_maturity_prediction(historical_scores, forecast_periods=4, target_level=4.0):
    \"\"\"Run maturity trend prediction using linear regression.\"\"\"
    predictor = MaturityPredictor()
    times = [t for t, _ in historical_scores]
    scores = [s for _, s in historical_scores]
    predictor.fit(times, scores)

    last_time = max(times)
    forecast_times = [last_time + i + 1 for i in range(forecast_periods)]
    forecasts = predictor.predict_batch(forecast_times)

    return {
        "model_summary": predictor.summary(),
        "historical_data": [{"time": t, "score": s} for t, s in historical_scores],
        "forecasts": [
            {"time": t, "predicted_score": round(s, 2)}
            for t, s in zip(forecast_times, forecasts)
        ],
        "time_to_target": predictor.time_to_target(target_level),
        "target_level": target_level,
        "_predictor": predictor,
    }


print("Module 5 loaded: build_assessment_from_template,")
print("  run_assessment, run_maturity_prediction")
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 6 — Mining Use Cases & Best Practices
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 6: Mining Industry AI-ML Use Case Registry & Best Practices

Catalogue of **8 AI-ML use cases** for Ma'aden-style mining operations,
plus **13 best practices** across 4 categories for AI adoption in the
extractive industry.
""")

# Read mining_use_cases.py and adapt for notebook
with open("ai_governance/mining_use_cases.py") as f:
    mining_src = f.read()

# Remove the package import and fix for inline use
mining_src = mining_src.replace(
    "from .models import AIUseCase, RiskLevel, UseCaseStatus",
    "# (Models already loaded above)",
)

code(f"""\
# ============================================================
# MODULE 6 — MINING USE CASE REGISTRY & BEST PRACTICES
# ============================================================

{mining_src}

# Print summary
catalogue = get_mining_use_case_catalogue()
practices = get_ai_adoption_best_practices()
categories = get_use_case_categories()

print(f"Mining use case catalogue: {{len(catalogue)}} use cases")
print(f"Use case categories     : {{len(categories)}}")
print(f"Best practice items     : {{sum(len(v) for v in practices.values())}} across {{len(practices)}} categories")
""")

# ══════════════════════════════════════════════════════════════════════
# MODULE 7 — Dashboard
# ══════════════════════════════════════════════════════════════════════
md("""\
---
## Module 7: ESG & Safety Dashboard

Executive dashboard data generation combining governance maturity,
ESG scorecard, AI use case portfolio, and safety incident tracking.
""")

# Read dashboard.py and adapt
with open("ai_governance/dashboard.py") as f:
    dash_src = f.read()

# Remove package-level imports (already loaded inline)
dash_lines = dash_src.split("\n")
cleaned = []
in_import_block = False
for line in dash_lines:
    # Skip "from .xxx import (" multi-line blocks and single-line imports
    if line.startswith("from ."):
        if "(" in line and ")" not in line:
            in_import_block = True
        continue
    if in_import_block:
        if ")" in line:
            in_import_block = False
        continue
    if line.startswith("import "):
        if "statistics" in line:
            continue  # already imported
    cleaned.append(line)
dash_src_clean = "\n".join(cleaned)

code(f"""\
# ============================================================
# MODULE 7 — ESG & SAFETY DASHBOARD
# ============================================================

{dash_src_clean}

print("Module 7 loaded: generate_executive_summary, render_text_dashboard,")
print("  generate_esg_kpi_data, generate_safety_dashboard_data")
""")

# ══════════════════════════════════════════════════════════════════════
# DEMOS
# ══════════════════════════════════════════════════════════════════════
md("""\
---
---

# Interactive Demos

The cells below demonstrate all tool capabilities with **Ma'aden mining
industry data** and **matplotlib visualizations**.

---
""")

# --- Demo 1: ISO 42001 Assessment ---
md("## Demo 1: ISO/IEC 42001 AI Management System Assessment")

code("""\
# ── Sample scores for Ma'aden ISO/IEC 42001 assessment ──
iso_scores = {
    "D1-C01": 3, "D1-C02": 4, "D1-C03": 3,   # Context of the Organization
    "D2-C01": 4, "D2-C02": 3, "D2-C03": 4,   # Leadership & Commitment
    "D3-C01": 2, "D3-C02": 2, "D3-C03": 3,   # Planning
    "D4-C01": 4, "D4-C02": 3, "D4-C03": 3,   # Support & Resources
    "D5-C01": 3, "D5-C02": 2, "D5-C03": 3, "D5-C04": 2,  # Operation
    "D6-C01": 4, "D6-C02": 3, "D6-C03": 3,   # Performance Evaluation
    "D7-C01": 3, "D7-C02": 4,                 # Improvement
}

iso_report = run_assessment(
    "iso_42001_template.json",
    "MAADEN-ISO-2026-001",
    "Ma'aden (Saudi Arabian Mining Company)",
    iso_scores,
    target_level=4,
)

# Print text heat map
print(iso_report["text_heat_map"])
print()
print(f"Overall Score   : {iso_report['overall_score']}/5.00")
print(f"Overall Maturity: {iso_report['overall_maturity']}")
print(f"Assessment Valid : {iso_report['is_valid']}")
""")

# --- Demo 2: ISO Heat Map Chart ---
md("## Demo 2: ISO/IEC 42001 Domain Maturity Heat Map")

code("""\
fig, ax = plt.subplots(figsize=(12, 6))

domains = list(iso_report["domain_scores"].keys())
scores = list(iso_report["domain_scores"].values())
domain_names = [iso_report["gap_analysis"][d]["domain_name"] for d in domains]

colors = []
for s in scores:
    if s < 2.5:
        colors.append("#d32f2f")
    elif s < 3.0:
        colors.append("#f57c00")
    elif s < 3.5:
        colors.append("#fbc02d")
    elif s < 4.0:
        colors.append("#388e3c")
    else:
        colors.append("#1b5e20")

bars = ax.barh(range(len(domains)), scores, color=colors, edgecolor="white", height=0.6)
ax.set_yticks(range(len(domains)))
ax.set_yticklabels([f"[{d}] {n}" for d, n in zip(domains, domain_names)], fontsize=10)
ax.set_xlabel("Maturity Score", fontsize=12)
ax.set_title(
    "ISO/IEC 42001 \\u2014 AI Governance Maturity Heat Map\\n"
    "Ma'aden (Saudi Arabian Mining Company)",
    fontsize=14, fontweight="bold",
)
ax.set_xlim(0, 5.5)
ax.axvline(x=4, color="red", linestyle="--", alpha=0.7, label="Target Level 4 (MANAGED)")

for i, (bar, score) in enumerate(zip(bars, scores)):
    ax.text(score + 0.1, i, f"{score:.1f}", va="center", fontweight="bold", fontsize=11)

ax.legend(loc="lower right")
ax.invert_yaxis()
plt.tight_layout()
plt.show()
""")

# --- Demo 3: ESG Assessment ---
md("## Demo 3: AI-Based ESG Monitoring Governance Assessment")

code("""\
esg_scores = {
    "ESG-E-01": 4, "ESG-E-02": 3, "ESG-E-03": 2, "ESG-E-04": 3,  # Environmental
    "ESG-S-01": 3, "ESG-S-02": 3, "ESG-S-03": 2, "ESG-S-04": 3,  # Social
    "ESG-G-01": 4, "ESG-G-02": 3, "ESG-G-03": 3, "ESG-G-04": 2,  # Governance
    "ESG-I-01": 3, "ESG-I-02": 2, "ESG-I-03": 3,                  # Data Integration
}

esg_report = run_assessment(
    "esg_ai_monitoring_template.json",
    "MAADEN-ESG-2026-001",
    "Ma'aden (Saudi Arabian Mining Company)",
    esg_scores,
    target_level=4,
)

print(esg_report["text_heat_map"])
print()
print(f"Overall Score   : {esg_report['overall_score']}/5.00")
print(f"Overall Maturity: {esg_report['overall_maturity']}")
""")

# --- Demo 4: ESG Radar Chart ---
md("## Demo 4: ESG Governance Maturity Radar Chart")

code("""\
esg_domain_names = [d["domain_name"] for d in esg_report["domain_heat_map"]]
esg_domain_scores = [d["average_score"] for d in esg_report["domain_heat_map"]]

angles = np.linspace(0, 2 * np.pi, len(esg_domain_names), endpoint=False).tolist()
scores_closed = esg_domain_scores + [esg_domain_scores[0]]
angles_closed = angles + [angles[0]]
target_closed = [4] * (len(angles) + 1)

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.fill(angles_closed, scores_closed, alpha=0.25, color="#1976d2")
ax.plot(angles_closed, scores_closed, "o-", color="#1976d2", linewidth=2, label="Current Score")
ax.plot(angles_closed, target_closed, "--", color="#d32f2f", linewidth=1.5, alpha=0.7, label="Target (Level 4)")

ax.set_xticks(angles)
ax.set_xticklabels(esg_domain_names, fontsize=9)
ax.set_ylim(0, 5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_yticklabels(["1-Initial", "2-Developing", "3-Defined", "4-Managed", "5-Optimizing"], fontsize=8)
ax.set_title("ESG Governance Maturity Radar\\nMa'aden", fontsize=14, fontweight="bold", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.show()
""")

# --- Demo 5: Control-Level Heat Map ---
md("## Demo 5: Control-Level Governance Heat Map (All Controls)")

code("""\
hm_data = iso_report["heat_map_data"]
control_ids = [h["control_id"] for h in hm_data]
control_scores = [h["score"] for h in hm_data]
control_domains = [h["domain_id"] for h in hm_data]

fig, ax = plt.subplots(figsize=(14, 8))
cmap = plt.cm.RdYlGn
norm = plt.Normalize(vmin=1, vmax=5)

unique_domains = list(OrderedDict.fromkeys(control_domains))
y_pos = 0
y_positions = []
y_labels = []

for domain in unique_domains:
    domain_controls = [
        (h["control_id"], h["score"], h["control_name"])
        for h in hm_data if h["domain_id"] == domain
    ]
    for cid, score, cname in domain_controls:
        color = cmap(norm(score))
        ax.barh(y_pos, score, color=color, edgecolor="white", height=0.7)
        ax.text(score + 0.1, y_pos, f"{score}/5", va="center", fontsize=9, fontweight="bold")
        ax.text(-0.1, y_pos, f"{cid}", va="center", ha="right", fontsize=8, color="#555")
        y_positions.append(y_pos)
        y_labels.append(cname)
        y_pos += 1

ax.set_yticks(y_positions)
ax.set_yticklabels(y_labels, fontsize=8)
ax.set_xlim(-0.5, 6)
ax.set_xlabel("Maturity Score", fontsize=11)
ax.set_title(
    "ISO/IEC 42001 \\u2014 Control-Level Maturity Heat Map\\nMa'aden",
    fontsize=14, fontweight="bold",
)
ax.axvline(x=4, color="red", linestyle="--", alpha=0.5, label="Target")

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, shrink=0.6)
cbar.set_label("Maturity Level")
cbar.set_ticks([1, 2, 3, 4, 5])
cbar.set_ticklabels(["1-Initial", "2-Developing", "3-Defined", "4-Managed", "5-Optimizing"])

ax.legend(loc="lower right")
ax.invert_yaxis()
plt.tight_layout()
plt.show()
""")

# --- Demo 6: ML Prediction ---
md("## Demo 6: ML-Based Maturity Trend Prediction")

code("""\
# Historical maturity scores (quarterly assessments)
historical = [
    (1, 1.8), (2, 2.1), (3, 2.4), (4, 2.6),
    (5, 2.8), (6, 3.0), (7, 3.1), (8, 3.2),
]

prediction = run_maturity_prediction(historical, forecast_periods=8, target_level=4.0)
model = prediction["model_summary"]

print("Maturity Trend Analysis (OLS Linear Regression)")
print("=" * 50)
print(f"  Slope      : {model['slope']:+.4f} per period")
print(f"  Intercept  : {model['intercept']:.4f}")
print(f"  R-squared  : {model['r_squared']:.4f}")
print(f"  Trend      : {model['trend'].upper()}")
if prediction["time_to_target"]:
    print(f"  Est. periods to Level 4.0: {prediction['time_to_target']:.1f}")
print()

# ── Visualization ──
fig, ax = plt.subplots(figsize=(12, 6))

hist_times = [h["time"] for h in prediction["historical_data"]]
hist_scores = [h["score"] for h in prediction["historical_data"]]
fore_times = [f["time"] for f in prediction["forecasts"]]
fore_scores = [f["predicted_score"] for f in prediction["forecasts"]]

ax.plot(hist_times, hist_scores, "o-", color="#1976d2", linewidth=2,
        markersize=8, label="Historical", zorder=5)
ax.plot(fore_times, fore_scores, "s--", color="#f57c00", linewidth=2,
        markersize=8, label="Forecast", zorder=5)

# Regression line
all_times = hist_times + fore_times
pred = prediction["_predictor"]
reg_x = range(int(min(all_times)), int(max(all_times)) + 1)
reg_y = [pred.predict(t) for t in reg_x]
ax.plot(reg_x, reg_y, "-", color="gray", alpha=0.4, linewidth=1)

# Target line
ax.axhline(y=4.0, color="#d32f2f", linestyle="--", alpha=0.7, label="Target: Level 4 (MANAGED)")

# Maturity level bands
for level, label, color in [
    (1, "Initial", "#ffcdd2"), (2, "Developing", "#fff9c4"),
    (3, "Defined", "#c8e6c9"), (4, "Managed", "#bbdefb"),
    (5, "Optimizing", "#e1bee7"),
]:
    ax.axhspan(level - 0.5, level + 0.5, alpha=0.15, color=color)
    ax.text(max(all_times) + 0.3, level, label, fontsize=8, va="center", color="#555")

ax.set_xlabel("Assessment Period (Quarter)", fontsize=12)
ax.set_ylabel("Maturity Score", fontsize=12)
ax.set_title(
    f"AI Governance Maturity Trend Prediction\\n"
    f"Slope={model['slope']:+.4f}, R\\u00b2={model['r_squared']:.4f}, "
    f"Trend={model['trend'].upper()}",
    fontsize=14, fontweight="bold",
)
ax.set_ylim(0.5, 5.5)
ax.set_xlim(0.5, max(all_times) + 1)
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()
""")

# --- Demo 7: Use Case Portfolio ---
md("## Demo 7: Mining AI-ML Use Case Portfolio & Priority Ranking")

code("""\
catalogue = get_mining_use_case_catalogue()
ranked = rank_use_cases(catalogue)

# Print ranking table
print(f"{'Rank':>4}  {'Score':>6}  {'Use Case':<45}  {'Status':<12}  {'Risk':<10}  Recommendation")
dash = "\\u2500"
print(f"{dash * 4}  {dash * 6}  {dash * 45}  {dash * 12}  {dash * 10}  {dash * 35}")
for i, r in enumerate(ranked, 1):
    uc = next(u for u in catalogue if u.use_case_id == r["use_case_id"])
    print(
        f"{i:4d}  {r['composite_score']:6.1f}  "
        f"{r['name'][:45]:<45}  {uc.status.name:<12}  "
        f"{uc.risk_level.name:<10}  {r['recommendation'][:50]}"
    )

print()

# ── Stacked bar chart ──
fig, ax = plt.subplots(figsize=(14, 7))
names = [r["name"][:35] for r in ranked]
impact = [r["impact_score"] for r in ranked]
readiness = [r["readiness_score"] for r in ranked]
risk = [r["risk_score"] for r in ranked]
governance = [r["governance_score"] for r in ranked]
y = range(len(names))

ax.barh(y, impact, color="#1976d2", label="Business Impact", height=0.6)
ax.barh(y, readiness, left=impact, color="#388e3c", label="Technical Readiness", height=0.6)
ax.barh(y, risk, left=[i + r for i, r in zip(impact, readiness)],
        color="#f57c00", label="Risk Score", height=0.6)
ax.barh(y, governance, left=[i + r + k for i, r, k in zip(impact, readiness, risk)],
        color="#7b1fa2", label="Governance", height=0.6)

for i, r in enumerate(ranked):
    ax.text(r["composite_score"] + 0.5, i, f"{r['composite_score']:.0f}",
            va="center", fontweight="bold", fontsize=10)

ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=9)
ax.set_xlabel("Priority Score (0-100)", fontsize=12)
ax.set_title("Mining AI-ML Use Case Priority Ranking\\n(Multi-Criteria Weighted Scoring)",
             fontsize=14, fontweight="bold")
ax.legend(loc="lower right")
ax.axvline(x=75, color="green", linestyle="--", alpha=0.5)
ax.axvline(x=55, color="orange", linestyle="--", alpha=0.5)
ax.invert_yaxis()
plt.tight_layout()
plt.show()
""")

# --- Demo 8: Gap Analysis ---
md("## Demo 8: Gap Analysis Visualization")

code("""\
gaps = iso_report["gap_analysis"]
gap_domains = list(gaps.keys())
gap_current = [gaps[d]["current_score"] for d in gap_domains]
gap_target = [gaps[d]["target_level"] for d in gap_domains]
gap_values = [gaps[d]["gap"] for d in gap_domains]
gap_names = [gaps[d]["domain_name"] for d in gap_domains]
gap_priorities = [gaps[d]["priority"] for d in gap_domains]

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(gap_domains))
width = 0.35

ax.bar(x - width / 2, gap_current, width, label="Current Score", color="#1976d2", edgecolor="white")
ax.bar(x + width / 2, gap_target, width, label="Target Level", color="#d32f2f", alpha=0.3, edgecolor="#d32f2f")

for i, (cur, gap, prio) in enumerate(zip(gap_current, gap_values, gap_priorities)):
    if gap > 0:
        color = "#d32f2f" if prio == "critical" else "#f57c00" if prio == "high" else "#fbc02d"
        ax.annotate(
            f"Gap: {gap:.1f}\\n({prio.upper()})",
            xy=(i, cur), xytext=(i + 0.3, cur + 0.3),
            fontsize=8, color=color, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
        )

ax.set_xticks(x)
ax.set_xticklabels(
    [f"[{d}]\\n{n[:20]}" for d, n in zip(gap_domains, gap_names)],
    fontsize=8, ha="center",
)
ax.set_ylabel("Score", fontsize=12)
ax.set_ylim(0, 5.5)
ax.set_title("ISO/IEC 42001 Gap Analysis \\u2014 Current vs. Target (Level 4)\\nMa'aden",
             fontsize=14, fontweight="bold")
ax.legend()
plt.tight_layout()
plt.show()
""")

# --- Demo 9: Deployment Test Protocol ---
md("## Demo 9: AI-ML Deployment Test Protocol")

code("""\
# Create protocol for SAG Mill Predictive Maintenance model
protocol = create_standard_test_protocol(
    "TP-2026-001", "MN-UC-001",
    "SAG Mill Predictive Maintenance Model", "2.1.0",
)

# Simulate test results
test_results = {
    "DQ-01": True, "DQ-02": True, "DQ-03": True,
    "MP-01": True, "MP-02": False, "MP-03": True,
    "BF-01": True, "BF-02": True,
    "SC-01": True, "SC-02": True,
    "IT-01": True, "IT-02": True, "IT-03": None,  # not yet tested
}
for step in protocol.steps:
    if step.step_id in test_results:
        step.passed = test_results[step.step_id]
        if step.passed is False:
            step.notes = "Edge case: underperforms on high-vibration anomaly patterns."

# Print summary
print(f"Protocol  : {protocol.protocol_id}")
print(f"Model     : {protocol.model_name} v{protocol.model_version}")
print(f"Completion: {protocol.completion_rate * 100:.0f}%")
print(f"Pass Rate : {protocol.pass_rate * 100:.0f}%")
result_str = "PASSED" if protocol.is_passed else ("INCOMPLETE" if not protocol.is_complete else "FAILED")
print(f"Result    : {result_str}")
print()

# ── Visualization ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Pie chart
pass_count = sum(1 for s in protocol.steps if s.passed is True)
fail_count = sum(1 for s in protocol.steps if s.passed is False)
pending_count = sum(1 for s in protocol.steps if s.passed is None)
axes[0].pie(
    [pass_count, fail_count, pending_count],
    labels=[f"Passed ({pass_count})", f"Failed ({fail_count})", f"Pending ({pending_count})"],
    colors=["#388e3c", "#d32f2f", "#9e9e9e"],
    autopct="%1.0f%%", startangle=90, textprops={"fontsize": 11},
)
axes[0].set_title("Test Protocol Results", fontsize=13, fontweight="bold")

# Stacked bar by category
type_counts = {}
for step in protocol.steps:
    vtype = step.validation_type
    if vtype not in type_counts:
        type_counts[vtype] = {"pass": 0, "fail": 0, "pending": 0}
    if step.passed is True:
        type_counts[vtype]["pass"] += 1
    elif step.passed is False:
        type_counts[vtype]["fail"] += 1
    else:
        type_counts[vtype]["pending"] += 1

vtypes = list(type_counts.keys())
type_labels = {
    "data_quality": "Data Quality", "model_performance": "Model Perf.",
    "bias": "Bias/Fairness", "security": "Security", "integration": "Integration",
}
x = np.arange(len(vtypes))
passes = [type_counts[v]["pass"] for v in vtypes]
fails = [type_counts[v]["fail"] for v in vtypes]
pendings = [type_counts[v]["pending"] for v in vtypes]

axes[1].bar(x, passes, color="#388e3c", label="Pass")
axes[1].bar(x, fails, bottom=passes, color="#d32f2f", label="Fail")
axes[1].bar(x, pendings, bottom=[p + f for p, f in zip(passes, fails)], color="#9e9e9e", label="Pending")
axes[1].set_xticks(x)
axes[1].set_xticklabels([type_labels.get(v, v) for v in vtypes], fontsize=9)
axes[1].set_ylabel("# Steps")
axes[1].set_title("Results by Category", fontsize=13, fontweight="bold")
axes[1].legend()

plt.suptitle("SAG Mill Predictive Maintenance \\u2014 Deployment Test Protocol",
             fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.show()
""")

# --- Demo 10: Executive Dashboard ---
md("## Demo 10: Executive Dashboard with Safety Data")

code("""\
# Create sample safety incidents
incidents = [
    SafetyIncidentRecord("INC-001", "MN-UC-001", "medium",
        "Predictive maintenance model missed early bearing degradation signal.",
        root_cause="Insufficient training data for low-frequency vibration patterns.",
        corrective_action="Retrained model with expanded vibration dataset.",
        is_resolved=True),
    SafetyIncidentRecord("INC-002", "MN-UC-003", "high",
        "Safety prediction model generated false negative for confined space hazard.",
        root_cause="NLP module failed to parse non-standard incident report format.",
        corrective_action="Updated NLP pipeline with additional report templates.",
        is_resolved=False),
    SafetyIncidentRecord("INC-003", "MN-UC-006", "critical",
        "Autonomous haul truck proximity alert triggered 0.5s late in simulation.",
        root_cause="Sensor fusion latency under heavy dust conditions.",
        corrective_action="Upgraded sensor preprocessing pipeline; added redundant LIDAR.",
        is_resolved=False),
    SafetyIncidentRecord("INC-004", "MN-UC-005", "low",
        "Energy optimization model recommended off-peak schedule conflicting with production.",
        root_cause="Production schedule constraint not included in optimization model.",
        corrective_action="Added production schedule as hard constraint in optimizer.",
        is_resolved=True),
]

# Render text dashboard
iso_result = iso_report["_result"]
dashboard_text = render_text_dashboard(iso_result, catalogue, incidents)
print(dashboard_text)
""")

# --- Demo 11: Best Practices ---
md("## Demo 11: AI Adoption Best Practices Framework")

code("""\
practices = get_ai_adoption_best_practices()

print("=" * 72)
print("  AI ADOPTION BEST PRACTICES FOR MINING/EXTRACTIVE INDUSTRY")
print("=" * 72)

for category, items in practices.items():
    label = category.replace("_", " ").title()
    print(f"\\n  {label}")
    print(f"  {'-' * 50}")
    for item in items:
        print(f"    [{item['id']}] {item['title']}")
        desc = item["description"]
        # Word-wrap at ~65 chars
        while len(desc) > 65:
            cut = desc[:65].rfind(" ")
            if cut < 0:
                cut = 65
            print(f"           {desc[:cut]}")
            desc = desc[cut:].strip()
        print(f"           {desc}")

total = sum(len(v) for v in practices.values())
print(f"\\n{'=' * 72}")
print(f"  Total: {total} best practices across {len(practices)} categories")
print("=" * 72)
""")

# --- Demo 12: Combined Comparison ---
md("## Demo 12: Combined ISO + ESG Framework Comparison")

code("""\
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# ISO 42001
iso_d = list(iso_report["domain_scores"].keys())
iso_s = list(iso_report["domain_scores"].values())
iso_n = [iso_report["gap_analysis"][d]["domain_name"][:25] for d in iso_d]

colors_iso = []
for s in iso_s:
    if s < 2.5: colors_iso.append("#d32f2f")
    elif s < 3.0: colors_iso.append("#f57c00")
    elif s < 3.5: colors_iso.append("#fbc02d")
    else: colors_iso.append("#388e3c")

axes[0].barh(range(len(iso_d)), iso_s, color=colors_iso, height=0.6)
axes[0].set_yticks(range(len(iso_d)))
axes[0].set_yticklabels(iso_n, fontsize=9)
axes[0].set_xlim(0, 5.5)
axes[0].axvline(x=4, color="red", linestyle="--", alpha=0.5)
axes[0].set_title(f"ISO/IEC 42001\\nOverall: {iso_report['overall_score']}/5.00",
                  fontsize=13, fontweight="bold")
axes[0].set_xlabel("Score")
for i, s in enumerate(iso_s):
    axes[0].text(s + 0.1, i, f"{s:.1f}", va="center", fontweight="bold")
axes[0].invert_yaxis()

# ESG
esg_d = list(esg_report["domain_scores"].keys())
esg_s = list(esg_report["domain_scores"].values())
esg_n = [esg_report["gap_analysis"][d]["domain_name"][:30] for d in esg_d]

colors_esg = []
for s in esg_s:
    if s < 2.5: colors_esg.append("#d32f2f")
    elif s < 3.0: colors_esg.append("#f57c00")
    elif s < 3.5: colors_esg.append("#fbc02d")
    else: colors_esg.append("#388e3c")

axes[1].barh(range(len(esg_d)), esg_s, color=colors_esg, height=0.6)
axes[1].set_yticks(range(len(esg_d)))
axes[1].set_yticklabels(esg_n, fontsize=9)
axes[1].set_xlim(0, 5.5)
axes[1].axvline(x=4, color="red", linestyle="--", alpha=0.5)
axes[1].set_title(f"ESG Monitoring\\nOverall: {esg_report['overall_score']}/5.00",
                  fontsize=13, fontweight="bold")
axes[1].set_xlabel("Score")
for i, s in enumerate(esg_s):
    axes[1].text(s + 0.1, i, f"{s:.1f}", va="center", fontweight="bold")
axes[1].invert_yaxis()

legend_elements = [
    mpatches.Patch(facecolor="#d32f2f", label="Critical (<2.5)"),
    mpatches.Patch(facecolor="#f57c00", label="Warning (2.5-3.0)"),
    mpatches.Patch(facecolor="#fbc02d", label="Acceptable (3.0-3.5)"),
    mpatches.Patch(facecolor="#388e3c", label="Strong (>3.5)"),
]
fig.legend(handles=legend_elements, loc="lower center", ncol=4,
           fontsize=10, bbox_to_anchor=(0.5, -0.02))
plt.suptitle("Ma'aden AI Governance \\u2014 Dual Framework Assessment",
             fontsize=15, fontweight="bold")
plt.tight_layout()
plt.show()
""")

# --- Demo 13: Unit Tests ---
md("## Demo 13: Self-Verification Unit Tests")

code("""\
# ── Test helpers ──
def assert_eq(a, b):
    assert a == b, f"{a} != {b}"

def assert_true(x):
    assert x, f"Expected True, got {x}"

def assert_false(x):
    assert not x, f"Expected False, got {x}"

def assert_none(x):
    assert x is None, f"Expected None, got {x}"

def assert_close(a, b, tol=0.01):
    assert abs(a - b) < tol, f"{a} not close to {b}"


# ── Define tests ──
test_results_list = []

def run_test(name, fn):
    try:
        fn()
        test_results_list.append((name, True, ""))
    except Exception as e:
        test_results_list.append((name, False, str(e)))


# Model tests
run_test("MaturityLevel enum values",
         lambda: assert_eq(MaturityLevel.INITIAL, 1))
run_test("Control maturity with score",
         lambda: assert_eq(
             GovernanceControl("C1", "T", "D", "D1", score=3).maturity_level,
             MaturityLevel.DEFINED))
run_test("Control maturity without score",
         lambda: assert_none(
             GovernanceControl("C1", "T", "D", "D1").maturity_level))
run_test("Domain average score",
         lambda: assert_close(
             GovernanceDomain("D1", "T", "D", [
                 GovernanceControl("C1", "A", "D", "D1", score=2),
                 GovernanceControl("C2", "B", "D", "D1", score=4),
             ]).average_score, 3.0))
run_test("Weighted score calculation",
         lambda: assert_close(
             GovernanceControl("C1", "T", "D", "D1", score=3, weight=2.0).weighted_score, 6.0))

# Template tests
run_test("ISO template loads (7 domains)",
         lambda: assert_eq(
             len(build_assessment_from_template("iso_42001_template.json", "T1", "Org").domains), 7))
run_test("ESG template loads (4 domains)",
         lambda: assert_eq(
             len(build_assessment_from_template("esg_ai_monitoring_template.json", "T2", "Org").domains), 4))

# Assessment tests
run_test("Full ISO assessment validates",
         lambda: assert_true(
             run_assessment("iso_42001_template.json", "T3", "Org", iso_scores)["is_valid"]))
run_test("Full ESG assessment validates",
         lambda: assert_true(
             run_assessment("esg_ai_monitoring_template.json", "T4", "Org", esg_scores)["is_valid"]))

# Scoring tests
run_test("Gap analysis: D2 meets target",
         lambda: assert_true(
             compute_gap_analysis(
                 build_assessment_from_template("iso_42001_template.json", "T", "O", iso_scores)
             )["D2"]["meets_target"]))

# ML prediction tests
def _test_predictor():
    p = MaturityPredictor()
    p.fit([1, 2, 3, 4], [1.5, 2.0, 2.5, 3.0])
    assert p._fitted
    assert p.slope > 0
    assert p.trend_direction == "improving"
    assert p.predict(5) > 3.0

run_test("MaturityPredictor fit & predict", _test_predictor)
run_test("Use case ranking returns results",
         lambda: assert_true(len(rank_use_cases(get_mining_use_case_catalogue())) > 0))

# Validation tests
run_test("Valid control passes",
         lambda: assert_true(
             validate_control(GovernanceControl("C1", "N", "D", "D1", score=3, evidence="e")).is_valid))
run_test("Empty control ID fails",
         lambda: assert_false(
             validate_control(GovernanceControl("", "N", "D", "D1")).is_valid))
run_test("Score out of range fails",
         lambda: assert_false(
             validate_control(GovernanceControl("C1", "N", "D", "D1", score=6)).is_valid))
run_test("Use case validation passes",
         lambda: assert_true(
             validate_use_case(get_mining_use_case_catalogue()[0]).is_valid))

# Protocol tests
run_test("Standard protocol has 13 steps",
         lambda: assert_eq(
             len(create_standard_test_protocol("P", "U", "M", "1").steps), 13))

def _test_protocol_pass():
    p = create_standard_test_protocol("P", "U", "M", "1")
    for s in p.steps:
        s.passed = True
    assert p.is_passed

run_test("Protocol passes when all steps pass", _test_protocol_pass)

# Mining catalogue tests
run_test("Catalogue has 8+ use cases",
         lambda: assert_true(len(get_mining_use_case_catalogue()) >= 8))
run_test("Best practices has 4 categories",
         lambda: assert_eq(len(get_ai_adoption_best_practices()), 4))
run_test("Categories has 12+ entries",
         lambda: assert_true(len(get_use_case_categories()) >= 12))

# ── Report results ──
passed = sum(1 for _, ok, _ in test_results_list if ok)
failed = sum(1 for _, ok, _ in test_results_list if not ok)

print()
print("=" * 60)
print(f"  TEST RESULTS: {passed} passed, {failed} failed, {len(test_results_list)} total")
print("=" * 60)
for name, ok, err in test_results_list:
    icon = "\\u2705" if ok else "\\u274c"
    print(f"  {icon} {name}")
    if err:
        print(f"       Error: {err}")
print("=" * 60)
""")

# --- Summary ---
md("""\
---

## Summary

This notebook demonstrates the complete **AI Governance Control Register
& Maturity Assessment Tool**, designed for the mining and extractive
industry context.

### Modules
| # | Module | Contents |
|---|--------|----------|
| 1 | **Data Models** | GovernanceControl, GovernanceDomain, AssessmentResult, AIUseCase, SafetyIncidentRecord |
| 2 | **Templates** | ISO/IEC 42001 (7 domains, 21 controls) + ESG Monitoring (4 domains, 15 controls) |
| 3 | **Scoring & ML** | Domain scoring, gap analysis, heat maps, MaturityPredictor (OLS), use case prioritization |
| 4 | **Validation** | Data integrity checks, use case validation, deployment test protocols (13 steps) |
| 5 | **Assessment Engine** | Template loading, full assessment pipeline, maturity forecasting |
| 6 | **Mining Use Cases** | 8 AI-ML use cases + 13 best practices for extractive industry |
| 7 | **Dashboard** | Executive summary, ESG KPIs, safety tracking, text dashboard |

### Key Capabilities for Ma'aden Senior Specialist Role
- AI-ML use case evaluation and prioritization for mining operations
- AI advisory modelling with ML algorithms (linear regression)
- AI-based ESG and safety dashboard data generation
- Testing and validation protocols for AI-ML deployments
- Best practices, standards, and policies for AI adoption
- Alignment with ISO/IEC 42001, Saudi Vision 2030, and Saudi Green Initiative

### Frameworks Covered
- **ISO/IEC 42001** \\u2014 AI Management Systems
- **AI-Based ESG Monitoring** \\u2014 Environmental, Social, and Governance

---
*Built with Python standard library + matplotlib. No external AI/ML frameworks required.*
""")

# ══════════════════════════════════════════════════════════════════════
# Write the notebook
# ══════════════════════════════════════════════════════════════════════
nb.cells = cells
nbformat.validate(nb)

with open("AI_Governance_Assessment_Tool.ipynb", "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"Notebook written: {len(cells)} cells")
