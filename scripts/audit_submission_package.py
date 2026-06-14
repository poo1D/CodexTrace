from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_paper_claims import build_claim_audit
from scripts.audit_thesis_readiness import build_thesis_readiness


def build_submission_package() -> dict[str, Any]:
    claim_audit = build_claim_audit()
    thesis = build_thesis_readiness()
    claims_by_name = {row["claim"]: row for row in claim_audit["claims"]}
    requirements_by_id = {row["id"]: row for row in thesis["requirements"]}

    rq_rows = [
        {
            "rq": "RQ1",
            "question": "What observable multi-turn coding-agent failure modes appear?",
            "status": requirements_by_id["taxonomy"]["status"],
            "claim_boundary": "Use the six-label process taxonomy; do not imply the current real pilots cover every label equally.",
            "primary_evidence": [
                "docs/failure_taxonomy.md",
                "docs/failure_taxonomy_audit.md",
                "benchmark/detector-fixtures/label-eval.md",
                "docs/results_summary.md",
            ],
            "paper_action": "Frame RQ1 as an observable process taxonomy plus limited natural positives.",
        },
        {
            "rq": "RQ2",
            "question": "Can these failure modes be detected from trace signals alone?",
            "status": claims_by_name["Trace-based process rules detect most failure processes."]["status"],
            "claim_boundary": "Supported for rule fixtures and observed process positives; not supported for hidden semantic failures.",
            "primary_evidence": [
                "docs/failure_taxonomy_audit.md",
                "benchmark/detector-fixtures/label-eval.md",
                "benchmark/hard/pilot/hard30-real/label-eval.md",
                "benchmark/pilot/full30-real/process-label-eval.md",
            ],
            "paper_action": "Report trace-only detection as a boundary result, with hidden semantic false negatives explicit.",
        },
        {
            "rq": "RQ3",
            "question": "Do harness interventions reduce failures or waste?",
            "status": claims_by_name["Harness intervention reduces repeated tool-call and token waste."]["status"],
            "claim_boundary": "Waste reduction is supported; success lift is pilot-qualified; ordinary verification-rate lift is unsupported.",
            "primary_evidence": [
                "docs/results_summary.md",
                "docs/hard30_task_diagnosis.md",
                "docs/paper_claim_audit.md",
            ],
            "paper_action": "Lead with hard30 paired waste reduction and treat no-verify verification lift as mechanism ablation only.",
        },
        {
            "rq": "RQ4",
            "question": "Which trace signals explain failure?",
            "status": requirements_by_id["rq4_explanation"]["status"],
            "claim_boundary": "Signals explain observable process positives and the hidden-semantic boundary, not hidden correctness by themselves.",
            "primary_evidence": [
                "docs/rq4_signal_audit.md",
                "docs/results_summary.md",
                "benchmark/hard/pilot/hard30-real/paper-report-labeled.md",
            ],
            "paper_action": "Show the signal table as an explanation of where trace diagnosis works and where task oracles are still required.",
        },
    ]

    unsupported_claims = [
        row for row in claim_audit["claims"]
        if row["status"] == "unsupported"
    ]
    partial_claims = [
        row for row in claim_audit["claims"]
        if row["status"] == "partial"
    ]
    package_ready = (
        thesis["summary"]["ready_for_boundary_result_paper"]
        and not any(row["status"] == "missing" and row["id"] != "verification_lift" for row in thesis["requirements"])
        and claims_by_name["Harness intervention increases verification rate."]["status"] == "unsupported"
    )
    return {
        "summary": {
            "rq_count": len(rq_rows),
            "package_ready_for_boundary_paper": package_ready,
            "ready_for_original_thesis": thesis["summary"]["ready_for_original_thesis"],
            "ready_for_boundary_result_paper": thesis["summary"]["ready_for_boundary_result_paper"],
            "unsupported_claim_count": len(unsupported_claims),
            "partial_claim_count": len(partial_claims),
            "required_boundary": "ordinary verification-rate lift remains unsupported; no-verify lift is an ablation only",
        },
        "rq_rows": rq_rows,
        "unsupported_claims": unsupported_claims,
        "partial_claims": partial_claims,
        "required_files": [
            "README.md",
            "docs/artifact_guide.md",
            "docs/submission_package.md",
            "docs/goal_completion_audit.md",
            "docs/thesis_revision_decision.md",
            "docs/validity_threats.md",
            "docs/verification_lift_next_experiment.md",
            "docs/verification_lift_v2_plan_audit.md",
            "docs/headline_results.md",
            "docs/paper_draft.md",
            "docs/paper_abstract_audit.md",
            "docs/paper_contribution_audit.md",
            "docs/paper_structure_audit.md",
            "docs/paper_outline.md",
            "docs/related_work.md",
            "docs/related_work_audit.md",
            "docs/bibliography_audit.md",
            "docs/experiment_protocol.md",
            "docs/claim_text_guard.md",
            "docs/paper_number_guard.md",
            "docs/reviewer_path_audit.md",
            "docs/metric_coverage_audit.md",
            "docs/phase_coverage_audit.md",
            "docs/task_category_coverage.md",
            "docs/harness_protocol_audit.md",
            "docs/failure_taxonomy_audit.md",
            "docs/results_summary.md",
            "docs/paper_claim_audit.md",
            "docs/thesis_readiness.md",
            "docs/rq4_signal_audit.md",
            "docs/hard30_task_diagnosis.md",
            "docs/reproducibility_checklist.md",
            "docs/reproducibility_audit.md",
        ],
    }


def render_submission_package_markdown(package: dict[str, Any]) -> str:
    summary = package["summary"]
    lines = [
        "# CodexTrace Submission Package Map",
        "",
        "This generated map turns the current evidence into reviewer-facing paper claims.",
        "",
        "## Summary",
        "",
        f"- RQs mapped: {summary['rq_count']}",
        f"- Ready for original thesis: {'yes' if summary['ready_for_original_thesis'] else 'no'}",
        f"- Ready for boundary-result paper: {'yes' if summary['ready_for_boundary_result_paper'] else 'no'}",
        f"- Package ready for boundary paper: {'yes' if summary['package_ready_for_boundary_paper'] else 'no'}",
        f"- Unsupported claims: {summary['unsupported_claim_count']}",
        f"- Partial claims: {summary['partial_claim_count']}",
        f"- Required boundary: {summary['required_boundary']}",
        "",
        "## RQ-To-Evidence Map",
        "",
        "| RQ | Status | Evidence | Boundary | Paper action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in package["rq_rows"]:
        evidence = ", ".join(f"`{path}`" for path in row["primary_evidence"])
        lines.append(
            f"| {row['rq']} | {row['status']} | {evidence} | {row['claim_boundary']} | {row['paper_action']} |"
        )

    lines.extend(["", "## Unsupported Claims To Avoid", ""])
    for row in package["unsupported_claims"]:
        lines.append(f"- {row['claim']} Evidence: {row['evidence']} Action: {row['action']}")

    lines.extend(["", "## Partial Claims Requiring Qualifiers", ""])
    for row in package["partial_claims"]:
        lines.append(f"- {row['claim']} Evidence: {row['evidence']} Action: {row['action']}")

    lines.extend(["", "## Required Reviewer Files", ""])
    lines.extend(f"- `{path}`" for path in package["required_files"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the CodexTrace submission package claim/evidence map.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    package = build_submission_package()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_submission_package_markdown(package)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if package["summary"]["package_ready_for_boundary_paper"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
