from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FULL30_AGGREGATE = Path("benchmark/pilot/full30-real/aggregate.json")
DEFAULT_HARD10_AGGREGATE = Path("benchmark/hard/pilot/hard10-real/aggregate.json")
DEFAULT_HARD30_REPORT = Path("benchmark/hard/pilot/hard30-real/paper-report-labeled.json")
DEFAULT_HARD30_READINESS = Path("benchmark/hard/pilot/hard30-real/readiness.json")


def build_claim_audit(
    full30_aggregate_path: Path = DEFAULT_FULL30_AGGREGATE,
    hard10_aggregate_path: Path = DEFAULT_HARD10_AGGREGATE,
    hard30_report_path: Path = DEFAULT_HARD30_REPORT,
    hard30_readiness_path: Path = DEFAULT_HARD30_READINESS,
) -> dict[str, Any]:
    full30 = _read_json(full30_aggregate_path)
    hard10 = _read_json(hard10_aggregate_path)
    hard30 = _read_json(hard30_report_path)
    readiness = _read_json(hard30_readiness_path)

    hard30_aggregate = hard30["aggregate"]
    hard30_summary = hard30_aggregate["summary"]
    hard30_deltas = hard30_aggregate["deltas"]
    paired = hard30["paired_task_summary"]
    label_eval = hard30["detector_evaluation"]
    hidden = label_eval["labels"].get("hidden_semantic_edge_case", {})
    signal_rows = {row["signal"]: row for row in hard30["signal_by_outcome"]}

    full30_task_count = int(full30["summary"]["baseline"]["n"])
    hard30_task_count = int(hard30_summary["baseline"]["n"])
    hard30_run_count = len(hard30_aggregate["runs"])
    hard30_ready = bool(readiness.get("ready"))
    hard30_failures = int(hard30.get("outcome_counts", {}).get("failure", 0))
    hard30_success_delta = float(hard30_deltas.get("success_rate", 0) or 0)
    hard10_success_delta = float(hard10["deltas"].get("success_rate", 0) or 0)
    verification_delta = float(hard30_deltas.get("verification_rate", 0) or 0)
    repeated_delta = float(hard30_deltas.get("avg_repeated_tool_calls", 0) or 0)
    token_delta = float(hard30_deltas.get("avg_token_usage", 0) or 0)
    token_improved = int(paired["token_usage_delta"]["improved"])
    repeated_improved = int(paired["repeated_tool_call_delta"]["improved"])
    paired_n = int(paired["token_usage_delta"]["n"])
    hidden_fn = int(hidden.get("fn", 0) or 0)
    hidden_recall = float(hidden.get("recall", 0) or 0)
    verification_signal_delta = float(signal_rows["verification_rate"]["delta_success_minus_failure"])
    unresolved_signal_delta = float(signal_rows["unresolved_error"]["delta_success_minus_failure"])

    claims = [
        {
            "claim": "CodexTrace is a GPU-free offline parser and diagnosis engine for Codex JSONL traces.",
            "status": "supported",
            "evidence": "Parser, diagnosis CLI, reports, demo traces, and CI-tested package exist; stored pilots can be analyzed without Codex or GPU.",
            "action": "Keep as a headline artifact claim.",
        },
        {
            "claim": "The benchmark has 30-50 coding tasks with baseline and intervention traces.",
            "status": "supported" if hard30_ready and hard30_task_count == 30 and hard30_run_count == 60 else "partial",
            "evidence": f"full30 has {full30_task_count} seed tasks; hard30 has {hard30_task_count} selected hard tasks and {hard30_run_count} real runs; readiness={hard30_ready}.",
            "action": "Describe as a 30-task paper-facing hard artifact plus a 30-task seed pilot, not as a broad benchmark.",
        },
        {
            "claim": "Harness intervention increases success rate.",
            "status": "partial",
            "evidence": f"hard10 success delta is {hard10_success_delta:+.2f}; hard30 success delta is {hard30_success_delta:+.2f}.",
            "action": "State that success improves in the early hard10 pilot but is flat on hard30.",
        },
        {
            "claim": "Harness intervention increases verification rate.",
            "status": "unsupported",
            "evidence": f"hard30 verification delta is {verification_delta:+.2f}; both baseline and intervention verification rates are already {hard30_summary['baseline']['verification_rate']:.2f}.",
            "action": "Do not claim verification-rate lift for current stored pilots; frame verification as saturated.",
        },
        {
            "claim": "Harness intervention reduces repeated tool-call and token waste.",
            "status": "supported" if repeated_delta < 0 and token_delta < 0 else "partial",
            "evidence": f"hard30 repeated tool calls change {repeated_delta:+.2f}; token usage changes {token_delta:+.1f}; paired improvements are repeated={repeated_improved}/{paired_n}, token={token_improved}/{paired_n}.",
            "action": "Use as the strongest current RQ3 result.",
        },
        {
            "claim": "Trace-based process rules detect most failure processes.",
            "status": "unsupported",
            "evidence": f"hard30 has {hard30_failures} failures, all labeled hidden semantic edge cases; trace-only recall for that label is {hidden_recall:.2f} with FN={hidden_fn}.",
            "action": "Reframe as a boundary result until process-failure-positive tasks or richer labels are collected.",
        },
        {
            "claim": "Trace signals explain whether hidden semantic failures will fail.",
            "status": "unsupported",
            "evidence": f"hard30 verification-rate signal delta is {verification_signal_delta:+.2f}; unresolved-error delta is {unresolved_signal_delta:+.2f}.",
            "action": "Say process signals explain the detector boundary, not hidden correctness.",
        },
        {
            "claim": "Strong task-level oracles remain necessary.",
            "status": "supported",
            "evidence": f"hard30 visible traces often verify cleanly, but hidden graders expose {hard30_failures} failures and {hidden_fn} trace-only false negatives.",
            "action": "Keep as a limitation and contribution.",
        },
    ]
    counts = {}
    for claim in claims:
        counts[claim["status"]] = counts.get(claim["status"], 0) + 1
    return {
        "summary": {
            "claims": len(claims),
            "status_counts": counts,
            "hard30_tasks": hard30_task_count,
            "hard30_runs": hard30_run_count,
            "hard30_failures": hard30_failures,
            "hard30_ready": hard30_ready,
        },
        "claims": claims,
    }


def render_claim_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    counts = summary["status_counts"]
    lines = [
        "# CodexTrace Paper Claim Audit",
        "",
        "This generated audit maps the original thesis-style claims to the evidence currently stored in the repository.",
        "",
        "## Summary",
        "",
        f"- Claims audited: {summary['claims']}",
        f"- Supported: {counts.get('supported', 0)}",
        f"- Partial: {counts.get('partial', 0)}",
        f"- Unsupported: {counts.get('unsupported', 0)}",
        f"- Hard30 artifact: {summary['hard30_tasks']} tasks, {summary['hard30_runs']} runs, {summary['hard30_failures']} failures, readiness={'yes' if summary['hard30_ready'] else 'no'}",
        "",
        "## Claim Status",
        "",
        "| Claim | Status | Evidence | Writing action |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["claims"]:
        lines.append(f"| {row['claim']} | {row['status']} | {row['evidence']} | {row['action']} |")
    lines.extend([
        "",
        "## Paper Writing Rule",
        "",
        "Use `supported` claims as paper/CV headline claims. Use `partial` claims only with pilot qualifiers. Do not state `unsupported` claims as findings; turn them into limitations or next experiments.",
    ])
    return "\n".join(lines) + "\n"


def write_claim_audit_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_claim_audit_markdown(result), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper claims against stored CodexTrace artifacts.")
    parser.add_argument("--full30-aggregate", type=Path, default=DEFAULT_FULL30_AGGREGATE)
    parser.add_argument("--hard10-aggregate", type=Path, default=DEFAULT_HARD10_AGGREGATE)
    parser.add_argument("--hard30-report", type=Path, default=DEFAULT_HARD30_REPORT)
    parser.add_argument("--hard30-readiness", type=Path, default=DEFAULT_HARD30_READINESS)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_claim_audit(
        args.full30_aggregate,
        args.hard10_aggregate,
        args.hard30_report,
        args.hard30_readiness,
    )
    if args.json_output or args.markdown_output:
        write_claim_audit_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_claim_audit_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
