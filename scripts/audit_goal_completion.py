from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_paper_claims import build_claim_audit
from scripts.audit_submission_package import build_submission_package
from scripts.audit_thesis_readiness import build_thesis_readiness


def build_goal_completion_audit() -> dict[str, Any]:
    thesis = build_thesis_readiness()
    claims = build_claim_audit()
    package = build_submission_package()

    requirements = {row["id"]: row for row in thesis["requirements"]}
    claim_rows = {row["claim"]: row for row in claims["claims"]}
    items = [
        {
            "id": "taxonomy",
            "objective": "Propose a multi-turn coding-agent failure taxonomy.",
            "status": requirements["taxonomy"]["status"],
            "evidence": requirements["taxonomy"]["evidence"],
            "completion_effect": "complete",
        },
        {
            "id": "benchmark",
            "objective": "Build a 30-50 task Codex JSONL trace benchmark with baseline and intervention runs.",
            "status": requirements["benchmark"]["status"],
            "evidence": requirements["benchmark"]["evidence"],
            "completion_effect": "complete",
        },
        {
            "id": "codextrace",
            "objective": "Provide a GPU-free offline parser and diagnosis engine.",
            "status": requirements["codextrace"]["status"],
            "evidence": requirements["codextrace"]["evidence"],
            "completion_effect": "complete",
        },
        {
            "id": "trace_rule_detection",
            "objective": "Show trace-based rules can detect observable failure processes.",
            "status": requirements["process_rule_detection"]["status"],
            "evidence": requirements["process_rule_detection"]["evidence"],
            "completion_effect": "complete for boundary paper; limited for broad real-world claims",
        },
        {
            "id": "verification_lift",
            "objective": "Show harness intervention raises ordinary-baseline verification rate.",
            "status": requirements["verification_lift"]["status"],
            "evidence": requirements["verification_lift"]["evidence"],
            "completion_effect": "blocks original goal completion",
        },
        {
            "id": "success_or_waste",
            "objective": "Show intervention improves success and/or reduces tool-call and token waste.",
            "status": requirements["success_or_waste"]["status"],
            "evidence": requirements["success_or_waste"]["evidence"],
            "completion_effect": "complete for waste; success lift remains pilot-qualified",
        },
        {
            "id": "verification_behavior",
            "objective": "Show harness intervention changes verification behavior under saturated verification rates.",
            "status": requirements["verification_behavior"]["status"],
            "evidence": requirements["verification_behavior"]["evidence"],
            "completion_effect": "complete as boundary evidence; does not close ordinary verification-rate lift",
        },
        {
            "id": "rq4",
            "objective": "Identify trace signals that explain failures or detector boundaries.",
            "status": requirements["rq4_explanation"]["status"],
            "evidence": requirements["rq4_explanation"]["evidence"],
            "completion_effect": "complete for boundary-style RQ4",
        },
    ]
    blocking_items = [row for row in items if row["completion_effect"].startswith("blocks")]
    original_complete = thesis["summary"]["ready_for_original_thesis"] and not blocking_items
    boundary_ready = (
        thesis["summary"]["ready_for_boundary_result_paper"]
        and package["summary"]["package_ready_for_boundary_paper"]
        and claim_rows["Harness intervention increases verification rate."]["status"] == "unsupported"
    )
    next_decision = (
        "Revise the thesis to a boundary-result paper centered on waste reduction and trace-diagnosis limits; "
        "the ordinary-baseline verification-lift-v2 retest is complete and remains saturated."
    )
    return {
        "summary": {
            "items": len(items),
            "blocking_items": len(blocking_items),
            "original_goal_complete": original_complete,
            "boundary_result_paper_ready": boundary_ready,
            "should_mark_goal_complete": original_complete,
            "next_decision": next_decision,
        },
        "items": items,
        "blocking_items": blocking_items,
    }


def render_goal_completion_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Goal Completion Audit",
        "",
        "This generated audit checks the active original objective against current repository evidence.",
        "",
        "## Verdict",
        "",
        f"- Original goal complete: {'yes' if summary['original_goal_complete'] else 'no'}",
        f"- Boundary-result paper ready: {'yes' if summary['boundary_result_paper_ready'] else 'no'}",
        f"- Should mark active goal complete: {'yes' if summary['should_mark_goal_complete'] else 'no'}",
        f"- Blocking items: {summary['blocking_items']}",
        f"- Next decision: {summary['next_decision']}",
        "",
        "## Requirement Audit",
        "",
        "| ID | Status | Completion effect | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["items"]:
        lines.append(f"| {row['id']} | {row['status']} | {row['completion_effect']} | {row['evidence']} |")
    if result["blocking_items"]:
        lines.extend(["", "## Blocking Original-Thesis Items", ""])
        for row in result["blocking_items"]:
            lines.append(f"- `{row['id']}`: {row['objective']} Evidence: {row['evidence']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit active goal completion against current CodexTrace evidence.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_goal_completion_audit()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_goal_completion_audit_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["boundary_result_paper_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
