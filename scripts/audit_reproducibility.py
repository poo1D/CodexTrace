from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_CHECKLIST = Path("docs/reproducibility_checklist.md")

REQUIRED_COMMANDS = (
    {
        "id": "full30_aggregate",
        "phrase": "codex_trace.cli research aggregate \\\n  benchmark/pilot/full30-real/runs.jsonl",
    },
    {
        "id": "controlled_fixture_eval",
        "phrase": "benchmark/detector-fixtures/runs.jsonl \\\n  benchmark/detector-fixtures/labels.jsonl",
    },
    {"id": "detector_evaluation_audit", "phrase": "scripts/audit_detector_evaluation.py"},
    {"id": "rule_implementation_audit", "phrase": "scripts/audit_rule_implementation.py"},
    {"id": "rq4_signal_audit", "phrase": "scripts/audit_rq4_signals.py"},
    {"id": "metric_coverage_audit", "phrase": "scripts/audit_metric_coverage.py"},
    {"id": "paired_effects_audit", "phrase": "scripts/audit_paired_effects.py"},
    {"id": "paired_effect_limitations_audit", "phrase": "scripts/audit_paired_effect_limitations.py"},
    {"id": "demo_audit", "phrase": "scripts/audit_demo.py"},
    {"id": "web_artifact_audit", "phrase": "scripts/audit_web_artifact.py"},
    {"id": "cli_surface_audit", "phrase": "scripts/audit_cli_surface.py"},
    {"id": "ci_surface_audit", "phrase": "scripts/audit_ci_surface.py"},
    {"id": "schema_field_audit", "phrase": "scripts/audit_schema_fields.py"},
    {"id": "parser_event_coverage", "phrase": "scripts/audit_parser_event_coverage.py"},
    {"id": "failure_node_traceability", "phrase": "scripts/audit_failure_node_traceability.py"},
    {"id": "phase_coverage_audit", "phrase": "scripts/audit_phase_coverage.py"},
    {"id": "task_category_coverage_audit", "phrase": "scripts/audit_task_category_coverage.py"},
    {"id": "harness_protocol_audit", "phrase": "scripts/audit_harness_protocol.py"},
    {"id": "failure_taxonomy_audit", "phrase": "scripts/audit_failure_taxonomy.py"},
    {"id": "related_work_audit", "phrase": "scripts/audit_related_work.py"},
    {"id": "bibliography_audit", "phrase": "scripts/audit_bibliography.py"},
    {"id": "paper_abstract_audit", "phrase": "scripts/audit_paper_abstract.py"},
    {"id": "paper_contribution_audit", "phrase": "scripts/audit_paper_contributions.py"},
    {"id": "paper_conclusion_audit", "phrase": "scripts/audit_paper_conclusion.py"},
    {"id": "paper_structure_audit", "phrase": "scripts/audit_paper_structure.py"},
    {"id": "method_pipeline_audit", "phrase": "scripts/audit_method_pipeline.py"},
    {"id": "rq_table_consistency_audit", "phrase": "scripts/audit_rq_table_consistency.py"},
    {
        "id": "hard30_paper_report",
        "phrase": "codex_trace.cli research paper-report \\\n  benchmark/hard/pilot/hard30-real/runs.jsonl",
    },
    {"id": "hard30_task_diagnosis", "phrase": "scripts/audit_hard30_task_diagnosis.py"},
    {"id": "combined_summary", "phrase": "codex_trace.cli research summary"},
    {"id": "thesis_readiness", "phrase": "scripts/audit_thesis_readiness.py"},
    {"id": "goal_completion", "phrase": "scripts/audit_goal_completion.py"},
    {"id": "submission_readiness_plan_audit", "phrase": "scripts/audit_submission_readiness_plan.py"},
    {"id": "thesis_revision_decision", "phrase": "scripts/audit_thesis_revision_decision.py"},
    {"id": "validity_threats", "phrase": "scripts/audit_validity_threats.py"},
    {"id": "limitations_traceability_audit", "phrase": "scripts/audit_limitations_traceability.py"},
    {"id": "expected_results_reconciliation", "phrase": "scripts/audit_expected_results_reconciliation.py"},
    {"id": "paper_number_guard", "phrase": "scripts/audit_paper_numbers.py"},
    {"id": "reviewer_path_audit", "phrase": "scripts/audit_reviewer_path.py"},
    {"id": "artifact_guide_sequence_audit", "phrase": "scripts/audit_artifact_guide_sequence.py"},
    {"id": "benchmark_trace_artifact", "phrase": "scripts/audit_benchmark_trace_artifact.py"},
    {"id": "label_provenance_audit", "phrase": "scripts/audit_label_provenance.py"},
    {"id": "label_limitations_audit", "phrase": "scripts/audit_label_limitations.py"},
    {"id": "verification_saturation_audit", "phrase": "scripts/audit_verification_saturation.py"},
    {"id": "submission_package", "phrase": "scripts/audit_submission_package.py"},
    {"id": "headline_results", "phrase": "scripts/audit_headline_results.py"},
    {"id": "verification_ablation_plan", "phrase": "scripts/audit_verification_ablation_plan.py"},
    {"id": "verification_lift_v2_collection", "phrase": "scripts/run_benchmark_shards.py"},
    {"id": "verification_lift_v2_finalize", "phrase": "scripts/finalize_benchmark_pilot.py"},
    {
        "id": "verification_ablation_outputs",
        "phrase": "benchmark/verification-ablation/pilot/full-real/runs.jsonl",
    },
    {"id": "submission_readiness_gate", "phrase": "scripts/check_submission_readiness.py"},
    {"id": "paper_claim_audit", "phrase": "scripts/audit_paper_claims.py"},
    {"id": "claim_text_guard", "phrase": "scripts/audit_claim_text_guard.py"},
)
REQUIRED_SEMANTIC_PHRASES = (
    {
        "id": "nullable_timing_metrics",
        "phrase": "nullable timing metrics",
    },
    {
        "id": "rule_evidence_tiers",
        "phrase": "detector evidence tiers",
    },
    {
        "id": "task_design_family_mapping",
        "phrase": "design-family mapping",
    },
)


def build_reproducibility_audit(checklist_path: Path = DEFAULT_CHECKLIST) -> dict[str, Any]:
    text = checklist_path.read_text(encoding="utf-8")
    normalized_text = _normalize(text)
    command_rows = []
    for command in REQUIRED_COMMANDS:
        present = _normalize(command["phrase"]) in normalized_text
        command_rows.append({
            "id": command["id"],
            "phrase": command["phrase"],
            "present": present,
        })
    semantic_rows = []
    for phrase in REQUIRED_SEMANTIC_PHRASES:
        present = _normalize(phrase["phrase"]) in normalized_text
        semantic_rows.append({
            "id": phrase["id"],
            "phrase": phrase["phrase"],
            "present": present,
        })

    fence_count = text.count("```")
    bash_fence_count = text.count("```bash")
    return {
        "summary": {
            "ready": (
                all(row["present"] for row in command_rows)
                and all(row["present"] for row in semantic_rows)
                and fence_count % 2 == 0
            ),
            "required_command_count": len(command_rows),
            "covered_command_count": sum(1 for row in command_rows if row["present"]),
            "required_semantic_phrase_count": len(semantic_rows),
            "covered_semantic_phrase_count": sum(1 for row in semantic_rows if row["present"]),
            "fence_count": fence_count,
            "bash_fence_count": bash_fence_count,
            "fences_balanced": fence_count % 2 == 0,
            "checklist_path": str(checklist_path),
        },
        "commands": command_rows,
        "semantic_phrases": semantic_rows,
    }


def render_reproducibility_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Reproducibility Checklist Audit",
        "",
        "This generated audit checks that the reviewer-facing reproducibility checklist contains the key commands needed to regenerate CodexTrace paper artifacts.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Commands covered: {summary['covered_command_count']} / {summary['required_command_count']}",
        f"- Semantic phrases covered: {summary['covered_semantic_phrase_count']} / {summary['required_semantic_phrase_count']}",
        f"- Markdown fences balanced: {'yes' if summary['fences_balanced'] else 'no'}",
        f"- Bash command blocks: {summary['bash_fence_count']}",
        f"- Checklist: `{summary['checklist_path']}`",
        "",
        "## Command Coverage",
        "",
        "| Command area | Covered |",
        "| --- | --- |",
    ]
    for row in result["commands"]:
        lines.append(f"| {row['id']} | {'yes' if row['present'] else 'no'} |")
    lines.extend([
        "",
        "## Semantic Phrase Coverage",
        "",
        "| Reproducibility note | Covered |",
        "| --- | --- |",
    ])
    for row in result["semantic_phrases"]:
        lines.append(f"| {row['id']} | {'yes' if row['present'] else 'no'} |")
    lines.extend([
        "",
        "Interpretation: this audit checks command presence, key reproducibility semantics, and Markdown structure. It does not execute the full real Codex collection commands.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_reproducibility_audit_markdown(result), encoding="utf-8")


def _normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit reproducibility checklist command coverage.")
    parser.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_reproducibility_audit(args.checklist)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_reproducibility_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
