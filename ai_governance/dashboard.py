"""AI-based ESG & safety dashboard data generator.

Generates structured data for ESG monitoring dashboards and safety analytics,
suitable for rendering in web-based visualization tools. Designed for
mining/extractive industry organizations managing AI governance alongside
environmental, social, and safety KPIs.
"""

import statistics
from typing import Any

from .models import AIUseCase, AssessmentResult, SafetyIncidentRecord
from .scoring import (
    compute_domain_scores,
    compute_gap_analysis,
    generate_domain_heat_map,
    rank_use_cases,
)


def generate_executive_summary(
    assessment: AssessmentResult,
    use_cases: list[AIUseCase] | None = None,
    incidents: list[SafetyIncidentRecord] | None = None,
) -> dict[str, Any]:
    """Generate an executive summary dashboard combining governance, ESG, and safety data.

    This is the top-level dashboard view a Director of Technology CoE or
    Chief Sustainability Officer would review.
    """
    domain_scores = compute_domain_scores(assessment)
    gaps = compute_gap_analysis(assessment, target_level=3)

    summary: dict[str, Any] = {
        "organization": assessment.organization,
        "framework": assessment.framework,
        "assessment_id": assessment.assessment_id,
        "overall_maturity": {
            "score": round(assessment.overall_score, 2) if assessment.overall_score else None,
            "level": assessment.overall_maturity.name if assessment.overall_maturity else None,
            "controls_assessed": assessment.scored_controls,
            "controls_total": assessment.total_controls,
        },
        "domain_summary": generate_domain_heat_map(assessment),
        "gap_analysis": gaps,
        "domains_below_target": sum(1 for g in gaps.values() if not g["meets_target"]),
        "domains_meeting_target": sum(1 for g in gaps.values() if g["meets_target"]),
    }

    if use_cases:
        uc_summary = _summarize_use_cases(use_cases)
        summary["ai_use_cases"] = uc_summary

    if incidents:
        safety_summary = _summarize_safety_incidents(incidents)
        summary["safety_overview"] = safety_summary

    return summary


def _summarize_use_cases(use_cases: list[AIUseCase]) -> dict[str, Any]:
    """Generate a summary of the AI-ML use case portfolio."""
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_risk: dict[str, int] = {}

    for uc in use_cases:
        status_name = uc.status.name
        by_status[status_name] = by_status.get(status_name, 0) + 1
        by_category[uc.category] = by_category.get(uc.category, 0) + 1
        risk_name = uc.risk_level.name
        by_risk[risk_name] = by_risk.get(risk_name, 0) + 1

    ranked = rank_use_cases(use_cases)
    top_priorities = ranked[:3] if len(ranked) >= 3 else ranked

    return {
        "total_use_cases": len(use_cases),
        "by_status": by_status,
        "by_category": by_category,
        "by_risk_level": by_risk,
        "top_priorities": [
            {"name": p["name"], "score": p["composite_score"], "recommendation": p["recommendation"]}
            for p in top_priorities
        ],
    }


def _summarize_safety_incidents(incidents: list[SafetyIncidentRecord]) -> dict[str, Any]:
    """Generate a safety incident summary for the dashboard."""
    by_severity: dict[str, int] = {}
    resolved = 0
    unresolved = 0

    for inc in incidents:
        by_severity[inc.severity] = by_severity.get(inc.severity, 0) + 1
        if inc.is_resolved:
            resolved += 1
        else:
            unresolved += 1

    return {
        "total_incidents": len(incidents),
        "resolved": resolved,
        "unresolved": unresolved,
        "by_severity": by_severity,
        "resolution_rate": round(resolved / len(incidents) * 100, 1) if incidents else 0.0,
    }


def generate_esg_kpi_data(assessment: AssessmentResult) -> dict[str, Any]:
    """Generate ESG-specific KPI data for dashboard display.

    Extracts and structures ESG-relevant metrics from the assessment,
    suitable for visualization in a sustainability dashboard.
    """
    esg_domains = {
        "environmental": [],
        "social": [],
        "governance": [],
    }

    for domain in assessment.domains:
        did = domain.domain_id.upper()
        if "ESG-E" in did or "ENVIRON" in domain.name.upper():
            esg_domains["environmental"].append(domain)
        elif "ESG-S" in did or "SOCIAL" in domain.name.upper():
            esg_domains["social"].append(domain)
        elif "ESG-G" in did or "GOVERNANCE" in domain.name.upper() or "ESG-I" in did:
            esg_domains["governance"].append(domain)

    kpis: dict[str, Any] = {}
    for pillar, domains in esg_domains.items():
        if not domains:
            continue
        scores = [d.average_score for d in domains if d.average_score is not None]
        kpis[pillar] = {
            "domains": len(domains),
            "average_score": round(statistics.mean(scores), 2) if scores else None,
            "min_score": round(min(scores), 2) if scores else None,
            "max_score": round(max(scores), 2) if scores else None,
            "controls": sum(len(d.controls) for d in domains),
        }

    return {
        "framework": assessment.framework,
        "esg_pillars": kpis,
        "overall_esg_score": round(
            statistics.mean(
                [v["average_score"] for v in kpis.values() if v["average_score"] is not None]
            ), 2
        ) if any(v["average_score"] is not None for v in kpis.values()) else None,
    }


def generate_safety_dashboard_data(
    use_cases: list[AIUseCase],
    incidents: list[SafetyIncidentRecord],
) -> dict[str, Any]:
    """Generate data for an AI-powered safety dashboard.

    Combines AI use case status with safety incident tracking,
    designed for the Safety & Sustainability business unit.
    """
    safety_use_cases = [uc for uc in use_cases if uc.category == "safety"]
    safety_adjacent = [
        uc for uc in use_cases
        if uc.category in ("predictive_maintenance", "autonomous_systems", "environmental_monitoring")
    ]

    unresolved_critical = [
        inc for inc in incidents
        if inc.severity in ("high", "critical") and not inc.is_resolved
    ]

    return {
        "safety_ai_use_cases": {
            "direct_safety": len(safety_use_cases),
            "safety_adjacent": len(safety_adjacent),
            "total_safety_related": len(safety_use_cases) + len(safety_adjacent),
            "details": [
                {
                    "id": uc.use_case_id,
                    "name": uc.name,
                    "status": uc.status.name,
                    "risk_level": uc.risk_level.name,
                }
                for uc in safety_use_cases + safety_adjacent
            ],
        },
        "incident_tracking": _summarize_safety_incidents(incidents),
        "critical_alerts": [
            {
                "incident_id": inc.incident_id,
                "description": inc.description,
                "severity": inc.severity,
            }
            for inc in unresolved_critical
        ],
    }


def render_text_dashboard(
    assessment: AssessmentResult,
    use_cases: list[AIUseCase] | None = None,
    incidents: list[SafetyIncidentRecord] | None = None,
) -> str:
    """Render a complete text-based dashboard for terminal display."""
    summary = generate_executive_summary(assessment, use_cases, incidents)
    lines: list[str] = []

    lines.append(f"{'='*72}")
    lines.append(f"  AI GOVERNANCE & ESG EXECUTIVE DASHBOARD")
    lines.append(f"  Organization: {summary['organization']}")
    lines.append(f"  Framework: {summary['framework']}")
    lines.append(f"{'='*72}")

    # Maturity overview
    m = summary["overall_maturity"]
    lines.append(f"\n  MATURITY OVERVIEW")
    lines.append(f"  {'-'*40}")
    lines.append(f"  Overall Score:      {m['score'] or 'N/A'}/5.00")
    lines.append(f"  Maturity Level:     {m['level'] or 'N/A'}")
    lines.append(f"  Controls Assessed:  {m['controls_assessed']}/{m['controls_total']}")
    lines.append(f"  Domains on Target:  {summary['domains_meeting_target']}/{summary['domains_meeting_target'] + summary['domains_below_target']}")

    # Domain heat map
    lines.append(f"\n  DOMAIN HEAT MAP")
    lines.append(f"  {'-'*40}")
    BLOCKS = {1: "█", 2: "▓", 3: "▒", 4: "░", 5: " "}
    for d in summary["domain_summary"]:
        score = d["average_score"]
        bar_len = round(score)
        block = BLOCKS.get(bar_len, "?")
        bar = block * bar_len + "." * (5 - bar_len)
        sev = d["severity"].upper()[:4]
        lines.append(f"    {d['domain_id']:12s} |{bar}| {score:.1f}  {sev:4s}  {d['domain_name']}")

    # Gap analysis
    gaps_found = {k: v for k, v in summary["gap_analysis"].items() if not v["meets_target"]}
    if gaps_found:
        lines.append(f"\n  GAP ANALYSIS (Below Target)")
        lines.append(f"  {'-'*40}")
        for domain_id, gap_info in gaps_found.items():
            prio = gap_info["priority"].upper()
            lines.append(
                f"    {domain_id:12s}  gap={gap_info['gap']:.1f}  priority={prio:8s}  {gap_info['domain_name']}"
            )

    # AI use case portfolio
    if "ai_use_cases" in summary:
        uc = summary["ai_use_cases"]
        lines.append(f"\n  AI-ML USE CASE PORTFOLIO ({uc['total_use_cases']} use cases)")
        lines.append(f"  {'-'*40}")
        for status, count in sorted(uc["by_status"].items()):
            lines.append(f"    {status:16s}: {count}")
        if uc.get("top_priorities"):
            lines.append(f"\n  Top Priorities:")
            for p in uc["top_priorities"]:
                lines.append(f"    [{p['score']:5.1f}] {p['name']}")

    # Safety overview
    if "safety_overview" in summary:
        so = summary["safety_overview"]
        lines.append(f"\n  SAFETY INCIDENT OVERVIEW")
        lines.append(f"  {'-'*40}")
        lines.append(f"  Total: {so['total_incidents']}  |  Resolved: {so['resolved']}  |  Unresolved: {so['unresolved']}  |  Resolution: {so['resolution_rate']}%")
        for sev, count in sorted(so["by_severity"].items()):
            lines.append(f"    {sev:12s}: {count}")

    lines.append(f"\n{'='*72}")
    return "\n".join(lines)
