"""CLI entry point for the AI Governance Control Register & Maturity Assessment Tool.

Supports three modes:
  assess   — Run a governance assessment against a template
  demo     — Run a full demonstration with mining industry data
  usecases — Display and rank mining AI-ML use cases

Usage:
    python main.py assess --template iso_42001_template.json --org "Ma'aden" --scores scores.json
    python main.py demo
    python main.py usecases
"""

import argparse
import json
import sys
import uuid

from ai_governance.assessment import run_assessment, run_maturity_prediction
from ai_governance.dashboard import render_text_dashboard
from ai_governance.mining_use_cases import (
    get_ai_adoption_best_practices,
    get_mining_use_case_catalogue,
    get_use_case_categories,
)
from ai_governance.models import SafetyIncidentRecord
from ai_governance.scoring import (
    compute_use_case_priority_score,
    rank_use_cases,
    render_text_heat_map,
)
from ai_governance.validation import (
    create_standard_test_protocol,
    render_protocol_report,
    validate_use_case,
)


def cmd_assess(args: argparse.Namespace) -> None:
    """Run a governance assessment from CLI arguments."""
    with open(args.scores, "r", encoding="utf-8") as f:
        scores = json.load(f)

    assessment_id = f"ASSESS-{uuid.uuid4().hex[:8].upper()}"
    report = run_assessment(args.template, assessment_id, args.org, scores, args.target_level)

    if not report["is_valid"]:
        print("VALIDATION ERRORS:")
        for err in report["validation_errors"]:
            if err["severity"] == "error":
                print(f"  [{err['severity'].upper()}] {err['field']}: {err['message']}")
        sys.exit(1)

    print(report["text_heat_map"])
    print()
    print(f"Overall Score: {report['overall_score']}/5.00  ({report['overall_maturity']})")
    print(f"Controls Assessed: {report['controls_assessed']}/{report['controls_total']}")
    print()

    if report["validation_errors"]:
        print("Warnings:")
        for err in report["validation_errors"]:
            if err["severity"] == "warning":
                print(f"  {err['field']}: {err['message']}")
        print()

    gaps = report["gap_analysis"]
    gaps_found = {k: v for k, v in gaps.items() if not v["meets_target"]}
    if gaps_found:
        print("Gap Analysis (domains below target):")
        for domain_id, gap_info in gaps_found.items():
            print(
                f"  {domain_id} ({gap_info['domain_name']}): "
                f"current={gap_info['current_score']}, "
                f"target={gap_info['target_level']}, "
                f"gap={gap_info['gap']}, "
                f"priority={gap_info['priority'].upper()}"
            )
        print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Full report written to: {args.output}")


def cmd_demo(args: argparse.Namespace) -> None:
    """Run a comprehensive demonstration with mining industry data."""
    print("=" * 72)
    print("  AI GOVERNANCE CONTROL REGISTER & MATURITY ASSESSMENT TOOL")
    print("  Comprehensive Demo — Mining & Extractive Industry")
    print("=" * 72)

    # --- Part 1: ISO 42001 Assessment for Ma'aden ---
    print("\n\n[1/6] ISO/IEC 42001 AI Management System Assessment")
    print("-" * 50)
    iso_scores = {
        "D1-C01": 3, "D1-C02": 4, "D1-C03": 3,
        "D2-C01": 4, "D2-C02": 3, "D2-C03": 4,
        "D3-C01": 2, "D3-C02": 2, "D3-C03": 3,
        "D4-C01": 4, "D4-C02": 3, "D4-C03": 3,
        "D5-C01": 3, "D5-C02": 2, "D5-C03": 3, "D5-C04": 2,
        "D6-C01": 4, "D6-C02": 3, "D6-C03": 3,
        "D7-C01": 3, "D7-C02": 4,
    }
    iso_report = run_assessment(
        "iso_42001_template.json", "MAADEN-ISO-2026-001", "Ma'aden (Saudi Arabian Mining Company)",
        iso_scores, target_level=4,
    )
    print(iso_report["text_heat_map"])

    # --- Part 2: ESG Assessment ---
    print("\n\n[2/6] AI-Based ESG Monitoring Governance Assessment")
    print("-" * 50)
    esg_scores = {
        "ESG-E-01": 4, "ESG-E-02": 3, "ESG-E-03": 2, "ESG-E-04": 3,
        "ESG-S-01": 3, "ESG-S-02": 3, "ESG-S-03": 2, "ESG-S-04": 3,
        "ESG-G-01": 4, "ESG-G-02": 3, "ESG-G-03": 3, "ESG-G-04": 2,
        "ESG-I-01": 3, "ESG-I-02": 2, "ESG-I-03": 3,
    }
    esg_report = run_assessment(
        "esg_ai_monitoring_template.json", "MAADEN-ESG-2026-001", "Ma'aden (Saudi Arabian Mining Company)",
        esg_scores, target_level=4,
    )
    print(esg_report["text_heat_map"])

    # --- Part 3: Mining AI-ML Use Case Registry ---
    print("\n\n[3/6] Mining Industry AI-ML Use Case Portfolio & Priority Ranking")
    print("-" * 50)
    catalogue = get_mining_use_case_catalogue()
    ranked = rank_use_cases(catalogue)
    print(f"\n  {'Rank':>4s}  {'Score':>6s}  {'Status':12s}  {'Risk':10s}  Use Case")
    print(f"  {'----':>4s}  {'-----':>6s}  {'------':12s}  {'----':10s}  {'--------'}")
    for i, uc in enumerate(ranked, 1):
        print(f"  {i:4d}  {uc['composite_score']:6.1f}  {catalogue[0].status.name:12s}  {uc['recommendation'][:40]}")
        # Find original UC for status
        orig = next(c for c in catalogue if c.use_case_id == uc["use_case_id"])
        print(f"        {' ':6s}  {orig.status.name:12s}  {orig.risk_level.name:10s}  {uc['name']}")

    # --- Part 4: ML Maturity Prediction ---
    print("\n\n[4/6] ML-Based Maturity Trend Prediction")
    print("-" * 50)
    historical = [
        (1, 1.8), (2, 2.1), (3, 2.4), (4, 2.6),
        (5, 2.8), (6, 3.0), (7, 3.1), (8, 3.2),
    ]
    prediction = run_maturity_prediction(historical, forecast_periods=6, target_level=4.0)
    model = prediction["model_summary"]
    print(f"\n  Trend Analysis (OLS Linear Regression)")
    print(f"  Slope:     {model['slope']:+.4f} per period")
    print(f"  R-squared: {model['r_squared']:.4f}")
    print(f"  Trend:     {model['trend'].upper()}")
    print(f"\n  Historical & Forecast:")
    for h in prediction["historical_data"]:
        bar = "█" * round(h["score"] * 4)
        print(f"    Period {h['time']:2.0f}:  {h['score']:.2f}  {bar}")
    for f in prediction["forecasts"]:
        bar = "░" * round(f["predicted_score"] * 4)
        print(f"    Period {f['time']:2.0f}:  {f['predicted_score']:.2f}  {bar}  (forecast)")
    if prediction["time_to_target"]:
        print(f"\n  Estimated periods to reach Level 4.0: {prediction['time_to_target']:.1f}")
    else:
        print(f"\n  Target level 4.0 not reachable with current trend.")

    # --- Part 5: Deployment Test Protocol ---
    print("\n\n[5/6] AI-ML Deployment Test Protocol")
    print("-" * 50)
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
        "IT-01": True, "IT-02": True, "IT-03": None,
    }
    for step in protocol.steps:
        if step.step_id in test_results:
            step.passed = test_results[step.step_id]
            if step.passed is False:
                step.notes = "Edge case: model underperforms on high-vibration anomaly patterns."
    print(render_protocol_report(protocol))

    # --- Part 6: Executive Dashboard ---
    print("\n\n[6/6] AI Governance & ESG Executive Dashboard")
    print("-" * 50)
    from ai_governance.assessment import build_assessment_from_template, TEMPLATES_DIR

    esg_result = build_assessment_from_template(
        TEMPLATES_DIR / "esg_ai_monitoring_template.json",
        "MAADEN-ESG-2026-001", "Ma'aden (Saudi Arabian Mining Company)", esg_scores,
    )
    incidents = [
        SafetyIncidentRecord("INC-001", "MN-UC-003", "medium", "False positive safety alert in Zone B"),
        SafetyIncidentRecord("INC-002", "MN-UC-006", "high", "Haul truck proximity sensor miscalibration", is_resolved=True),
        SafetyIncidentRecord("INC-003", "MN-UC-001", "low", "Delayed maintenance prediction for conveyor belt", is_resolved=True),
    ]
    print(render_text_dashboard(esg_result, catalogue, incidents))

    # --- Best Practices Summary ---
    print("\n\n  AI ADOPTION BEST PRACTICES FRAMEWORK")
    print("  " + "-" * 40)
    practices = get_ai_adoption_best_practices()
    for category, items in practices.items():
        label = category.replace("_", " ").title()
        print(f"\n  {label}:")
        for item in items:
            print(f"    [{item['id']}] {item['title']}")

    print(f"\n{'='*72}")
    print("  Demo complete. All modules operational.")
    print(f"{'='*72}\n")


def cmd_usecases(args: argparse.Namespace) -> None:
    """Display mining AI-ML use case catalogue and validation."""
    catalogue = get_mining_use_case_catalogue()
    categories = get_use_case_categories()

    print("=" * 72)
    print("  MINING INDUSTRY AI-ML USE CASE REGISTRY")
    print("=" * 72)

    print("\n  Standard Categories:")
    for cat, desc in categories.items():
        print(f"    {cat:30s}  {desc}")

    print(f"\n  Registered Use Cases ({len(catalogue)}):")
    print(f"  {'-'*62}")
    for uc in catalogue:
        validation = validate_use_case(uc)
        status = "OK" if validation.is_valid else "ERR"
        warns = len(validation.warnings)
        priority = compute_use_case_priority_score(uc)
        print(f"\n    [{status}] {uc.use_case_id}: {uc.name}")
        print(f"          Category: {uc.category}  |  Status: {uc.status.name}  |  Risk: {uc.risk_level.name}")
        print(f"          Priority Score: {priority['composite_score']:.1f}/100  —  {priority['recommendation']}")
        print(f"          AI Techniques: {', '.join(uc.ai_techniques[:3])}")
        if warns:
            print(f"          Warnings: {warns}")

    print(f"\n{'='*72}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Governance Control Register & Maturity Assessment Tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # assess command
    assess_parser = subparsers.add_parser("assess", help="Run a governance assessment")
    assess_parser.add_argument("--template", required=True, help="Template filename")
    assess_parser.add_argument("--org", required=True, help="Organization name")
    assess_parser.add_argument("--scores", required=True, help="Path to JSON scores file")
    assess_parser.add_argument("--target-level", type=int, default=3, help="Target maturity level (default: 3)")
    assess_parser.add_argument("--output", help="Path to write JSON report")

    # demo command
    subparsers.add_parser("demo", help="Run comprehensive demonstration")

    # usecases command
    subparsers.add_parser("usecases", help="Display mining AI-ML use case catalogue")

    args = parser.parse_args()

    if args.command == "assess":
        cmd_assess(args)
    elif args.command == "demo":
        cmd_demo(args)
    elif args.command == "usecases":
        cmd_usecases(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
