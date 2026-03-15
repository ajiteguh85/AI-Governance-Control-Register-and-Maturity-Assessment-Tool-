"""CLI entry point for the AI Governance Assessment Tool.

Usage:
    python main.py --template iso_42001_template.json --org "Acme Corp" --scores scores.json
    python main.py --template esg_ai_monitoring_template.json --org "GreenCo" --scores scores.json
"""

import argparse
import json
import sys
import uuid

from ai_governance.assessment import run_assessment


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Governance Control Register & Maturity Assessment Tool"
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Template filename (e.g. iso_42001_template.json or esg_ai_monitoring_template.json)",
    )
    parser.add_argument(
        "--org",
        required=True,
        help="Organization name being assessed",
    )
    parser.add_argument(
        "--scores",
        required=True,
        help="Path to JSON file mapping control_id to score (1-5)",
    )
    parser.add_argument(
        "--target-level",
        type=int,
        default=3,
        help="Target maturity level for gap analysis (default: 3)",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write JSON report output",
    )

    args = parser.parse_args()

    with open(args.scores, "r", encoding="utf-8") as f:
        scores = json.load(f)

    assessment_id = f"ASSESS-{uuid.uuid4().hex[:8].upper()}"

    report = run_assessment(args.template, assessment_id, args.org, scores)

    if not report["is_valid"]:
        print("VALIDATION ERRORS:")
        for err in report["validation_errors"]:
            if err["severity"] == "error":
                print(f"  [{err['severity'].upper()}] {err['field']}: {err['message']}")
        sys.exit(1)

    print(report["text_heat_map"])
    print()
    print(f"Overall Score: {report['overall_score']}/5.00")
    print(f"Overall Maturity: {report['overall_maturity']}")
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
                f"gap={gap_info['gap']}"
            )
        print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Full report written to: {args.output}")


if __name__ == "__main__":
    main()
