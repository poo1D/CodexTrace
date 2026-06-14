from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_PAPER = Path("docs/paper_draft.md")
DEFAULT_HARD30_REPORT_JSON = Path("benchmark/hard/pilot/hard30-real/paper-report-labeled.json")
DEFAULT_HARD30_REPORT_MD = Path("benchmark/hard/pilot/hard30-real/paper-report-labeled.md")


def build_rq_table_consistency_audit(
    paper_path: Path = DEFAULT_PAPER,
    hard30_report_json: Path = DEFAULT_HARD30_REPORT_JSON,
    hard30_report_md: Path = DEFAULT_HARD30_REPORT_MD,
) -> dict[str, Any]:
    paper_text = _normalize(paper_path.read_text(encoding="utf-8"))
    report_text = _normalize(hard30_report_md.read_text(encoding="utf-8"))
    report = json.loads(hard30_report_json.read_text(encoding="utf-8"))

    checks = (
        _rq1_checks(report),
        _rq2_checks(report),
        _rq3_checks(report),
        _rq4_checks(report),
    )
    rows = []
    for rq, rq_checks in zip(("RQ1", "RQ2", "RQ3", "RQ4"), checks):
        for check in rq_checks:
            paper_present = _normalize(check["paper_snippet"]) in paper_text
            report_present = _normalize(check["report_snippet"]) in report_text
            value_ok = bool(check["value_ok"])
            rows.append({
                "rq": rq,
                "id": check["id"],
                "value_ok": value_ok,
                "paper_present": paper_present,
                "report_present": report_present,
                "covered": value_ok and paper_present and report_present,
                "expected": check["expected"],
                "paper_snippet": check["paper_snippet"],
                "report_snippet": check["report_snippet"],
            })

    return {
        "summary": {
            "ready": all(row["covered"] for row in rows),
            "check_count": len(rows),
            "covered_check_count": sum(1 for row in rows if row["covered"]),
            "rq_count": 4,
            "paper_path": str(paper_path),
            "hard30_report_json": str(hard30_report_json),
            "hard30_report_md": str(hard30_report_md),
        },
        "checks": rows,
    }


def render_rq_table_consistency_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# RQ Table Consistency Audit",
        "",
        "This generated audit checks that the paper draft's RQ1-RQ4 result-table claims match the generated hard30 paper report.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- RQs covered: {summary['rq_count']} / 4",
        f"- Table checks covered: {summary['covered_check_count']} / {summary['check_count']}",
        f"- Paper draft: `{summary['paper_path']}`",
        f"- Hard30 report JSON: `{summary['hard30_report_json']}`",
        f"- Hard30 report Markdown: `{summary['hard30_report_md']}`",
        "",
        "## Checks",
        "",
        "| RQ | Check | Value | Paper | Report | Covered |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["checks"]:
        lines.append(
            f"| {row['rq']} | `{row['id']}` | {'yes' if row['value_ok'] else 'no'} | "
            f"{'yes' if row['paper_present'] else 'no'} | {'yes' if row['report_present'] else 'no'} | "
            f"{'yes' if row['covered'] else 'no'} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit guards the paper's RQ result tables against drift from generated hard30 report artifacts. It does not add new statistical evidence.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_rq_table_consistency_markdown(result), encoding="utf-8")


def _rq1_checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    distribution = {row["failure_tag"]: row for row in report["taxonomy_distribution"]}
    return [
        {
            "id": "hidden_semantic_distribution",
            "value_ok": distribution["hidden_semantic_edge_case"]["count"] == 30,
            "expected": "hard30 hidden_semantic_edge_case count is 30",
            "paper_snippet": "| hard30 | `hidden_semantic_edge_case` | 30 | `HARD-001/baseline` |",
            "report_snippet": "| hidden_semantic_edge_case | 30 | 88.24 | HARD-001/baseline |",
        },
        {
            "id": "repetitive_distribution",
            "value_ok": distribution["repetitive_exploration"]["count"] == 4,
            "expected": "hard30 repetitive_exploration count is 4",
            "paper_snippet": "| hard30 | `repetitive_exploration` | 4 | `HARD-011/baseline` |",
            "report_snippet": "| repetitive_exploration | 4 | 11.76 | HARD-011/baseline |",
        },
    ]


def _rq2_checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    labels = report["detector_evaluation"]["labels"]
    hidden = labels["hidden_semantic_edge_case"]
    repetitive = labels["repetitive_exploration"]
    return [
        {
            "id": "hidden_semantic_detector_boundary",
            "value_ok": hidden["tp"] == 0 and hidden["fn"] == 30 and hidden["f1"] == 0,
            "expected": "hidden semantic labels are trace-only false negatives",
            "paper_snippet": "| `hidden_semantic_edge_case` | 0 | 0 | 30 | 0 | 0 | 0 |",
            "report_snippet": "| hidden_semantic_edge_case | 0 | 0 | 30 | 0 | 0 | 0 |",
        },
        {
            "id": "repetitive_detector_positive",
            "value_ok": repetitive["tp"] == 4 and repetitive["fn"] == 0 and repetitive["f1"] == 1,
            "expected": "repetitive exploration positives are detected",
            "paper_snippet": "| `repetitive_exploration` | 4 | 0 | 0 | 1 | 1 | 1 |",
            "report_snippet": "| repetitive_exploration | 4 | 0 | 0 | 1 | 1 | 1 |",
        },
    ]


def _rq3_checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    aggregate = report["aggregate"]
    summary = aggregate["summary"]
    paired = report["paired_task_summary"]
    return [
        {
            "id": "hard30_flat_success",
            "value_ok": summary["baseline"]["success_rate"] == 0.5 and summary["intervention"]["success_rate"] == 0.5,
            "expected": "hard30 success is flat at 0.50 -> 0.50",
            "paper_snippet": "| success_rate | 0.50 | 0.50 | 0.00 |",
            "report_snippet": "| success_rate | 0.5 | 0.5 | 0 |",
        },
        {
            "id": "hard30_waste_reduction",
            "value_ok": (
                round(summary["baseline"]["avg_repeated_tool_calls"], 2) == 12.93
                and round(summary["intervention"]["avg_repeated_tool_calls"], 2) == 9.20
                and round(aggregate["deltas"]["avg_repeated_tool_calls"], 3) == -3.733
            ),
            "expected": "hard30 repeated tool calls drop 12.93 -> 9.20",
            "paper_snippet": "| hard30 waste | 12.93 repeated calls / 355.0k tokens | 9.20 repeated calls / 256.3k tokens |",
            "report_snippet": "| avg_repeated_tool_calls | 12.93 | 9.2 | -3.733 |",
        },
        {
            "id": "paired_token_improvement",
            "value_ok": paired["token_usage_delta"]["improved"] == 26 and paired["token_usage_delta"]["n"] == 30,
            "expected": "token usage improves in 26 of 30 paired tasks",
            "paper_snippet": "token usage improves in 26 of 30 tasks",
            "report_snippet": "| token usage | 26 | 4 | 0 | -9.866e+04 |",
        },
    ]


def _rq4_checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    outcome = {row["signal"]: row for row in report["signal_by_outcome"]}
    counts = report["outcome_counts"]
    return [
        {
            "id": "outcome_counts",
            "value_ok": counts["failure"] == 30 and counts["success"] == 30,
            "expected": "hard30 has 30 failures and 30 successes",
            "paper_snippet": "The hard30 artifact contains 30 failed and 30 successful runs.",
            "report_snippet": "Outcome counts: failure=30, success=30, unknown=0.",
        },
        {
            "id": "verification_signal_boundary",
            "value_ok": outcome["verification_rate"]["delta_success_minus_failure"] == 0,
            "expected": "verification_rate does not separate hard30 success and failure",
            "paper_snippet": "| verification_rate | 1.00 | 1.00 | 0.00 |",
            "report_snippet": "| verification_rate | 1 | 1 | 0 |",
        },
        {
            "id": "unresolved_error_boundary",
            "value_ok": outcome["unresolved_error"]["delta_success_minus_failure"] == 0,
            "expected": "unresolved_error does not separate hard30 success and failure",
            "paper_snippet": "| unresolved_error | 0 | 0 | 0 |",
            "report_snippet": "| unresolved_error | 0 | 0 | 0 |",
        },
    ]


def _normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit consistency of RQ result tables against generated paper-report artifacts.")
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--hard30-report-json", type=Path, default=DEFAULT_HARD30_REPORT_JSON)
    parser.add_argument("--hard30-report-md", type=Path, default=DEFAULT_HARD30_REPORT_MD)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_rq_table_consistency_audit(args.paper, args.hard30_report_json, args.hard30_report_md)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_rq_table_consistency_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
