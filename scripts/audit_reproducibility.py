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
    {"id": "rq4_signal_audit", "phrase": "scripts/audit_rq4_signals.py"},
    {"id": "metric_coverage_audit", "phrase": "scripts/audit_metric_coverage.py"},
    {"id": "failure_taxonomy_audit", "phrase": "scripts/audit_failure_taxonomy.py"},
    {"id": "related_work_audit", "phrase": "scripts/audit_related_work.py"},
    {"id": "paper_structure_audit", "phrase": "scripts/audit_paper_structure.py"},
    {
        "id": "hard30_paper_report",
        "phrase": "codex_trace.cli research paper-report \\\n  benchmark/hard/pilot/hard30-real/runs.jsonl",
    },
    {"id": "hard30_task_diagnosis", "phrase": "scripts/audit_hard30_task_diagnosis.py"},
    {"id": "combined_summary", "phrase": "codex_trace.cli research summary"},
    {"id": "thesis_readiness", "phrase": "scripts/audit_thesis_readiness.py"},
    {"id": "goal_completion", "phrase": "scripts/audit_goal_completion.py"},
    {"id": "paper_number_guard", "phrase": "scripts/audit_paper_numbers.py"},
    {"id": "reviewer_path_audit", "phrase": "scripts/audit_reviewer_path.py"},
    {"id": "submission_package", "phrase": "scripts/audit_submission_package.py"},
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

    fence_count = text.count("```")
    bash_fence_count = text.count("```bash")
    return {
        "summary": {
            "ready": all(row["present"] for row in command_rows) and fence_count % 2 == 0,
            "required_command_count": len(command_rows),
            "covered_command_count": sum(1 for row in command_rows if row["present"]),
            "fence_count": fence_count,
            "bash_fence_count": bash_fence_count,
            "fences_balanced": fence_count % 2 == 0,
            "checklist_path": str(checklist_path),
        },
        "commands": command_rows,
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
        "Interpretation: this audit checks command presence and Markdown structure. It does not execute the full real Codex collection commands.",
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
