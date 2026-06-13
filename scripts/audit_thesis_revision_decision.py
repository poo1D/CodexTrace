from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_THESIS_READINESS = Path("docs/thesis_readiness.json")
DEFAULT_CLAIM_AUDIT = Path("docs/paper_claim_audit.json")
DEFAULT_VERIFICATION_LIFT_DECISION = Path("docs/verification_lift_next_experiment.json")
DEFAULT_HEADLINE_RESULTS = Path("docs/headline_results.json")


def build_thesis_revision_decision(
    thesis_readiness_path: Path = DEFAULT_THESIS_READINESS,
    claim_audit_path: Path = DEFAULT_CLAIM_AUDIT,
    verification_lift_decision_path: Path = DEFAULT_VERIFICATION_LIFT_DECISION,
    headline_results_path: Path = DEFAULT_HEADLINE_RESULTS,
) -> dict[str, Any]:
    thesis = _read_json(thesis_readiness_path)
    claims = _read_json(claim_audit_path)
    verification = _read_json(verification_lift_decision_path)
    headline = _read_json(headline_results_path)

    requirements = {row["id"]: row for row in thesis["requirements"]}
    claim_rows = {row["claim"]: row for row in claims["claims"]}
    headline_rows = {row["id"]: row for row in headline["rows"]}

    decision_rows = [
        {
            "id": "failure_taxonomy",
            "original_claim": "Observable multi-turn coding-agent failure modes can be categorized.",
            "decision": "keep",
            "paper_framing": "Use the six-label process taxonomy as a contribution.",
            "evidence": requirements["taxonomy"]["evidence"],
        },
        {
            "id": "trace_rule_detection",
            "original_claim": "Trace rules detect most failure processes.",
            "decision": "narrow",
            "paper_framing": "Claim trace-only rules detect observable process positives and expose hidden-semantic limits.",
            "evidence": requirements["process_rule_detection"]["evidence"],
        },
        {
            "id": "verification_rate_lift",
            "original_claim": "Harness intervention increases ordinary-baseline verification rate.",
            "decision": "drop_as_finding",
            "paper_framing": "Report saturated ordinary baselines as a negative result and limitation.",
            "evidence": claim_rows["Harness intervention increases verification rate."]["evidence"],
        },
        {
            "id": "no_verify_ablation",
            "original_claim": "No-verify ablation shows harness control over verification behavior.",
            "decision": "keep_as_mechanism_check",
            "paper_framing": "Use only as an auxiliary mechanism check, not as ordinary-baseline evidence.",
            "evidence": headline_rows["no_verify_ablation_verification"]["interpretation"],
        },
        {
            "id": "waste_reduction",
            "original_claim": "Harness intervention reduces tool-call and token waste.",
            "decision": "keep",
            "paper_framing": "Lead RQ3 with paired hard30 waste reduction and supporting pilots.",
            "evidence": claim_rows["Harness intervention reduces repeated tool-call and token waste."]["evidence"],
        },
        {
            "id": "success_lift",
            "original_claim": "Harness intervention increases success rate.",
            "decision": "qualify",
            "paper_framing": "Report hard10 lift as pilot-qualified and hard30 as flat.",
            "evidence": claim_rows["Harness intervention increases success rate."]["evidence"],
        },
        {
            "id": "rq4_signals",
            "original_claim": "Trace signals explain whether an agent will fail.",
            "decision": "narrow",
            "paper_framing": "Explain observable process failure signals and the hidden-semantic boundary, not all correctness failures.",
            "evidence": claim_rows["Trace signals explain observable process failures and the hidden-semantic boundary."]["evidence"],
        },
    ]

    ready = (
        thesis["summary"]["ready_for_original_thesis"] is False
        and thesis["summary"]["ready_for_boundary_result_paper"] is True
        and verification["claim_revision_required"] is True
        and verification["additional_ordinary_baseline_experiment_required"] is False
        and headline["summary"]["ordinary_verification_rate_lift_supported"] is False
        and headline["summary"]["waste_reduction_supported"] is True
        and claim_rows["Harness intervention increases verification rate."]["status"] == "unsupported"
    )
    return {
        "summary": {
            "ready": ready,
            "decision": "revise_to_boundary_result_paper",
            "ready_for_original_thesis": thesis["summary"]["ready_for_original_thesis"],
            "ready_for_boundary_result_paper": thesis["summary"]["ready_for_boundary_result_paper"],
            "claim_revision_required": verification["claim_revision_required"],
            "additional_ordinary_baseline_experiment_required": verification["additional_ordinary_baseline_experiment_required"],
            "ordinary_verification_rate_lift_supported": headline["summary"]["ordinary_verification_rate_lift_supported"],
            "recommended_thesis": (
                "Coding-agent traces can diagnose observable multi-turn process failures and quantify harness-level waste reduction, "
                "but ordinary Codex baselines already verify on these small tasks, so verification-rate lift should be reported as a negative boundary result."
            ),
        },
        "decisions": decision_rows,
    }


def render_thesis_revision_decision_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Thesis Revision Decision",
        "",
        "This generated decision memo records how the original thesis should be revised given the current evidence.",
        "",
        "## Verdict",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Decision: {summary['decision']}",
        f"- Ready for original thesis: {'yes' if summary['ready_for_original_thesis'] else 'no'}",
        f"- Ready for boundary-result paper: {'yes' if summary['ready_for_boundary_result_paper'] else 'no'}",
        f"- Claim revision required: {'yes' if summary['claim_revision_required'] else 'no'}",
        f"- Additional ordinary-baseline experiment required: {'yes' if summary['additional_ordinary_baseline_experiment_required'] else 'no'}",
        f"- Ordinary verification-rate lift supported: {'yes' if summary['ordinary_verification_rate_lift_supported'] else 'no'}",
        f"- Recommended thesis: {summary['recommended_thesis']}",
        "",
        "## Claim Decisions",
        "",
        "| Claim area | Decision | Paper framing | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["decisions"]:
        lines.append(f"| `{row['id']}` | {row['decision']} | {row['paper_framing']} | {row['evidence']} |")
    lines.extend([
        "",
        "Interpretation: the paper can be submitted as a boundary-result artifact if it drops the ordinary verification-rate-lift finding, keeps the no-verify ablation separate, and leads RQ3 with waste reduction rather than verification-rate lift.",
    ])
    return "\n".join(lines) + "\n"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the CodexTrace thesis-revision decision memo.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_thesis_revision_decision()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_thesis_revision_decision_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
