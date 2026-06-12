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
DEFAULT_PROCESS_STRESS_AUDIT = Path("docs/process_stress_plan_audit.json")
DEFAULT_PROCESS_STRESS_PILOT = Path("benchmark/process-stress/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_LIFT_AUDIT = Path("docs/verification_lift_plan_audit.json")
DEFAULT_VERIFICATION_LIFT_PILOT = Path("benchmark/verification-lift/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_ABLATION_AUDIT = Path("docs/verification_ablation_plan_audit.json")
DEFAULT_VERIFICATION_ABLATION_PILOT = Path("benchmark/verification-ablation/pilot/full-real/aggregate.json")
DEFAULT_RQ4_SIGNAL_AUDIT = Path("docs/rq4_signal_audit.json")
DEFAULT_TAXONOMY = Path("docs/failure_taxonomy.md")


def build_thesis_readiness(
    full30_aggregate_path: Path = DEFAULT_FULL30_AGGREGATE,
    full30_process_label_eval_path: Path = DEFAULT_FULL30_PROCESS_LABEL_EVAL,
    detector_fixture_eval_path: Path = DEFAULT_DETECTOR_FIXTURE_EVAL,
    hard10_aggregate_path: Path = DEFAULT_HARD10_AGGREGATE,
    hard30_report_path: Path = DEFAULT_HARD30_REPORT,
    hard30_readiness_path: Path = DEFAULT_HARD30_READINESS,
    process_stress_audit_path: Path = DEFAULT_PROCESS_STRESS_AUDIT,
    process_stress_pilot_path: Path = DEFAULT_PROCESS_STRESS_PILOT,
    verification_lift_audit_path: Path = DEFAULT_VERIFICATION_LIFT_AUDIT,
    verification_lift_pilot_path: Path = DEFAULT_VERIFICATION_LIFT_PILOT,
    verification_ablation_audit_path: Path = DEFAULT_VERIFICATION_ABLATION_AUDIT,
    verification_ablation_pilot_path: Path = DEFAULT_VERIFICATION_ABLATION_PILOT,
    rq4_signal_audit_path: Path = DEFAULT_RQ4_SIGNAL_AUDIT,
    taxonomy_path: Path = DEFAULT_TAXONOMY,
) -> dict[str, Any]:
    full30 = _read_json(full30_aggregate_path)
    full30_process_eval = _read_json(full30_process_label_eval_path) if full30_process_label_eval_path.exists() else {"labels": {}}
    detector_fixture_eval = _read_json(detector_fixture_eval_path) if detector_fixture_eval_path.exists() else {"labels": {}, "summary": {}}
    hard10 = _read_json(hard10_aggregate_path)
    hard30 = _read_json(hard30_report_path)
    readiness = _read_json(hard30_readiness_path)
    process_stress = _read_json(process_stress_audit_path) if process_stress_audit_path.exists() else {"ok": False, "task_count": 0}
    process_pilot = _read_json(process_stress_pilot_path) if process_stress_pilot_path.exists() else None
    verification_lift = _read_json(verification_lift_audit_path) if verification_lift_audit_path.exists() else {"ok": False, "task_count": 0}
    verification_lift_pilot = _read_json(verification_lift_pilot_path) if verification_lift_pilot_path.exists() else None
    verification_ablation = _read_json(verification_ablation_audit_path) if verification_ablation_audit_path.exists() else {"ok": False, "task_count": 0}
    verification_ablation_pilot = _read_json(verification_ablation_pilot_path) if verification_ablation_pilot_path.exists() else None
    rq4_signal_audit = _read_json(rq4_signal_audit_path) if rq4_signal_audit_path.exists() else {"summary": {"ready": False}}
    taxonomy_text = taxonomy_path.read_text(encoding="utf-8")

    full30_summary = full30["summary"]
    hard10_summary = hard10["summary"]
    hard30_aggregate = hard30["aggregate"]
    hard30_summary = hard30_aggregate["summary"]
    hard30_deltas = hard30_aggregate["deltas"]
    hard30_eval = hard30["detector_evaluation"]["labels"]
    hard30_paired = hard30["paired_task_summary"]
    signal_rows = {row["signal"]: row for row in hard30["signal_by_outcome"]}
    rq4_ready = bool(rq4_signal_audit.get("summary", {}).get("ready"))

    taxonomy_tags = [
        "verification_gap",
        "unrecovered_tool_error",
        "repetitive_exploration",
        "context_drift",
        "premature_completion",
        "sandbox_permission_deadlock",
    ]
    taxonomy_present = all(tag in taxonomy_text for tag in taxonomy_tags)

    hard30_tasks = int(hard30_summary["baseline"]["n"])
    hard30_runs = len(hard30_aggregate["runs"])
    hard30_ready = bool(readiness.get("ready"))
    hard30_success_delta = float(hard30_deltas.get("success_rate", 0) or 0)
    hard10_success_delta = float(hard10["deltas"].get("success_rate", 0) or 0)
    hard30_verification_delta = float(hard30_deltas.get("verification_rate", 0) or 0)
    hard30_repeated_delta = float(hard30_deltas.get("avg_repeated_tool_calls", 0) or 0)
    hard30_token_delta = float(hard30_deltas.get("avg_token_usage", 0) or 0)
    process_pilot_summary = _process_pilot_summary(process_pilot)
    verification_lift_summary = _process_pilot_summary(verification_lift_pilot)
    verification_ablation_summary = _process_pilot_summary(verification_ablation_pilot)
    process_verification_evidence = ""
    verification_lift_evidence = ""
    process_waste_evidence = ""
    verification_lift_waste_evidence = ""
    if process_pilot_summary.get("exists"):
        process_verification_evidence = (
            f", process-stress={process_pilot_summary['baseline_verification_rate']:.2f}->"
            f"{process_pilot_summary['intervention_verification_rate']:.2f}"
        )
        process_waste_evidence = (
            f"; process-stress success delta={process_pilot_summary['intervention_success_rate'] - process_pilot_summary['baseline_success_rate']:+.2f}, "
            f"repeated calls={process_pilot_summary['baseline_repeated_calls']:.2f}->{process_pilot_summary['intervention_repeated_calls']:.2f}, "
            f"token usage={process_pilot_summary['baseline_token_usage'] / 1000:.1f}k->{process_pilot_summary['intervention_token_usage'] / 1000:.1f}k"
        )
    if verification_lift_summary.get("exists"):
        verification_lift_evidence = (
            f", verification-lift={verification_lift_summary['baseline_verification_rate']:.2f}->"
            f"{verification_lift_summary['intervention_verification_rate']:.2f}"
        )
        verification_lift_waste_evidence = (
            f"; verification-lift success delta={verification_lift_summary['intervention_success_rate'] - verification_lift_summary['baseline_success_rate']:+.2f}, "
            f"repeated calls={verification_lift_summary['baseline_repeated_calls']:.2f}->{verification_lift_summary['intervention_repeated_calls']:.2f}, "
            f"token usage={verification_lift_summary['baseline_token_usage'] / 1000:.1f}k->{verification_lift_summary['intervention_token_usage'] / 1000:.1f}k"
        )
    elif verification_lift.get("ok"):
        verification_lift_evidence = (
            f"; verification-lift scaffold is ready with {int(verification_lift.get('task_count', 0) or 0)} task(s), but no real pilot aggregate yet"
        )
    verification_lift_delta = (
        verification_lift_summary["intervention_verification_rate"] - verification_lift_summary["baseline_verification_rate"]
        if verification_lift_summary.get("exists")
        else 0
    )
    token_improved = int(hard30_paired["token_usage_delta"]["improved"])
    repeated_improved = int(hard30_paired["repeated_tool_call_delta"]["improved"])
    paired_n = int(hard30_paired["token_usage_delta"]["n"])
    hidden = hard30_eval.get("hidden_semantic_edge_case", {})
    repetitive = hard30_eval.get("repetitive_exploration", {})
    full30_sandbox = full30_process_eval.get("labels", {}).get("sandbox_permission_deadlock", {})
    full30_repetitive_process = full30_process_eval.get("labels", {}).get("repetitive_exploration", {})
    detector_fixture_summary = detector_fixture_eval.get("summary", {})
    detector_fixture_labels = detector_fixture_eval.get("labels", {})
    target_detector_labels = {
        "verification_gap",
        "unrecovered_tool_error",
        "repetitive_exploration",
        "context_drift",
        "premature_completion",
        "sandbox_permission_deadlock",
    }
    detector_fixture_covers_taxonomy = target_detector_labels.issubset(set(detector_fixture_labels))
    detector_fixture_micro_f1 = float(detector_fixture_summary.get("micro_f1", 0) or 0)

    requirements = [
        {
            "id": "taxonomy",
            "requirement": "Define observable multi-turn coding-agent failure modes.",
            "status": "satisfied" if taxonomy_present else "partial",
            "evidence": f"{taxonomy_path} contains {len(taxonomy_tags)} target process labels.",
            "gap": "None for paper scope." if taxonomy_present else "Add missing target labels to the taxonomy document.",
        },
        {
            "id": "benchmark",
            "requirement": "Provide a 30-50 task Codex JSONL benchmark with baseline and intervention traces.",
            "status": "satisfied" if hard30_ready and hard30_tasks == 30 and hard30_runs == 60 else "partial",
            "evidence": f"hard30 has {hard30_tasks} tasks and {hard30_runs} runs; readiness={hard30_ready}.",
            "gap": "None for the current 30-task paper artifact." if hard30_ready else "Finish hard30 collection/finalization.",
        },
        {
            "id": "codextrace",
            "requirement": "Implement an offline parser and diagnosis engine without training or GPU.",
            "status": "satisfied",
            "evidence": "Stored traces can be parsed, diagnosed, aggregated, and rendered from repository artifacts.",
            "gap": "None for artifact scope.",
        },
        {
            "id": "process_rule_detection",
            "requirement": "Show that trace-based rules detect observable failure processes.",
            "status": "satisfied" if detector_fixture_covers_taxonomy and detector_fixture_micro_f1 >= 1 else "partial",
            "evidence": (
                f"controlled detector fixtures cover {len(detector_fixture_labels)} labels with micro-F1={detector_fixture_micro_f1:.2f}; "
                "hard30 repetitive_exploration detector has "
                f"TP={repetitive.get('tp', 0)}, FP={repetitive.get('fp', 0)}, FN={repetitive.get('fn', 0)}; "
                f"full30 sandbox_permission_deadlock has TP={full30_sandbox.get('tp', 0)}, FP={full30_sandbox.get('fp', 0)}, FN={full30_sandbox.get('fn', 0)}; "
                f"full30 process-label repetitive_exploration has FP={full30_repetitive_process.get('fp', 0)}; "
                f"hidden_semantic_edge_case recall={hidden.get('recall', 0):.2f}."
            ),
            "gap": "Rule-level taxonomy coverage is satisfied; real-pilot natural positives still cover only part of the taxonomy and should be described as limited.",
        },
        {
            "id": "verification_lift",
            "requirement": "Show that harness intervention increases verification rate.",
            "status": "satisfied" if verification_lift_delta > 0 else "missing",
            "evidence": (
                "verification is saturated in stored pilots: "
                f"full30={full30_summary['baseline']['verification_rate']:.2f}->{full30_summary['intervention']['verification_rate']:.2f}, "
                f"hard10={hard10_summary['baseline']['verification_rate']:.2f}->{hard10_summary['intervention']['verification_rate']:.2f}, "
                f"hard30={hard30_summary['baseline']['verification_rate']:.2f}->{hard30_summary['intervention']['verification_rate']:.2f}"
                f"{process_verification_evidence}{verification_lift_evidence}."
            ),
            "gap": (
                "None for original thesis." if verification_lift_delta > 0
                else (
                    "The ordinary and weak-baseline pilots are negative results; the no-verify ablation shows the harness can lift verification "
                    f"from {verification_ablation_summary.get('baseline_verification_rate', 0):.2f} to {verification_ablation_summary.get('intervention_verification_rate', 0):.2f}, "
                    "but this is not an ordinary-baseline result."
                )
            ),
        },
        {
            "id": "success_or_waste",
            "requirement": "Show intervention improves success and/or reduces tool-call and token waste.",
            "status": "satisfied",
            "evidence": (
                f"hard10 success delta={hard10_success_delta:+.2f}; hard30 success delta={hard30_success_delta:+.2f}; "
                f"hard30 repeated calls delta={hard30_repeated_delta:+.2f}; token delta={hard30_token_delta:+.1f}; "
                f"paired improvements repeated={repeated_improved}/{paired_n}, token={token_improved}/{paired_n}"
                f"{process_waste_evidence}{verification_lift_waste_evidence}."
            ),
            "gap": "Repeat hard30 or add a process-stress tier if a stable success-rate lift is required.",
        },
        {
            "id": "rq4_explanation",
            "requirement": "Identify trace signals that explain whether a run fails.",
            "status": "satisfied" if rq4_ready else "partial",
            "evidence": (
                "hard30 hidden failures are not separated by process signals: "
                f"verification delta={signal_rows['verification_rate']['delta_success_minus_failure']:+.2f}, "
                f"unresolved-error delta={signal_rows['unresolved_error']['delta_success_minus_failure']:+.2f}; "
                "repetitive_exploration positives are explained by repeated calls, token usage, and failure score; "
                f"RQ4 signal audit ready={rq4_ready}."
            ),
            "gap": (
                "Boundary-style RQ4 is supported: process signals explain observable process failures, while hidden semantic correctness remains a limitation."
                if rq4_ready
                else "Frame RQ4 as explaining observable process failures and detector boundaries, or add semantic-oracle features for hidden correctness failures."
            ),
        },
    ]

    counts: dict[str, int] = {}
    for row in requirements:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    return {
        "summary": {
            "requirements": len(requirements),
            "status_counts": counts,
            "ready_for_original_thesis": counts.get("missing", 0) == 0 and counts.get("partial", 0) == 0,
            "ready_for_boundary_result_paper": hard30_ready and counts.get("satisfied", 0) >= 4,
        },
        "requirements": requirements,
        "next_experiment": {
            "name": "process-stress tier",
            "purpose": "Close unsupported original-thesis claims about verification lift and broader process-rule recall.",
            "current_scaffold": {
                "tasks": "benchmark/process-stress/tasks.jsonl",
                "audit": str(process_stress_audit_path),
                "ready": bool(process_stress.get("ok")),
                "task_count": int(process_stress.get("task_count", 0) or 0),
                "pilot": process_pilot_summary,
            },
            "minimum_design": [
                "10-15 tasks whose visible success checks are weak enough that baseline may skip or under-run verification.",
                "At least two tasks each targeting verification_gap, unrecovered_tool_error, premature_completion, context_drift, repetitive_exploration, and sandbox_permission_deadlock.",
                "Baseline/intervention Codex JSONL traces with manual process labels for every failure and high-waste success.",
                "Acceptance gate: process-label recall >= 0.70 on observable labels, plus verification-rate or verification-depth improvement under intervention.",
            ],
        },
        "verification_lift_experiment": {
            "name": "verification-lift tier",
            "purpose": "Directly test the missing verification-rate-lift claim under a prompt contrast where baseline verification is optional and intervention verification is evidence-gated.",
            "current_scaffold": {
                "tasks": "benchmark/verification-lift/tasks.jsonl",
                "prompt_dir": "benchmark/verification-lift/prompts",
                "audit": str(verification_lift_audit_path),
                "ready": bool(verification_lift.get("ok")),
                "task_count": int(verification_lift.get("task_count", 0) or 0),
                "pilot": verification_lift_summary,
            },
            "minimum_design": [
                "The first 8-task pilot is complete and is a negative result for verification-rate lift.",
                "If preserving the original verification-lift claim, design a stronger ablation where baseline verification is genuinely absent.",
                "Otherwise revise the thesis to claim robust waste reduction under already-saturated verification behavior.",
                "Report the existing verification-lift pilot as an auxiliary stress result, not a replacement for the ordinary hard30 baseline.",
            ],
        },
        "verification_ablation_experiment": {
            "name": "verification-ablation tier",
            "purpose": "Auxiliary mechanism check: explicit no-verify baseline versus evidence-gated intervention.",
            "current_scaffold": {
                "tasks": "benchmark/verification-ablation/tasks.jsonl",
                "prompt_dir": "benchmark/verification-ablation/prompts",
                "audit": str(verification_ablation_audit_path),
                "ready": bool(verification_ablation.get("ok")),
                "task_count": int(verification_ablation.get("task_count", 0) or 0),
                "pilot": verification_ablation_summary,
            },
            "minimum_design": [
                "Treat as an ablation only, not as the ordinary Codex baseline.",
                "Use to support harness control over verification behavior.",
                "Do not use it to mark the original verification-lift claim complete.",
            ],
        },
    }


def render_thesis_readiness_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    counts = summary["status_counts"]
    lines = [
        "# CodexTrace Thesis Readiness",
        "",
        "This audit maps the original thesis objective to the current repository evidence.",
        "",
        "## Summary",
        "",
        f"- Requirements audited: {summary['requirements']}",
        f"- Satisfied: {counts.get('satisfied', 0)}",
        f"- Partial: {counts.get('partial', 0)}",
        f"- Missing: {counts.get('missing', 0)}",
        f"- Ready for original thesis: {'yes' if summary['ready_for_original_thesis'] else 'no'}",
        f"- Ready for boundary-result paper: {'yes' if summary['ready_for_boundary_result_paper'] else 'no'}",
        "",
        "## Requirement Status",
        "",
        "| ID | Status | Requirement | Evidence | Gap / action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result["requirements"]:
        lines.append(f"| {row['id']} | {row['status']} | {row['requirement']} | {row['evidence']} | {row['gap']} |")

    experiment = result["next_experiment"]
    scaffold = experiment["current_scaffold"]
    pilot = scaffold.get("pilot") or {}
    lines.extend([
        "",
        "## Next Experiment",
        "",
        f"Name: `{experiment['name']}`",
        "",
        experiment["purpose"],
        "",
        f"Current scaffold: {scaffold['task_count']} materialized tasks in `{scaffold['tasks']}`; audit ready={'yes' if scaffold['ready'] else 'no'}.",
        "",
    ])
    if pilot.get("exists"):
        lines.extend([
            (
                "Current process-stress pilot: "
                f"{pilot['tasks']} task(s), {pilot['runs']} run(s), "
                f"success {pilot['baseline_success_rate']:.2f}->{pilot['intervention_success_rate']:.2f}, "
                f"verification {pilot['baseline_verification_rate']:.2f}->{pilot['intervention_verification_rate']:.2f}, "
                f"repeated calls {pilot['baseline_repeated_calls']:.2f}->{pilot['intervention_repeated_calls']:.2f}, "
                f"token usage {pilot['baseline_token_usage'] / 1000:.1f}k->{pilot['intervention_token_usage'] / 1000:.1f}k."
            ),
            "",
        ])
    for item in experiment["minimum_design"]:
        lines.append(f"- {item}")
    verification_experiment = result["verification_lift_experiment"]
    verification_scaffold = verification_experiment["current_scaffold"]
    verification_pilot = verification_scaffold.get("pilot") or {}
    lines.extend([
        "",
        "## Verification-Lift Experiment",
        "",
        f"Name: `{verification_experiment['name']}`",
        "",
        verification_experiment["purpose"],
        "",
        (
            f"Current scaffold: {verification_scaffold['task_count']} task(s) in "
            f"`{verification_scaffold['tasks']}` with prompts in `{verification_scaffold['prompt_dir']}`; "
            f"audit ready={'yes' if verification_scaffold['ready'] else 'no'}."
        ),
        "",
    ])
    if verification_pilot.get("exists"):
        lines.extend([
            (
                "Current verification-lift pilot: "
                f"{verification_pilot['tasks']} task(s), {verification_pilot['runs']} run(s), "
                f"verification {verification_pilot['baseline_verification_rate']:.2f}->{verification_pilot['intervention_verification_rate']:.2f}, "
                f"success {verification_pilot['baseline_success_rate']:.2f}->{verification_pilot['intervention_success_rate']:.2f}."
            ),
            "",
        ])
    for item in verification_experiment["minimum_design"]:
        lines.append(f"- {item}")
    ablation_experiment = result["verification_ablation_experiment"]
    ablation_scaffold = ablation_experiment["current_scaffold"]
    ablation_pilot = ablation_scaffold.get("pilot") or {}
    lines.extend([
        "",
        "## Verification Ablation Experiment",
        "",
        f"Name: `{ablation_experiment['name']}`",
        "",
        ablation_experiment["purpose"],
        "",
        (
            f"Current scaffold: {ablation_scaffold['task_count']} task(s) in "
            f"`{ablation_scaffold['tasks']}` with prompts in `{ablation_scaffold['prompt_dir']}`; "
            f"audit ready={'yes' if ablation_scaffold['ready'] else 'no'}."
        ),
        "",
    ])
    if ablation_pilot.get("exists"):
        lines.extend([
            (
                "Current verification-ablation pilot: "
                f"{ablation_pilot['tasks']} task(s), {ablation_pilot['runs']} run(s), "
                f"verification {ablation_pilot['baseline_verification_rate']:.2f}->{ablation_pilot['intervention_verification_rate']:.2f}, "
                f"success {ablation_pilot['baseline_success_rate']:.2f}->{ablation_pilot['intervention_success_rate']:.2f}, "
                f"failure score {ablation_pilot['baseline_failure_score']:.2f}->{ablation_pilot['intervention_failure_score']:.2f}."
            ),
            "",
        ])
    for item in ablation_experiment["minimum_design"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def write_thesis_readiness_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_thesis_readiness_markdown(result), encoding="utf-8")


def _process_pilot_summary(aggregate: dict[str, Any] | None) -> dict[str, Any]:
    if not aggregate:
        return {"exists": False}
    baseline = aggregate["summary"].get("baseline", {})
    intervention = aggregate["summary"].get("intervention", {})
    return {
        "exists": True,
        "tasks": int(baseline.get("n", 0) or 0),
        "runs": len(aggregate.get("runs", [])),
        "baseline_success_rate": float(baseline.get("success_rate", 0) or 0),
        "intervention_success_rate": float(intervention.get("success_rate", 0) or 0),
        "baseline_verification_rate": float(baseline.get("verification_rate", 0) or 0),
        "intervention_verification_rate": float(intervention.get("verification_rate", 0) or 0),
        "baseline_repeated_calls": float(baseline.get("avg_repeated_tool_calls", 0) or 0),
        "intervention_repeated_calls": float(intervention.get("avg_repeated_tool_calls", 0) or 0),
        "baseline_token_usage": float(baseline.get("avg_token_usage", 0) or 0),
        "intervention_token_usage": float(intervention.get("avg_token_usage", 0) or 0),
        "baseline_failure_score": float(baseline.get("avg_failure_score", 0) or 0),
        "intervention_failure_score": float(intervention.get("avg_failure_score", 0) or 0),
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit original CodexTrace thesis readiness against stored artifacts.")
    parser.add_argument("--full30-aggregate", type=Path, default=DEFAULT_FULL30_AGGREGATE)
    parser.add_argument("--full30-process-label-eval", type=Path, default=DEFAULT_FULL30_PROCESS_LABEL_EVAL)
    parser.add_argument("--detector-fixture-eval", type=Path, default=DEFAULT_DETECTOR_FIXTURE_EVAL)
    parser.add_argument("--hard10-aggregate", type=Path, default=DEFAULT_HARD10_AGGREGATE)
    parser.add_argument("--hard30-report", type=Path, default=DEFAULT_HARD30_REPORT)
    parser.add_argument("--hard30-readiness", type=Path, default=DEFAULT_HARD30_READINESS)
    parser.add_argument("--process-stress-audit", type=Path, default=DEFAULT_PROCESS_STRESS_AUDIT)
    parser.add_argument("--process-stress-pilot", type=Path, default=DEFAULT_PROCESS_STRESS_PILOT)
    parser.add_argument("--verification-lift-audit", type=Path, default=DEFAULT_VERIFICATION_LIFT_AUDIT)
    parser.add_argument("--verification-lift-pilot", type=Path, default=DEFAULT_VERIFICATION_LIFT_PILOT)
    parser.add_argument("--verification-ablation-audit", type=Path, default=DEFAULT_VERIFICATION_ABLATION_AUDIT)
    parser.add_argument("--verification-ablation-pilot", type=Path, default=DEFAULT_VERIFICATION_ABLATION_PILOT)
    parser.add_argument("--rq4-signal-audit", type=Path, default=DEFAULT_RQ4_SIGNAL_AUDIT)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_thesis_readiness(
        args.full30_aggregate,
        args.full30_process_label_eval,
        args.detector_fixture_eval,
        args.hard10_aggregate,
        args.hard30_report,
        args.hard30_readiness,
        args.process_stress_audit,
        args.process_stress_pilot,
        args.verification_lift_audit,
        args.verification_lift_pilot,
        args.verification_ablation_audit,
        args.verification_ablation_pilot,
        args.rq4_signal_audit,
        args.taxonomy,
    )
    if args.json_output or args.markdown_output:
        write_thesis_readiness_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_thesis_readiness_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
