from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FULL30_AGGREGATE = Path("benchmark/pilot/full30-real/aggregate.json")
DEFAULT_FULL30_PROCESS_LABEL_EVAL = Path("benchmark/pilot/full30-real/process-label-eval.json")
DEFAULT_DETECTOR_FIXTURE_EVAL = Path("benchmark/detector-fixtures/label-eval.json")
DEFAULT_HARD10_AGGREGATE = Path("benchmark/hard/pilot/hard10-real/aggregate.json")
DEFAULT_HARD30_REPORT = Path("benchmark/hard/pilot/hard30-real/paper-report-labeled.json")
DEFAULT_HARD30_READINESS = Path("benchmark/hard/pilot/hard30-real/readiness.json")
DEFAULT_PROCESS_STRESS_REPORT = Path("benchmark/process-stress/pilot/full-real/paper-report-labeled.json")
DEFAULT_VERIFICATION_LIFT_REPORT = Path("benchmark/verification-lift/pilot/full-real/paper-report-labeled.json")
DEFAULT_VERIFICATION_ABLATION_REPORT = Path("benchmark/verification-ablation/pilot/full-real/paper-report-labeled.json")
DEFAULT_RQ4_SIGNAL_AUDIT = Path("docs/rq4_signal_audit.json")


def build_claim_audit(
    full30_aggregate_path: Path = DEFAULT_FULL30_AGGREGATE,
    full30_process_label_eval_path: Path = DEFAULT_FULL30_PROCESS_LABEL_EVAL,
    detector_fixture_eval_path: Path = DEFAULT_DETECTOR_FIXTURE_EVAL,
    hard10_aggregate_path: Path = DEFAULT_HARD10_AGGREGATE,
    hard30_report_path: Path = DEFAULT_HARD30_REPORT,
    hard30_readiness_path: Path = DEFAULT_HARD30_READINESS,
    process_stress_report_path: Path = DEFAULT_PROCESS_STRESS_REPORT,
    verification_lift_report_path: Path = DEFAULT_VERIFICATION_LIFT_REPORT,
    verification_ablation_report_path: Path = DEFAULT_VERIFICATION_ABLATION_REPORT,
    rq4_signal_audit_path: Path = DEFAULT_RQ4_SIGNAL_AUDIT,
) -> dict[str, Any]:
    full30 = _read_json(full30_aggregate_path)
    full30_process_eval = _read_json(full30_process_label_eval_path) if full30_process_label_eval_path.exists() else {"labels": {}}
    detector_fixture_eval = _read_json(detector_fixture_eval_path) if detector_fixture_eval_path.exists() else {"labels": {}, "summary": {}}
    hard10 = _read_json(hard10_aggregate_path)
    hard30 = _read_json(hard30_report_path)
    readiness = _read_json(hard30_readiness_path)
    process_stress = _read_json(process_stress_report_path) if process_stress_report_path.exists() else None
    verification_lift = _read_json(verification_lift_report_path) if verification_lift_report_path.exists() else None
    verification_ablation = _read_json(verification_ablation_report_path) if verification_ablation_report_path.exists() else None
    rq4_signal_audit = _read_json(rq4_signal_audit_path) if rq4_signal_audit_path.exists() else {"summary": {"ready": False}}

    hard30_aggregate = hard30["aggregate"]
    hard30_summary = hard30_aggregate["summary"]
    hard30_deltas = hard30_aggregate["deltas"]
    paired = hard30["paired_task_summary"]
    label_eval = hard30["detector_evaluation"]
    hidden = label_eval["labels"].get("hidden_semantic_edge_case", {})
    repetitive = label_eval["labels"].get("repetitive_exploration", {})
    full30_sandbox = full30_process_eval.get("labels", {}).get("sandbox_permission_deadlock", {})
    full30_process_repetitive = full30_process_eval.get("labels", {}).get("repetitive_exploration", {})
    detector_fixture_summary = detector_fixture_eval.get("summary", {})
    detector_fixture_labels = detector_fixture_eval.get("labels", {})
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
    repetitive_tp = int(repetitive.get("tp", 0) or 0)
    repetitive_fn = int(repetitive.get("fn", 0) or 0)
    repetitive_f1 = float(repetitive.get("f1", 0) or 0)
    full30_sandbox_tp = int(full30_sandbox.get("tp", 0) or 0)
    full30_sandbox_fp = int(full30_sandbox.get("fp", 0) or 0)
    full30_sandbox_fn = int(full30_sandbox.get("fn", 0) or 0)
    full30_process_repetitive_fp = int(full30_process_repetitive.get("fp", 0) or 0)
    detector_fixture_label_count = int(detector_fixture_summary.get("labels", 0) or 0)
    detector_fixture_micro_f1 = float(detector_fixture_summary.get("micro_f1", 0) or 0)
    verification_signal_delta = float(signal_rows["verification_rate"]["delta_success_minus_failure"])
    unresolved_signal_delta = float(signal_rows["unresolved_error"]["delta_success_minus_failure"])
    rq4_ready = bool(rq4_signal_audit.get("summary", {}).get("ready"))
    process_stress_summary = process_stress["aggregate"]["summary"] if process_stress else {}
    process_stress_deltas = process_stress["aggregate"]["deltas"] if process_stress else {}
    process_stress_paired = process_stress["paired_task_summary"] if process_stress else {}
    process_stress_eval = process_stress["detector_evaluation"] if process_stress else {}
    process_stress_hidden = process_stress_eval.get("labels", {}).get("hidden_semantic_edge_case", {}) if process_stress else {}
    process_stress_tasks = int(process_stress_summary.get("baseline", {}).get("n", 0) or 0)
    process_stress_runs = len(process_stress["aggregate"]["runs"]) if process_stress else 0
    process_stress_failures = int(process_stress.get("outcome_counts", {}).get("failure", 0) or 0) if process_stress else 0
    process_stress_success_delta = float(process_stress_deltas.get("success_rate", 0) or 0)
    process_stress_verification_delta = float(process_stress_deltas.get("verification_rate", 0) or 0)
    process_stress_repeated_delta = float(process_stress_deltas.get("avg_repeated_tool_calls", 0) or 0)
    process_stress_token_delta = float(process_stress_deltas.get("avg_token_usage", 0) or 0)
    process_stress_repeated_improved = int(process_stress_paired.get("repeated_tool_call_delta", {}).get("improved", 0) or 0)
    process_stress_token_improved = int(process_stress_paired.get("token_usage_delta", {}).get("improved", 0) or 0)
    process_stress_paired_n = int(process_stress_paired.get("token_usage_delta", {}).get("n", 0) or 0)
    process_stress_hidden_fn = int(process_stress_hidden.get("fn", 0) or 0)
    verification_lift_summary = verification_lift["aggregate"]["summary"] if verification_lift else {}
    verification_lift_deltas = verification_lift["aggregate"]["deltas"] if verification_lift else {}
    verification_lift_eval = verification_lift["detector_evaluation"] if verification_lift else {}
    verification_lift_hidden = verification_lift_eval.get("labels", {}).get("hidden_semantic_edge_case", {}) if verification_lift else {}
    verification_lift_tasks = int(verification_lift_summary.get("baseline", {}).get("n", 0) or 0)
    verification_lift_runs = len(verification_lift["aggregate"]["runs"]) if verification_lift else 0
    verification_lift_failures = int(verification_lift.get("outcome_counts", {}).get("failure", 0) or 0) if verification_lift else 0
    verification_lift_verification_delta = float(verification_lift_deltas.get("verification_rate", 0) or 0)
    verification_lift_repeated_delta = float(verification_lift_deltas.get("avg_repeated_tool_calls", 0) or 0)
    verification_lift_token_delta = float(verification_lift_deltas.get("avg_token_usage", 0) or 0)
    verification_lift_hidden_fn = int(verification_lift_hidden.get("fn", 0) or 0)
    verification_ablation_summary = verification_ablation["aggregate"]["summary"] if verification_ablation else {}
    verification_ablation_deltas = verification_ablation["aggregate"]["deltas"] if verification_ablation else {}
    verification_ablation_tasks = int(verification_ablation_summary.get("baseline", {}).get("n", 0) or 0)
    verification_ablation_runs = len(verification_ablation["aggregate"]["runs"]) if verification_ablation else 0
    verification_ablation_failures = int(verification_ablation.get("outcome_counts", {}).get("failure", 0) or 0) if verification_ablation else 0
    verification_ablation_verification_delta = float(verification_ablation_deltas.get("verification_rate", 0) or 0)
    verification_ablation_failure_score_delta = float(verification_ablation_deltas.get("avg_failure_score", 0) or 0)

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
            "evidence": f"hard30 verification delta is {verification_delta:+.2f}; process-stress verification delta is {process_stress_verification_delta:+.2f}; verification-lift delta is {verification_lift_verification_delta:+.2f}; all stored pilots are saturated.",
            "action": "Do not claim verification-rate lift for current stored pilots; frame verification as saturated.",
        },
        {
            "claim": "Harness constraints can control verification behavior under a no-verify ablation.",
            "status": "supported" if verification_ablation_verification_delta > 0 else "partial",
            "evidence": f"verification-ablation verification delta is {verification_ablation_verification_delta:+.2f}; failure-score delta is {verification_ablation_failure_score_delta:+.2f}.",
            "action": "Use only as a mechanism ablation, not as ordinary-baseline evidence.",
        },
        {
            "claim": "Harness intervention reduces repeated tool-call and token waste.",
            "status": "supported" if repeated_delta < 0 and token_delta < 0 and process_stress_repeated_delta < 0 and process_stress_token_delta < 0 and verification_lift_repeated_delta < 0 and verification_lift_token_delta < 0 else "partial",
            "evidence": f"hard30 repeated tool calls change {repeated_delta:+.2f}, token usage {token_delta:+.1f}; process-stress repeated tool calls change {process_stress_repeated_delta:+.2f}, token usage {process_stress_token_delta:+.1f}; verification-lift repeated tool calls change {verification_lift_repeated_delta:+.2f}, token usage {verification_lift_token_delta:+.1f}.",
            "action": "Use as the strongest current RQ3 result.",
        },
        {
            "claim": "Trace-based process rules detect most failure processes.",
            "status": "partial",
            "evidence": f"controlled detector fixtures cover {detector_fixture_label_count} labels with micro-F1={detector_fixture_micro_f1:.2f}; hard30 includes {repetitive_tp} detected repetitive-exploration process positives (F1={repetitive_f1:.2f}); full30 includes sandbox/permission TP={full30_sandbox_tp}, FP={full30_sandbox_fp}, FN={full30_sandbox_fn}, with {full30_process_repetitive_fp} repetitive-exploration FP in the process-label slice. Hidden semantic recall is {hidden_recall:.2f} with FN={hidden_fn}; process-stress hidden semantic FN={process_stress_hidden_fn}; verification-lift hidden semantic FN={verification_lift_hidden_fn}.",
            "action": "Claim rule-level taxonomy coverage and observed process-positive detection; do not claim most real-world outcome failures are detected.",
        },
        {
            "claim": "Trace signals explain whether hidden semantic failures will fail.",
            "status": "unsupported",
            "evidence": f"hard30 verification-rate signal delta is {verification_signal_delta:+.2f}; unresolved-error delta is {unresolved_signal_delta:+.2f}.",
            "action": "Say process signals explain the detector boundary, not hidden correctness.",
        },
        {
            "claim": "Trace signals explain observable process failures and the hidden-semantic boundary.",
            "status": "supported" if rq4_ready else "partial",
            "evidence": f"RQ4 signal audit ready={rq4_ready}; hard30 hidden failures have verification delta {verification_signal_delta:+.2f} and unresolved-error delta {unresolved_signal_delta:+.2f}, while real process positives have large repeated-call, token, failure-score, command-failure, or recover-phase deltas.",
            "action": "Use as the paper's RQ4 framing.",
        },
        {
            "claim": "Strong task-level oracles remain necessary.",
            "status": "supported",
            "evidence": f"hard30 visible traces often verify cleanly, but hidden graders expose {hard30_failures} failures and {hidden_fn} trace-only false negatives; process-stress adds {process_stress_failures} failures and {process_stress_hidden_fn} false negatives; verification-lift adds {verification_lift_failures} failures and {verification_lift_hidden_fn} false negatives.",
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
            "hard30_repetitive_exploration_tp": repetitive_tp,
            "hard30_repetitive_exploration_fn": repetitive_fn,
            "full30_sandbox_permission_tp": full30_sandbox_tp,
            "full30_sandbox_permission_fp": full30_sandbox_fp,
            "full30_sandbox_permission_fn": full30_sandbox_fn,
            "detector_fixture_labels": detector_fixture_label_count,
            "detector_fixture_micro_f1": detector_fixture_micro_f1,
            "process_stress_tasks": process_stress_tasks,
            "process_stress_runs": process_stress_runs,
            "process_stress_failures": process_stress_failures,
            "process_stress_success_delta": process_stress_success_delta,
            "verification_lift_tasks": verification_lift_tasks,
            "verification_lift_runs": verification_lift_runs,
            "verification_lift_failures": verification_lift_failures,
            "verification_lift_verification_delta": verification_lift_verification_delta,
            "verification_ablation_tasks": verification_ablation_tasks,
            "verification_ablation_runs": verification_ablation_runs,
            "verification_ablation_failures": verification_ablation_failures,
            "verification_ablation_verification_delta": verification_ablation_verification_delta,
            "rq4_signal_audit_ready": rq4_ready,
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
        f"- Hard30 detected repetitive-exploration positives: TP={summary['hard30_repetitive_exploration_tp']}, FN={summary['hard30_repetitive_exploration_fn']}",
        f"- Full30 detected sandbox/permission positives: TP={summary['full30_sandbox_permission_tp']}, FP={summary['full30_sandbox_permission_fp']}, FN={summary['full30_sandbox_permission_fn']}",
        f"- Controlled detector fixture labels: {summary['detector_fixture_labels']}, micro-F1={summary['detector_fixture_micro_f1']:.2f}",
        f"- Process-stress artifact: {summary['process_stress_tasks']} tasks, {summary['process_stress_runs']} runs, {summary['process_stress_failures']} failures, success delta={summary['process_stress_success_delta']:+.2f}",
        f"- Verification-lift artifact: {summary['verification_lift_tasks']} tasks, {summary['verification_lift_runs']} runs, {summary['verification_lift_failures']} failures, verification delta={summary['verification_lift_verification_delta']:+.2f}",
        f"- Verification-ablation artifact: {summary['verification_ablation_tasks']} tasks, {summary['verification_ablation_runs']} runs, {summary['verification_ablation_failures']} failures, verification delta={summary['verification_ablation_verification_delta']:+.2f}",
        f"- RQ4 signal audit ready: {'yes' if summary['rq4_signal_audit_ready'] else 'no'}",
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
    parser.add_argument("--full30-process-label-eval", type=Path, default=DEFAULT_FULL30_PROCESS_LABEL_EVAL)
    parser.add_argument("--detector-fixture-eval", type=Path, default=DEFAULT_DETECTOR_FIXTURE_EVAL)
    parser.add_argument("--hard10-aggregate", type=Path, default=DEFAULT_HARD10_AGGREGATE)
    parser.add_argument("--hard30-report", type=Path, default=DEFAULT_HARD30_REPORT)
    parser.add_argument("--hard30-readiness", type=Path, default=DEFAULT_HARD30_READINESS)
    parser.add_argument("--process-stress-report", type=Path, default=DEFAULT_PROCESS_STRESS_REPORT)
    parser.add_argument("--verification-lift-report", type=Path, default=DEFAULT_VERIFICATION_LIFT_REPORT)
    parser.add_argument("--verification-ablation-report", type=Path, default=DEFAULT_VERIFICATION_ABLATION_REPORT)
    parser.add_argument("--rq4-signal-audit", type=Path, default=DEFAULT_RQ4_SIGNAL_AUDIT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_claim_audit(
        args.full30_aggregate,
        args.full30_process_label_eval,
        args.detector_fixture_eval,
        args.hard10_aggregate,
        args.hard30_report,
        args.hard30_readiness,
        args.process_stress_report,
        args.verification_lift_report,
        args.verification_ablation_report,
        args.rq4_signal_audit,
    )
    if args.json_output or args.markdown_output:
        write_claim_audit_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_claim_audit_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
