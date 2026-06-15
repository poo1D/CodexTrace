from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path("docs/submission_readiness_plan.md")


def build_submission_readiness_plan_audit(plan_path: Path = DEFAULT_PLAN) -> dict[str, Any]:
    text = plan_path.read_text(encoding="utf-8")
    checks = [
        _check("current_evidence_level", "## Current Evidence Level", text),
        _check("stronger_submission_target", "## Target For A Stronger Submission", text),
        _check("repeat_hard30_workstream", "## Workstream 1: Repeat And Stress Hard30", text),
        _check("manual_labeling_workstream", "## Workstream 2: Improve Manual Labeling", text),
        _check("repeatability_workstream", "## Workstream 3: Repeatability And Variance", text),
        _check("rq4_workstream", "## Workstream 4: Better RQ4 Analysis", text),
        _check("decision_gate", "## Decision Gate", text),
        _check("current_gate_passes", "Current status: this gate passes for the stored hard30 artifact", text),
        _check("boundary_positioning", "submission-ready hard30 artifact", text),
        _check("honest_positioning", "A reproducible pilot artifact showing", text),
        _check("remaining_repeatability", "repeat a hard-tier subset to estimate variance", text),
        _check("remaining_process_positives", "collect more natural observable process-failure positives", text),
        _check("known_readiness_command", "scripts/check_submission_readiness.py", text),
    ]
    overclaim_checks = [
        {
            "id": "no_original_goal_complete_claim",
            "passed": "original goal complete: yes" not in _normalize(text)
            and "ready for original thesis: yes" not in _normalize(text),
            "expected": "no original-goal-complete claim",
        },
        {
            "id": "no_stronger_submission_complete_claim",
            "passed": "stronger submission complete" not in _normalize(text)
            and "stronger submission is complete" not in _normalize(text),
            "expected": "no stronger-submission-complete claim",
        },
    ]
    all_checks = checks + overclaim_checks
    missing = [row for row in all_checks if not row["passed"]]
    return {
        "summary": {
            "ready": not missing,
            "checks": len(all_checks),
            "passed": sum(1 for row in all_checks if row["passed"]),
            "missing": len(missing),
            "plan_path": str(plan_path),
        },
        "checks": all_checks,
        "missing": missing,
    }


def render_submission_readiness_plan_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Submission Readiness Plan Audit",
        "",
        "This generated audit checks that the stronger-submission plan preserves both the current boundary-result readiness and the remaining evidence gaps.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Checks passed: {summary['passed']} / {summary['checks']}",
        f"- Missing checks: {summary['missing']}",
        f"- Plan: `{summary['plan_path']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Expected |",
        "| --- | --- | --- |",
    ]
    for row in result["checks"]:
        lines.append(f"| `{row['id']}` | {'pass' if row['passed'] else 'fail'} | {row['expected']} |")
    lines.extend([
        "",
        "Interpretation: the current artifact can be reviewer-ready as a boundary-result pilot while the stronger-submission plan keeps repeatability and natural process-positive collection explicit.",
    ])
    return "\n".join(lines) + "\n"


def _check(check_id: str, phrase: str, text: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": _normalize(phrase) in _normalize(text),
        "expected": phrase,
    }


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the stronger-submission readiness plan.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_submission_readiness_plan_audit(args.plan)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_submission_readiness_plan_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
