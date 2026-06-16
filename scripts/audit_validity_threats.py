from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_CLAIM_AUDIT = Path("docs/paper_claim_audit.json")
DEFAULT_THESIS_DECISION = Path("docs/thesis_revision_decision.json")
DEFAULT_HEADLINE_RESULTS = Path("docs/headline_results.json")


def build_validity_threats_audit(
    claim_audit_path: Path = DEFAULT_CLAIM_AUDIT,
    thesis_decision_path: Path = DEFAULT_THESIS_DECISION,
    headline_results_path: Path = DEFAULT_HEADLINE_RESULTS,
) -> dict[str, Any]:
    claims = _read_json(claim_audit_path)
    thesis_decision = _read_json(thesis_decision_path)
    headline = _read_json(headline_results_path)
    claim_rows = {row["claim"]: row for row in claims["claims"]}
    headline_rows = {row["id"]: row for row in headline["rows"]}

    rows = [
        {
            "id": "internal_validity",
            "threat": "Hidden graders may expose failures that visible trace process signals cannot explain.",
            "evidence": claim_rows["Strong task-level oracles remain necessary."]["evidence"],
            "mitigation": "Report trace diagnosis as process-level evidence and keep hidden-grader outcome oracles separate.",
            "paper_language": "Trace-only rules diagnose process failures but do not prove semantic correctness.",
        },
        {
            "id": "construct_validity",
            "threat": "Verification rate is saturated, so it is a weak construct for intervention benefit on current tasks.",
            "evidence": claim_rows["Harness intervention increases verification rate."]["evidence"],
            "mitigation": "Drop ordinary verification-rate lift as a finding and report waste metrics plus the no-verify ablation separately.",
            "paper_language": "Verification-rate lift is a negative boundary result, not a supported headline claim.",
        },
        {
            "id": "external_validity",
            "threat": "The artifact studies Codex CLI on pilot-scale fixture repositories, not all coding agents or SWE-bench-scale tasks.",
            "evidence": claim_rows["The benchmark has 30-50 coding tasks with baseline and intervention traces."]["evidence"],
            "mitigation": "Frame results as a 30-task hard-tier pilot plus auxiliary stress tiers; avoid broad population claims.",
            "paper_language": "Results are pilot-scale and Codex-CLI-specific.",
        },
        {
            "id": "conclusion_validity",
            "threat": "Single paired runs per task can show directional deltas but not stable population estimates.",
            "evidence": (
                f"hard30 success {headline_rows['hard30_success']['baseline']:.2f}->"
                f"{headline_rows['hard30_success']['intervention']:.2f}; "
                f"hard30 repeated calls {headline_rows['hard30_repeated_tool_calls']['baseline']:.2f}->"
                f"{headline_rows['hard30_repeated_tool_calls']['intervention']:.2f}; "
                f"hard30 token usage {headline_rows['hard30_token_usage']['baseline'] / 1000:.1f}k->"
                f"{headline_rows['hard30_token_usage']['intervention'] / 1000:.1f}k."
            ),
            "mitigation": "Use paired-task deltas as pilot evidence and call for repeated trials before population claims.",
            "paper_language": "Waste reduction is the strongest current RQ3 result; success lift remains pilot-qualified.",
        },
        {
            "id": "detector_validity",
            "threat": "Rule-based detectors are interpretable but incomplete and can miss hidden semantic edge cases.",
            "evidence": claim_rows["Trace-based process rules detect most failure processes."].get("evidence", ""),
            "mitigation": "Separate controlled-fixture detector coverage from natural real-pilot outcome detection.",
            "paper_language": "Detector results are boundary results for observable process failures; hidden semantic recall is 0.00 with FN=30.",
        },
        {
            "id": "ablation_validity",
            "threat": "The no-verify baseline is artificial and can overstate ordinary harness intervention effects.",
            "evidence": claim_rows["Harness constraints can control verification behavior under a no-verify ablation."].get("evidence", ""),
            "mitigation": "Treat the no-verify tier only as a mechanism check.",
            "paper_language": "No-verify ablation is not ordinary-baseline evidence.",
        },
        {
            "id": "reproducibility_validity",
            "threat": "Real Codex collection depends on CLI behavior and environment state.",
            "evidence": "Stored traces, generated reports, manual labels, reproduction commands, and readiness gates are committed.",
            "mitigation": "Support offline re-analysis without rerunning Codex; gate generated artifacts with tests and readiness checks.",
            "paper_language": "The artifact is reproducible for offline analysis, while new live collections may vary.",
        },
    ]
    covered = {row["id"] for row in rows}
    required = {
        "internal_validity",
        "construct_validity",
        "external_validity",
        "conclusion_validity",
        "detector_validity",
        "ablation_validity",
        "reproducibility_validity",
    }
    ready = (
        required.issubset(covered)
        and thesis_decision["summary"]["decision"] == "revise_to_boundary_result_paper"
        and thesis_decision["summary"]["ordinary_verification_rate_lift_supported"] is False
        and headline["summary"]["waste_reduction_supported"] is True
    )
    return {
        "summary": {
            "ready": ready,
            "threat_count": len(rows),
            "covered_count": len(covered & required),
            "required_count": len(required),
            "boundary_decision": thesis_decision["summary"]["decision"],
            "ordinary_verification_rate_lift_supported": thesis_decision["summary"]["ordinary_verification_rate_lift_supported"],
        },
        "threats": rows,
    }


def render_validity_threats_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Validity Threats Audit",
        "",
        "This generated audit maps paper validity threats to evidence, mitigations, and safe wording.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Threats covered: {summary['covered_count']} / {summary['required_count']}",
        f"- Boundary decision: {summary['boundary_decision']}",
        f"- Ordinary verification-rate lift supported: {'yes' if summary['ordinary_verification_rate_lift_supported'] else 'no'}",
        "",
        "## Threat Map",
        "",
        "| Threat area | Threat | Evidence | Mitigation | Paper language |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result["threats"]:
        lines.append(
            f"| `{row['id']}` | {row['threat']} | {row['evidence']} | {row['mitigation']} | {row['paper_language']} |"
        )
    lines.extend([
        "",
        "Interpretation: these threats are not blockers for a boundary-result paper, but they constrain the paper's wording and forbid broad verification-rate or hidden-correctness claims.",
    ])
    return "\n".join(lines) + "\n"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate validity-threat mapping for the CodexTrace paper artifact.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_validity_threats_audit()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_validity_threats_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
