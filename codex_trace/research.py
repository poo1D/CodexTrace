from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from .diagnose import diagnose
from .parser import is_verification_command, parse_jsonl
from .schema import Diagnosis, Trace


PROMPT_TYPES = ("baseline", "intervention")
TAXONOMY_ALIASES = {
    "command_failure_unhandled": "unrecovered_tool_error",
    "verification_gap": "verification_gap",
    "repeated_search_or_read": "repetitive_exploration",
    "sandbox_or_permission_block": "sandbox_permission_deadlock",
    "long_context_no_progress": "context_drift",
    "premature_completion": "premature_completion",
    "turn_failed": "turn_failed",
}
PAPER_SIGNAL_KEYS = (
    "verification_rate",
    "success_check_verification_rate",
    "unresolved_error",
    "repeated_tool_call_count",
    "retry_count",
    "command_failure_count",
    "token_usage",
    "failure_score",
    "turn_count",
    "time_to_first_edit",
    "time_to_first_test",
    "phase_inspect_events",
    "phase_edit_events",
    "phase_verify_events",
    "phase_recover_events",
)


@dataclass
class BenchmarkTask:
    task_id: str
    category: str
    instruction: str
    success_check: str
    public_success_check: str = ""
    repo_hint: str = ""
    fixture_path: str = ""
    grader_path: str = ""


@dataclass
class RunRecord:
    task_id: str
    prompt_type: str
    trace_path: Path
    outcome: str = "unknown"
    prompt_path: Path | None = None
    success_check: str = ""


def load_tasks(path: str | Path) -> list[BenchmarkTask]:
    task_path = Path(path)
    tasks = []
    for line in task_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        tasks.append(BenchmarkTask(
            task_id=str(item["task_id"]),
            category=str(item["category"]),
            instruction=str(item["instruction"]),
            success_check=str(item["success_check"]),
            public_success_check=str(item.get("public_success_check", item["success_check"])),
            repo_hint=str(item.get("repo_hint", "")),
            fixture_path=_resolve_optional_path(task_path.parent, item.get("fixture_path", "")),
            grader_path=_resolve_optional_path(task_path.parent, item.get("grader_path", "")),
        ))
    return tasks


def load_run_manifest(path: str | Path) -> list[RunRecord]:
    return [record for record, _ in _load_run_manifest_items(path)]


def _load_run_manifest_items(path: str | Path) -> list[tuple[RunRecord, str]]:
    manifest_path = Path(path)
    items = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        raw_trace_path = str(item["trace_path"])
        raw_prompt_path = str(item.get("prompt_path", ""))
        items.append((RunRecord(
            task_id=str(item["task_id"]),
            prompt_type=str(item["prompt_type"]),
            trace_path=(manifest_path.parent / raw_trace_path).resolve(),
            outcome=str(item.get("outcome", "unknown")),
            prompt_path=(manifest_path.parent / raw_prompt_path).resolve() if raw_prompt_path else None,
            success_check=str(item.get("success_check", "")),
        ), raw_trace_path))
    return items


def render_prompt(task: BenchmarkTask, prompt_type: str, prompt_dir: str | Path = "benchmark/prompts") -> str:
    if prompt_type not in PROMPT_TYPES:
        raise ValueError(f"prompt_type must be one of {PROMPT_TYPES}")
    template = Path(prompt_dir, f"{prompt_type}.txt").read_text(encoding="utf-8")
    return template.format(
        task_id=task.task_id,
        category=task.category,
        instruction=task.instruction,
        success_check=task.public_success_check or task.success_check,
        repo_hint=task.repo_hint,
    )


def run_benchmark(
    tasks_path: str | Path,
    output_dir: str | Path,
    prompt_types: list[str] | None = None,
    task_ids: list[str] | None = None,
    prompt_dir: str | Path = "benchmark/prompts",
    codex_bin: str = "codex",
    sandbox: str = "workspace-write",
    timeout_seconds: int = 300,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    tasks = load_tasks(tasks_path)
    selected_prompt_types = prompt_types or list(PROMPT_TYPES)
    selected_ids = set(task_ids or [])
    rows = []
    for task in tasks:
        if selected_ids and task.task_id not in selected_ids:
            continue
        for prompt_type in selected_prompt_types:
            rows.append(run_single_task(
                task=task,
                prompt_type=prompt_type,
                output_dir=output_dir,
                prompt_dir=prompt_dir,
                codex_bin=codex_bin,
                sandbox=sandbox,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            ))
    return rows


def run_single_task(
    task: BenchmarkTask,
    prompt_type: str,
    output_dir: str | Path,
    prompt_dir: str | Path = "benchmark/prompts",
    codex_bin: str = "codex",
    sandbox: str = "workspace-write",
    timeout_seconds: int = 300,
    dry_run: bool = False,
) -> dict[str, Any]:
    if prompt_type not in PROMPT_TYPES:
        raise ValueError(f"prompt_type must be one of {PROMPT_TYPES}")
    if not task.fixture_path:
        raise ValueError(f"{task.task_id} does not define fixture_path")

    output_root = Path(output_dir)
    run_dir = output_root / task.task_id / prompt_type
    repo_dir = run_dir / "repo"
    grader_dir = run_dir / "grader"
    trace_path = run_dir / "trace.jsonl"
    prompt_path = run_dir / "prompt.md"
    stderr_path = run_dir / "codex.stderr"
    check_path = run_dir / "success_check.txt"

    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(task.fixture_path, repo_dir)
    initialize_git_repo(repo_dir)

    prompt = render_prompt(task, prompt_type, prompt_dir)
    prompt_path.write_text(prompt, encoding="utf-8")

    if dry_run:
        if task.grader_path:
            shutil.copytree(task.grader_path, grader_dir)
        outcome = "not_run"
        codex_exit_code = None
        check_exit_code = None
    else:
        with trace_path.open("w", encoding="utf-8") as trace_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            codex_result = subprocess.run(
                [codex_bin, "exec", "--json", "--sandbox", sandbox, prompt],
                cwd=repo_dir,
                env=_clean_git_env(),
                text=True,
                stdout=trace_handle,
                stderr=stderr_handle,
                timeout=timeout_seconds,
                check=False,
            )
        codex_exit_code = codex_result.returncode
        if task.grader_path:
            shutil.copytree(task.grader_path, grader_dir)
        check_result = run_success_check(repo_dir, task.success_check, timeout_seconds, grader_dir if task.grader_path else None)
        check_exit_code = check_result.returncode
        check_path.write_text((check_result.stdout or "") + (check_result.stderr or ""), encoding="utf-8")
        outcome = "success" if check_exit_code == 0 else "failure"

    return {
        "task_id": task.task_id,
        "prompt_type": prompt_type,
        "trace_path": _relative_to(trace_path, output_root),
        "outcome": outcome,
        "workdir": _relative_to(repo_dir, output_root),
        "grader_path": _relative_to(grader_dir, output_root) if task.grader_path else "",
        "prompt_path": _relative_to(prompt_path, output_root),
        "codex_exit_code": codex_exit_code,
        "success_check": task.success_check,
        "success_check_exit_code": check_exit_code,
    }


def run_success_check(
    repo_dir: str | Path,
    success_check: str,
    timeout_seconds: int = 120,
    grader_dir: str | Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        success_check,
        cwd=repo_dir,
        shell=True,
        env=_clean_git_env({"CODEXTRACE_GRADER_DIR": str(Path(grader_dir).resolve())} if grader_dir else None),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_seconds,
        check=False,
    )


def initialize_git_repo(repo_dir: str | Path) -> None:
    repo = Path(repo_dir)
    env = _clean_git_env()
    subprocess.run(["git", "init", "-q"], cwd=repo, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "CodexTrace Benchmark"], cwd=repo, env=env, check=True)
    subprocess.run(["git", "config", "user.email", "benchmark@example.com"], cwd=repo, env=env, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, env=env, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "Initial fixture"], cwd=repo, env=env, check=True)


def write_run_manifest(rows: list[dict[str, Any]], path: str | Path) -> None:
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def aggregate_runs(manifest_path: str | Path) -> dict[str, Any]:
    records = load_run_manifest(manifest_path)
    run_rows = []
    for record in records:
        trace = parse_jsonl(record.trace_path)
        diagnosis = diagnose(trace)
        run_rows.append(_run_metrics(record, trace, diagnosis))

    grouped = {}
    for prompt_type in PROMPT_TYPES:
        rows = [row for row in run_rows if row["prompt_type"] == prompt_type]
        grouped[prompt_type] = _summarize_group(rows)

    return {
        "runs": run_rows,
        "summary": grouped,
        "deltas": _deltas(grouped.get("baseline", {}), grouped.get("intervention", {})),
    }


def write_aggregate_outputs(result: dict[str, Any], json_path: str | Path | None = None, markdown_path: str | Path | None = None) -> None:
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if markdown_path:
        path = Path(markdown_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_aggregate_markdown(result), encoding="utf-8")


def render_aggregate_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# CodexTrace Research Aggregate",
        "",
        "## Summary",
        "",
        "| Metric | Baseline | Intervention | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key in (
        "success_rate",
        "verification_rate",
        "success_check_verification_rate",
        "unresolved_error_rate",
        "avg_repeated_tool_calls",
        "avg_retry_count",
        "avg_command_failures",
        "avg_turn_count",
        "avg_time_to_first_edit",
        "avg_time_to_first_test",
        "avg_recover_events",
        "avg_verify_events",
        "avg_token_usage",
        "avg_failure_score",
    ):
        baseline = result["summary"].get("baseline", {}).get(key, 0)
        intervention = result["summary"].get("intervention", {}).get(key, 0)
        delta = result["deltas"].get(key, 0)
        lines.append(f"| {key} | {_fmt(baseline)} | {_fmt(intervention)} | {_fmt(delta)} |")

    lines.extend(["", "## Runs", "", "| Task | Prompt | Outcome | Failure score | Findings |", "| --- | --- | --- | ---: | --- |"])
    for row in result["runs"]:
        findings = ", ".join(row["finding_codes"]) or "-"
        lines.append(f"| {row['task_id']} | {row['prompt_type']} | {row['outcome']} | {row['failure_score']} | {findings} |")
    return "\n".join(lines) + "\n"


def write_runs_csv(result: dict[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_id",
        "prompt_type",
        "outcome",
        "success",
        "verification_rate",
        "success_check_verification_rate",
        "visible_success_check",
        "unresolved_error",
        "repeated_tool_call_count",
        "retry_count",
        "command_failure_count",
        "token_usage",
        "failure_score",
        "turn_count",
        "time_to_first_edit",
        "time_to_first_test",
        "phase_setup_events",
        "phase_inspect_events",
        "phase_edit_events",
        "phase_verify_events",
        "phase_recover_events",
        "phase_complete_events",
        "phase_other_events",
        "finding_codes",
        "taxonomy_tags",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in result["runs"]:
            serialized = dict(row)
            serialized["finding_codes"] = ";".join(row["finding_codes"])
            serialized["taxonomy_tags"] = ";".join(row["taxonomy_tags"])
            writer.writerow({key: serialized.get(key, "") for key in fieldnames})


def write_paired_task_deltas_csv(result: dict[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_id",
        "baseline_outcome",
        "intervention_outcome",
        "success_delta",
        "verification_delta",
        "success_check_verification_delta",
        "repeated_tool_call_delta",
        "token_usage_delta",
        "failure_score_delta",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in result.get("paired_task_deltas", []):
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_paired_task_summary_csv(result: dict[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["metric", "n", "improved", "regressed", "unchanged", "avg_delta"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for metric, row in sorted(result.get("paired_task_summary", {}).items()):
            writer.writerow({
                "metric": metric,
                "n": row.get("n", 0),
                "improved": row.get("improved", 0),
                "regressed": row.get("regressed", 0),
                "unchanged": row.get("unchanged", 0),
                "avg_delta": row.get("avg_delta", 0),
            })


def build_paper_report(manifest_path: str | Path, labels_path: str | Path | None = None) -> dict[str, Any]:
    aggregate = aggregate_runs(manifest_path)
    labels = load_manual_labels(labels_path) if labels_path else {}
    taxonomy = taxonomy_distribution(aggregate["runs"], labels)
    label_evaluation = evaluate_detector_labels(manifest_path, labels_path) if labels_path else None
    paired_deltas = paired_task_deltas(aggregate["runs"])
    return {
        "aggregate": aggregate,
        "taxonomy_distribution": taxonomy,
        "detector_evaluation": label_evaluation,
        "outcome_counts": outcome_counts(aggregate["runs"]),
        "paired_task_deltas": paired_deltas,
        "paired_task_summary": paired_task_summary(paired_deltas),
        "signal_by_outcome": signal_summary_by_outcome(aggregate["runs"]),
        "signal_by_label": signal_summary_by_label(aggregate["runs"], labels),
    }


def render_paper_report_markdown(result: dict[str, Any]) -> str:
    aggregate = result["aggregate"]
    lines = [
        "# CodexTrace Paper Tables",
        "",
        "## RQ1 Failure Taxonomy Distribution",
        "",
    ]
    if result["taxonomy_distribution"]:
        lines.extend(["| Failure tag | Count | Percentage | Example task |", "| --- | ---: | ---: | --- |"])
        for row in result["taxonomy_distribution"]:
            lines.append(f"| {row['failure_tag']} | {row['count']} | {_fmt(row['percentage'])} | {row['example_task']} |")
    else:
        lines.append("No failure tags were observed in these runs.")

    if result.get("detector_evaluation"):
        evaluation = result["detector_evaluation"]
        lines.extend(["", "## RQ2 Detector Agreement", ""])
        if evaluation["labels"]:
            lines.extend(["| Label | TP | FP | FN | Precision | Recall | F1 |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
            for label, scores in sorted(evaluation["labels"].items()):
                lines.append(
                    f"| {label} | {scores['tp']} | {scores['fp']} | {scores['fn']} | "
                    f"{_fmt(scores['precision'])} | {_fmt(scores['recall'])} | {_fmt(scores['f1'])} |"
                )
            summary = evaluation["summary"]
            lines.extend([
                "",
                f"Micro F1: {_fmt(summary['micro_f1'])}; Macro F1: {_fmt(summary['macro_f1'])}.",
            ])
        else:
            lines.append("No detector labels were present to score.")

    lines.extend([
        "",
        "## RQ3 Baseline vs Intervention",
        "",
        "| Metric | Baseline | Intervention | Delta |",
        "| --- | ---: | ---: | ---: |",
    ])
    for key in (
        "success_rate",
        "verification_rate",
        "success_check_verification_rate",
        "unresolved_error_rate",
        "avg_repeated_tool_calls",
        "avg_retry_count",
        "avg_command_failures",
        "avg_turn_count",
        "avg_time_to_first_edit",
        "avg_time_to_first_test",
        "avg_token_usage",
        "avg_failure_score",
        "avg_recover_events",
        "avg_verify_events",
    ):
        baseline = aggregate["summary"].get("baseline", {}).get(key, 0)
        intervention = aggregate["summary"].get("intervention", {}).get(key, 0)
        delta = aggregate["deltas"].get(key, 0)
        lines.append(f"| {key} | {_fmt(baseline)} | {_fmt(intervention)} | {_fmt(delta)} |")

    if result.get("paired_task_deltas"):
        paired_summary = result.get("paired_task_summary", {})
        lines.extend([
            "",
            "### Paired Task Summary",
            "",
            "| Metric | Improved | Regressed | Unchanged | Average delta |",
            "| --- | ---: | ---: | ---: | ---: |",
        ])
        for key, label in (
            ("success_delta", "success"),
            ("verification_delta", "verification"),
            ("success_check_verification_delta", "success check verification"),
            ("repeated_tool_call_delta", "repeated tool calls"),
            ("token_usage_delta", "token usage"),
            ("failure_score_delta", "failure score"),
        ):
            row = paired_summary.get(key, {})
            lines.append(
                f"| {label} | {row.get('improved', 0)} | {row.get('regressed', 0)} | "
                f"{row.get('unchanged', 0)} | {_fmt(row.get('avg_delta', 0))} |"
            )
        lines.extend([
            "",
            "### Paired Task Deltas",
            "",
            "| Task | Success delta | Verification delta | Success-check verification delta | Repeated calls delta | Token delta | Failure score delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for row in result["paired_task_deltas"]:
            lines.append(
                f"| {row['task_id']} | {_fmt(row['success_delta'])} | {_fmt(row['verification_delta'])} | "
                f"{_fmt(row['success_check_verification_delta'])} | "
                f"{_fmt(row['repeated_tool_call_delta'])} | {_fmt(row['token_usage_delta'])} | {_fmt(row['failure_score_delta'])} |"
            )

    counts = result.get("outcome_counts", {})
    lines.extend([
        "",
        "## RQ4 Trace Signals By Outcome",
        "",
        f"Outcome counts: failure={counts.get('failure', 0)}, success={counts.get('success', 0)}, unknown={counts.get('unknown', 0)}.",
        "",
        "| Signal | Failure mean | Success mean | Delta success-failure |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in result["signal_by_outcome"]:
        lines.append(
            f"| {row['signal']} | {_fmt(row['failure_mean'])} | {_fmt(row['success_mean'])} | {_fmt(row['delta_success_minus_failure'])} |"
        )

    if result.get("signal_by_label"):
        lines.extend([
            "",
            "## RQ4 Trace Signals By Manual Label",
            "",
            "| Label | Runs | Signal | Mean | Overall mean | Delta label-overall |",
            "| --- | ---: | --- | ---: | ---: | ---: |",
        ])
        for row in result["signal_by_label"]:
            lines.append(
                f"| {row['failure_tag']} | {row['n']} | {row['signal']} | "
                f"{_fmt(row['label_mean'])} | {_fmt(row['overall_mean'])} | {_fmt(row['delta_label_minus_overall'])} |"
            )

    expected_tags = {}
    if result.get("detector_evaluation"):
        expected_tags = {
            (row["task_id"], row["prompt_type"]): row["expected"]
            for row in result["detector_evaluation"]["runs"]
        }

    lines.extend(["", "## Per-Run Appendix", "", "| Task | Prompt | Outcome | Failure score | Tags |", "| --- | --- | --- | ---: | --- |"])
    for row in aggregate["runs"]:
        tags_for_row = expected_tags.get((row["task_id"], row["prompt_type"]), row["taxonomy_tags"])
        tags = ", ".join(tags_for_row) or "-"
        lines.append(f"| {row['task_id']} | {row['prompt_type']} | {row['outcome']} | {row['failure_score']} | {tags} |")
    return "\n".join(lines) + "\n"


def write_paper_report_outputs(result: dict[str, Any], json_path: str | Path | None = None, markdown_path: str | Path | None = None) -> None:
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if markdown_path:
        path = Path(markdown_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_paper_report_markdown(result), encoding="utf-8")


def build_results_summary(
    full_manifest_path: str | Path,
    full_process_labels_path: str | Path | None,
    detector_fixture_manifest_path: str | Path | None,
    detector_fixture_labels_path: str | Path | None,
    hard_manifest_path: str | Path,
    hard_labels_path: str | Path,
    hard30_manifest_path: str | Path | None = None,
    hard30_labels_path: str | Path | None = None,
    process_stress_manifest_path: str | Path | None = None,
    process_stress_labels_path: str | Path | None = None,
    verification_lift_manifest_path: str | Path | None = None,
    verification_lift_labels_path: str | Path | None = None,
    verification_lift_v2_manifest_path: str | Path | None = None,
    verification_ablation_manifest_path: str | Path | None = None,
    verification_ablation_labels_path: str | Path | None = None,
) -> dict[str, Any]:
    full = _load_finalized_aggregate(full_manifest_path) or aggregate_runs(full_manifest_path)
    full_process_eval = evaluate_detector_labels(full_manifest_path, full_process_labels_path) if full_process_labels_path else None
    detector_fixture_eval = (
        evaluate_detector_labels(detector_fixture_manifest_path, detector_fixture_labels_path)
        if detector_fixture_manifest_path and detector_fixture_labels_path
        else None
    )
    hard_paper_report = _load_finalized_paper_report(hard_manifest_path, hard_labels_path) or build_paper_report(
        hard_manifest_path,
        labels_path=hard_labels_path,
    )
    hard = hard_paper_report["aggregate"]
    hard_label_eval = hard_paper_report["detector_evaluation"]
    result: dict[str, Any] = {
        "full30": full,
        "full30_process_label_evaluation": full_process_eval,
        "detector_fixture_label_evaluation": detector_fixture_eval,
        "hard10": hard,
        "hard10_label_evaluation": hard_label_eval,
        "hard10_taxonomy_distribution": hard_paper_report["taxonomy_distribution"],
        "hard10_outcome_counts": hard_paper_report["outcome_counts"],
        "hard10_signal_by_outcome": hard_paper_report["signal_by_outcome"],
    }
    if hard30_manifest_path and hard30_labels_path:
        hard30_paper_report = _load_finalized_paper_report(hard30_manifest_path, hard30_labels_path) or build_paper_report(
            hard30_manifest_path,
            labels_path=hard30_labels_path,
        )
        hard30 = hard30_paper_report["aggregate"]
        hard30_label_eval = hard30_paper_report["detector_evaluation"]
        result.update({
            "hard30": hard30,
            "hard30_label_evaluation": hard30_label_eval,
            "hard30_taxonomy_distribution": hard30_paper_report["taxonomy_distribution"],
            "hard30_outcome_counts": hard30_paper_report["outcome_counts"],
            "hard30_signal_by_outcome": hard30_paper_report["signal_by_outcome"],
            "hard30_paired_task_summary": hard30_paper_report["paired_task_summary"],
        })
    if process_stress_manifest_path and process_stress_labels_path:
        process_stress_report = (
            _load_finalized_paper_report(process_stress_manifest_path, process_stress_labels_path)
            or build_paper_report(process_stress_manifest_path, labels_path=process_stress_labels_path)
        )
        result.update({
            "process_stress": process_stress_report["aggregate"],
            "process_stress_label_evaluation": process_stress_report["detector_evaluation"],
            "process_stress_taxonomy_distribution": process_stress_report["taxonomy_distribution"],
            "process_stress_outcome_counts": process_stress_report["outcome_counts"],
            "process_stress_signal_by_outcome": process_stress_report["signal_by_outcome"],
            "process_stress_paired_task_summary": process_stress_report["paired_task_summary"],
        })
    if verification_lift_manifest_path and verification_lift_labels_path:
        verification_lift_report = (
            _load_finalized_paper_report(verification_lift_manifest_path, verification_lift_labels_path)
            or build_paper_report(verification_lift_manifest_path, labels_path=verification_lift_labels_path)
        )
        result.update({
            "verification_lift": verification_lift_report["aggregate"],
            "verification_lift_label_evaluation": verification_lift_report["detector_evaluation"],
            "verification_lift_taxonomy_distribution": verification_lift_report["taxonomy_distribution"],
            "verification_lift_outcome_counts": verification_lift_report["outcome_counts"],
            "verification_lift_signal_by_outcome": verification_lift_report["signal_by_outcome"],
            "verification_lift_paired_task_summary": verification_lift_report["paired_task_summary"],
        })
    if verification_lift_v2_manifest_path:
        verification_lift_v2_report = (
            _load_finalized_paper_report(verification_lift_v2_manifest_path, None)
            or build_paper_report(verification_lift_v2_manifest_path)
        )
        result.update({
            "verification_lift_v2": verification_lift_v2_report["aggregate"],
            "verification_lift_v2_taxonomy_distribution": verification_lift_v2_report["taxonomy_distribution"],
            "verification_lift_v2_outcome_counts": verification_lift_v2_report["outcome_counts"],
            "verification_lift_v2_signal_by_outcome": verification_lift_v2_report["signal_by_outcome"],
            "verification_lift_v2_paired_task_summary": verification_lift_v2_report["paired_task_summary"],
        })
    if verification_ablation_manifest_path and verification_ablation_labels_path:
        verification_ablation_report = (
            _load_finalized_paper_report(verification_ablation_manifest_path, verification_ablation_labels_path)
            or build_paper_report(verification_ablation_manifest_path, labels_path=verification_ablation_labels_path)
        )
        result.update({
            "verification_ablation": verification_ablation_report["aggregate"],
            "verification_ablation_label_evaluation": verification_ablation_report["detector_evaluation"],
            "verification_ablation_taxonomy_distribution": verification_ablation_report["taxonomy_distribution"],
            "verification_ablation_outcome_counts": verification_ablation_report["outcome_counts"],
            "verification_ablation_signal_by_outcome": verification_ablation_report["signal_by_outcome"],
            "verification_ablation_paired_task_summary": verification_ablation_report["paired_task_summary"],
        })
    return result


def _load_finalized_aggregate(manifest_path: str | Path) -> dict[str, Any] | None:
    aggregate_path = Path(manifest_path).parent / "aggregate.json"
    if not aggregate_path.exists():
        return None
    return json.loads(aggregate_path.read_text(encoding="utf-8"))


def _load_finalized_paper_report(manifest_path: str | Path, labels_path: str | Path | None) -> dict[str, Any] | None:
    run_dir = Path(manifest_path).parent
    candidates = [run_dir / "paper-report-labeled.json", run_dir / "paper-report.json"] if labels_path else [run_dir / "paper-report.json"]
    for path in candidates:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def render_results_summary_markdown(result: dict[str, Any]) -> str:
    full = result["full30"]
    full_process_eval = result.get("full30_process_label_evaluation")
    detector_fixture_eval = result.get("detector_fixture_label_evaluation")
    hard = result["hard10"]
    hard30 = result.get("hard30")
    process_stress = result.get("process_stress")
    verification_lift = result.get("verification_lift")
    verification_lift_v2 = result.get("verification_lift_v2")
    verification_ablation = result.get("verification_ablation")
    hard_eval = result["hard10_label_evaluation"]
    hard_counts = result["hard10_outcome_counts"]
    boundary_eval = result.get("hard30_label_evaluation", hard_eval)
    boundary_counts = result.get("hard30_outcome_counts", hard_counts)
    boundary_signal_rows = result.get("hard30_signal_by_outcome", result["hard10_signal_by_outcome"])
    boundary_name = "Hard30" if hard30 else "Hard10"
    hidden_scores = boundary_eval["labels"].get("hidden_semantic_edge_case", {})

    lines = [
        "# CodexTrace Results Summary",
        "",
        "This generated summary consolidates the current paper-facing result tables.",
        "",
        "## Pilots",
        "",
        "| Pilot | Tasks | Runs | Failure outcomes | Main use |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| full30 | {full['summary']['baseline']['n']} | {len(full['runs'])} | {sum(row['outcome'] == 'failure' for row in full['runs'])} | Process-waste analysis with saturated outcomes. |",
        f"| hard10 | {hard['summary']['baseline']['n']} | {len(hard['runs'])} | {hard_counts.get('failure', 0)} | Outcome-failure and hidden-grader analysis. |",
    ]
    if hard30:
        lines.append(
            f"| hard30 | {hard30['summary']['baseline']['n']} | {len(hard30['runs'])} | "
            f"{boundary_counts.get('failure', 0)} | Submission-ready hard-tier hidden-grader artifact. |"
        )
    if process_stress:
        process_counts = result.get("process_stress_outcome_counts", {})
        lines.append(
            f"| process-stress | {process_stress['summary']['baseline']['n']} | {len(process_stress['runs'])} | "
            f"{process_counts.get('failure', 0)} | Failure-mode stress tasks with real Codex traces. |"
        )
    if verification_lift:
        verification_counts = result.get("verification_lift_outcome_counts", {})
        lines.append(
            f"| verification-lift | {verification_lift['summary']['baseline']['n']} | {len(verification_lift['runs'])} | "
            f"{verification_counts.get('failure', 0)} | Targeted verification-rate stress prompt contrast. |"
        )
    if verification_lift_v2:
        verification_v2_counts = result.get("verification_lift_v2_outcome_counts", {})
        lines.append(
            f"| verification-lift-v2 | {verification_lift_v2['summary']['baseline']['n']} | {len(verification_lift_v2['runs'])} | "
            f"{verification_v2_counts.get('failure', 0)} | Ordinary-baseline verification-rate retest with real Codex traces. |"
        )
    if verification_ablation:
        ablation_counts = result.get("verification_ablation_outcome_counts", {})
        lines.append(
            f"| verification-ablation | {verification_ablation['summary']['baseline']['n']} | {len(verification_ablation['runs'])} | "
            f"{ablation_counts.get('failure', 0)} | Auxiliary no-verify baseline ablation, not an ordinary baseline. |"
        )
    lines.extend([
        "",
        "## RQ3 Baseline vs Intervention",
        "",
        "### Headline Result Snapshot",
        "",
        "| Evidence slice | Baseline | Intervention | Interpretation |",
        "| --- | ---: | ---: | --- |",
        (
            f"| hard10 success | {_fmt_signal_metric('success_rate', hard['summary']['baseline']['success_rate'])} | "
            f"{_fmt_signal_metric('success_rate', hard['summary']['intervention']['success_rate'])} | "
            "Pilot success lift; not stable enough alone for a broad claim. |"
        ),
    ])
    if hard30:
        lines.append(
            f"| hard30 waste | {_fmt(hard30['summary']['baseline']['avg_repeated_tool_calls'])} repeated calls / "
            f"{_fmt_signal_metric('token_usage', hard30['summary']['baseline']['avg_token_usage'])} tokens | "
            f"{_fmt(hard30['summary']['intervention']['avg_repeated_tool_calls'])} repeated calls / "
            f"{_fmt_signal_metric('token_usage', hard30['summary']['intervention']['avg_token_usage'])} tokens | "
            "Supported paired waste reduction with flat success. |"
        )
    if verification_lift:
        lines.append(
            f"| verification-lift stress | {_fmt_signal_metric('verification_rate', verification_lift['summary']['baseline']['verification_rate'])} broad / "
            f"{_fmt_signal_metric('success_check_verification_rate', verification_lift['summary']['baseline']['success_check_verification_rate'])} exact | "
            f"{_fmt_signal_metric('verification_rate', verification_lift['summary']['intervention']['verification_rate'])} broad / "
            f"{_fmt_signal_metric('success_check_verification_rate', verification_lift['summary']['intervention']['success_check_verification_rate'])} exact | "
            "Negative result for ordinary or weak-baseline verification-rate lift. |"
        )
    if verification_lift_v2:
        lines.append(
            f"| verification-lift-v2 ordinary retest | {_fmt_signal_metric('verification_rate', verification_lift_v2['summary']['baseline']['verification_rate'])} broad / "
            f"{_fmt_signal_metric('success_check_verification_rate', verification_lift_v2['summary']['baseline']['success_check_verification_rate'])} exact | "
            f"{_fmt_signal_metric('verification_rate', verification_lift_v2['summary']['intervention']['verification_rate'])} broad / "
            f"{_fmt_signal_metric('success_check_verification_rate', verification_lift_v2['summary']['intervention']['success_check_verification_rate'])} exact | "
            "Negative ordinary-baseline retest; waste still improves. |"
        )
    if verification_ablation:
        lines.append(
            f"| no-verify ablation | {_fmt_signal_metric('verification_rate', verification_ablation['summary']['baseline']['verification_rate'])} broad / "
            f"{_fmt_signal_metric('success_check_verification_rate', verification_ablation['summary']['baseline']['success_check_verification_rate'])} exact | "
            f"{_fmt_signal_metric('verification_rate', verification_ablation['summary']['intervention']['verification_rate'])} broad / "
            f"{_fmt_signal_metric('success_check_verification_rate', verification_ablation['summary']['intervention']['success_check_verification_rate'])} exact | "
            "Mechanism check only; not an ordinary baseline. |"
        )
    lines.extend([
        "",
        "### Full30 Seed Pilot",
        "",
        "| Metric | Baseline | Intervention | Delta |",
        "| --- | ---: | ---: | ---: |",
    ])
    _append_metric_rows(lines, full, (
        "success_rate",
        "verification_rate",
        "success_check_verification_rate",
        "unresolved_error_rate",
        "avg_repeated_tool_calls",
        "avg_command_failures",
        "avg_turn_count",
        "avg_time_to_first_edit",
        "avg_time_to_first_test",
        "avg_recover_events",
        "avg_token_usage",
        "avg_failure_score",
    ))

    lines.extend([
        "",
        "### Hard10 Pilot",
        "",
        "| Metric | Baseline | Intervention | Delta |",
        "| --- | ---: | ---: | ---: |",
    ])
    _append_metric_rows(lines, hard, (
        "success_rate",
        "verification_rate",
        "success_check_verification_rate",
        "unresolved_error_rate",
        "avg_repeated_tool_calls",
        "avg_turn_count",
        "avg_time_to_first_edit",
        "avg_time_to_first_test",
        "avg_token_usage",
        "avg_verify_events",
    ))

    if hard30:
        lines.extend([
            "",
            "### Hard30 Pilot",
            "",
            "| Metric | Baseline | Intervention | Delta |",
            "| --- | ---: | ---: | ---: |",
        ])
        _append_metric_rows(lines, hard30, (
            "success_rate",
            "verification_rate",
            "success_check_verification_rate",
            "unresolved_error_rate",
            "avg_repeated_tool_calls",
            "avg_command_failures",
            "avg_turn_count",
            "avg_time_to_first_edit",
            "avg_time_to_first_test",
            "avg_token_usage",
            "avg_failure_score",
        ))
        paired = result.get("hard30_paired_task_summary", {})
        token_row = paired.get("token_usage_delta", {})
        repeated_row = paired.get("repeated_tool_call_delta", {})
        success_row = paired.get("success_delta", {})
        lines.extend([
            "",
            (
                "Paired hard30 deltas: token usage improves in "
                f"{token_row.get('improved', 0)}/{token_row.get('n', 0)} tasks, repeated tool calls improve in "
                f"{repeated_row.get('improved', 0)}/{repeated_row.get('n', 0)} tasks, success improves in "
                f"{success_row.get('improved', 0)} task(s) and regresses in {success_row.get('regressed', 0)} task(s)."
            ),
        ])

    if process_stress:
        lines.extend([
            "",
            "### Process-Stress Pilot",
            "",
            "| Metric | Baseline | Intervention | Delta |",
            "| --- | ---: | ---: | ---: |",
        ])
        _append_metric_rows(lines, process_stress, (
            "success_rate",
            "verification_rate",
            "success_check_verification_rate",
            "unresolved_error_rate",
            "avg_repeated_tool_calls",
            "avg_turn_count",
            "avg_time_to_first_edit",
            "avg_time_to_first_test",
            "avg_recover_events",
            "avg_token_usage",
            "avg_failure_score",
        ))
        paired = result.get("process_stress_paired_task_summary", {})
        token_row = paired.get("token_usage_delta", {})
        repeated_row = paired.get("repeated_tool_call_delta", {})
        success_row = paired.get("success_delta", {})
        lines.extend([
            "",
            (
                "Paired process-stress deltas: token usage improves in "
                f"{token_row.get('improved', 0)}/{token_row.get('n', 0)} tasks, repeated tool calls improve in "
                f"{repeated_row.get('improved', 0)}/{repeated_row.get('n', 0)} tasks, success improves in "
                f"{success_row.get('improved', 0)} task(s) and regresses in {success_row.get('regressed', 0)} task(s)."
            ),
        ])

    if verification_lift:
        lines.extend([
            "",
            "### Verification-Lift Pilot",
            "",
            "| Metric | Baseline | Intervention | Delta |",
            "| --- | ---: | ---: | ---: |",
        ])
        _append_metric_rows(lines, verification_lift, (
            "success_rate",
            "verification_rate",
            "success_check_verification_rate",
            "unresolved_error_rate",
            "avg_repeated_tool_calls",
            "avg_turn_count",
            "avg_time_to_first_edit",
            "avg_time_to_first_test",
            "avg_verify_events",
            "avg_token_usage",
            "avg_failure_score",
        ))
        paired = result.get("verification_lift_paired_task_summary", {})
        token_row = paired.get("token_usage_delta", {})
        repeated_row = paired.get("repeated_tool_call_delta", {})
        verification_row = paired.get("verification_delta", {})
        success_check_row = paired.get("success_check_verification_delta", {})
        lines.extend([
            "",
            (
                "Paired verification-lift deltas: verification improves in "
                f"{verification_row.get('improved', 0)}/{verification_row.get('n', 0)} tasks, exact success-check verification improves in "
                f"{success_check_row.get('improved', 0)}/{success_check_row.get('n', 0)} tasks, token usage improves in "
                f"{token_row.get('improved', 0)}/{token_row.get('n', 0)} tasks, repeated tool calls improve in "
                f"{repeated_row.get('improved', 0)}/{repeated_row.get('n', 0)} tasks."
            ),
        ])

    if verification_lift_v2:
        lines.extend([
            "",
            "### Verification-Lift-V2 Pilot",
            "",
            "This ordinary-baseline retest is a negative result for verification-rate lift, while still showing lower process waste under the intervention prompt.",
            "",
            "| Metric | Baseline | Intervention | Delta |",
            "| --- | ---: | ---: | ---: |",
        ])
        _append_metric_rows(lines, verification_lift_v2, (
            "success_rate",
            "verification_rate",
            "success_check_verification_rate",
            "unresolved_error_rate",
            "avg_repeated_tool_calls",
            "avg_turn_count",
            "avg_time_to_first_edit",
            "avg_time_to_first_test",
            "avg_verify_events",
            "avg_token_usage",
            "avg_failure_score",
        ))
        paired = result.get("verification_lift_v2_paired_task_summary", {})
        token_row = paired.get("token_usage_delta", {})
        repeated_row = paired.get("repeated_tool_call_delta", {})
        verification_row = paired.get("verification_delta", {})
        success_check_row = paired.get("success_check_verification_delta", {})
        success_row = paired.get("success_delta", {})
        lines.extend([
            "",
            (
                "Paired verification-lift-v2 deltas: verification improves in "
                f"{verification_row.get('improved', 0)}/{verification_row.get('n', 0)} tasks, exact success-check verification improves in "
                f"{success_check_row.get('improved', 0)}/{success_check_row.get('n', 0)} tasks, token usage improves in "
                f"{token_row.get('improved', 0)}/{token_row.get('n', 0)} tasks, repeated tool calls improve in "
                f"{repeated_row.get('improved', 0)}/{repeated_row.get('n', 0)} tasks, and success improves in "
                f"{success_row.get('improved', 0)} task(s) while regressing in {success_row.get('regressed', 0)} task(s)."
            ),
        ])

    if verification_ablation:
        lines.extend([
            "",
            "### Verification Ablation Pilot",
            "",
            "This auxiliary pilot uses an explicit no-verification baseline and should not be interpreted as the ordinary Codex baseline.",
            "",
            "| Metric | Baseline | Intervention | Delta |",
            "| --- | ---: | ---: | ---: |",
        ])
        _append_metric_rows(lines, verification_ablation, (
            "success_rate",
            "verification_rate",
            "success_check_verification_rate",
            "unresolved_error_rate",
            "avg_repeated_tool_calls",
            "avg_turn_count",
            "avg_time_to_first_edit",
            "avg_time_to_first_test",
            "avg_verify_events",
            "avg_token_usage",
            "avg_failure_score",
        ))
        paired = result.get("verification_ablation_paired_task_summary", {})
        verification_row = paired.get("verification_delta", {})
        success_check_row = paired.get("success_check_verification_delta", {})
        score_row = paired.get("failure_score_delta", {})
        lines.extend([
            "",
            (
                "Paired verification-ablation deltas: verification improves in "
                f"{verification_row.get('improved', 0)}/{verification_row.get('n', 0)} tasks, exact success-check verification improves in "
                f"{success_check_row.get('improved', 0)}/{success_check_row.get('n', 0)} tasks, and failure score improves in "
                f"{score_row.get('improved', 0)}/{score_row.get('n', 0)} tasks."
            ),
        ])

    lines.extend([
        "",
        "## RQ2 Detector Boundary Result",
        "",
        "| Label | TP | FP | FN | Precision | Recall | F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for label, scores in sorted(boundary_eval["labels"].items()):
        lines.append(
            f"| {label} | {scores.get('tp', 0)} | {scores.get('fp', 0)} | {scores.get('fn', 0)} | "
            f"{_fmt(scores.get('precision', 0))} | {_fmt(scores.get('recall', 0))} | {_fmt(scores.get('f1', 0))} |"
        )
    lines.extend([
        "",
        "Interpretation: deterministic process rules detect high-volume `repetitive_exploration` positives, but still do not detect hidden semantic edge-case failures when the visible process trace looks clean.",
    ])
    if detector_fixture_eval:
        fixture_summary = detector_fixture_eval.get("summary", {})
        lines.extend([
            "",
            "### Controlled Detector Fixture Check",
            "",
            (
                "These minimal JSONL traces are rule-level fixtures, not real Codex pilot runs. "
                f"They cover {fixture_summary.get('labels', 0)} process labels with "
                f"micro-F1 {_fmt(fixture_summary.get('micro_f1', 0))}."
            ),
            "",
            "| Label | TP | FP | FN | Precision | Recall | F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for label, scores in sorted(detector_fixture_eval.get("labels", {}).items()):
            lines.append(
                f"| {label} | {scores.get('tp', 0)} | {scores.get('fp', 0)} | {scores.get('fn', 0)} | "
                f"{_fmt(scores.get('precision', 0))} | {_fmt(scores.get('recall', 0))} | {_fmt(scores.get('f1', 0))} |"
            )
    if full_process_eval:
        lines.extend([
            "",
            "### Full30 Process-Positive Detector Check",
            "",
            "| Label | TP | FP | FN | Precision | Recall | F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for label, scores in sorted(full_process_eval.get("labels", {}).items()):
            lines.append(
                f"| {label} | {scores.get('tp', 0)} | {scores.get('fp', 0)} | {scores.get('fn', 0)} | "
                f"{_fmt(scores.get('precision', 0))} | {_fmt(scores.get('recall', 0))} | {_fmt(scores.get('f1', 0))} |"
            )
        lines.extend([
            "",
            "Interpretation: full30 adds an observed sandbox/permission process positive, while also exposing repetitive-exploration false positives in the process-label slice.",
        ])
    if process_stress:
        process_eval = result.get("process_stress_label_evaluation", {})
        process_hidden = process_eval.get("labels", {}).get("hidden_semantic_edge_case", {})
        lines.extend([
            "",
            "### Process-Stress Detector Boundary Check",
            "",
            "| Label | TP | FP | FN | Precision | Recall | F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for label, scores in sorted(process_eval.get("labels", {}).items()):
            lines.append(
                f"| {label} | {scores.get('tp', 0)} | {scores.get('fp', 0)} | {scores.get('fn', 0)} | "
                f"{_fmt(scores.get('precision', 0))} | {_fmt(scores.get('recall', 0))} | {_fmt(scores.get('f1', 0))} |"
            )
        lines.extend([
            "",
            (
                "Interpretation: the process-stress pilot repeats the same boundary: both failed runs are "
                f"hidden semantic edge cases, producing {process_hidden.get('fn', 0)} trace-only false negatives."
            ),
        ])
    if verification_lift:
        verification_eval = result.get("verification_lift_label_evaluation", {})
        verification_hidden = verification_eval.get("labels", {}).get("hidden_semantic_edge_case", {})
        lines.extend([
            "",
            "### Verification-Lift Detector Boundary Check",
            "",
            "| Label | TP | FP | FN | Precision | Recall | F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for label, scores in sorted(verification_eval.get("labels", {}).items()):
            lines.append(
                f"| {label} | {scores.get('tp', 0)} | {scores.get('fp', 0)} | {scores.get('fn', 0)} | "
                f"{_fmt(scores.get('precision', 0))} | {_fmt(scores.get('recall', 0))} | {_fmt(scores.get('f1', 0))} |"
            )
        lines.extend([
            "",
            (
                "Interpretation: the targeted verification-lift pilot still has saturated verification "
                f"and {verification_hidden.get('fn', 0)} hidden semantic false negatives."
            ),
        ])
    if verification_ablation:
        ablation_eval = result.get("verification_ablation_label_evaluation", {})
        lines.extend([
            "",
            "### Verification Ablation Detector Check",
            "",
            "| Label | TP | FP | FN | Precision | Recall | F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for label, scores in sorted(ablation_eval.get("labels", {}).items()):
            lines.append(
                f"| {label} | {scores.get('tp', 0)} | {scores.get('fp', 0)} | {scores.get('fn', 0)} | "
                f"{_fmt(scores.get('precision', 0))} | {_fmt(scores.get('recall', 0))} | {_fmt(scores.get('f1', 0))} |"
            )
        lines.extend([
            "",
            "Interpretation: explicit no-verify ablation creates detectable verification gaps, while hidden semantic failures remain outside process-rule detection.",
        ])
    lines.extend([
        "",
        "## RQ4 Trace Signals By Outcome",
        "",
        f"{boundary_name} outcome failures are hidden semantic edge cases, so most process signals do not separate failures from successes.",
        "",
        "| Signal | Failure mean | Success mean | Delta success-failure |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in boundary_signal_rows:
        lines.append(
            f"| {row['signal']} | {_fmt_signal_metric(row['signal'], row['failure_mean'])} | "
            f"{_fmt_signal_metric(row['signal'], row['success_mean'])} | "
            f"{_fmt_signal_metric(row['signal'], row['delta_success_minus_failure'])} |"
        )

    lines.extend([
        "",
        "Interpretation: `verification_rate` and `unresolved_error` do not separate hidden semantic failures from successes. The visible traces often look procedurally clean; hidden graders reveal the missed semantic edge cases.",
        "",
        "## Claim-Evidence Shortlist",
        "",
        "| Claim | Generated evidence |",
        "| --- | --- |",
        "| Intervention reduces process waste on full30. | `avg_repeated_tool_calls`, `avg_command_failures`, `avg_recover_events`, and `avg_token_usage` improve in the full30 table. |",
        "| Intervention improves success on hard10. | hard10 `success_rate` improves from baseline to intervention. |",
        "| Intervention reduces waste on hard30. | hard30 repeated tool calls, command failures, token usage, and failure score improve. |" if hard30 else "",
        "| Process-stress intervention reduces token and repeated-call waste while success stays flat. | process-stress keeps success at 91.67% while reducing repeated tool calls and token usage. |" if process_stress else "",
        "| Verification-lift stress test does not support a verification-rate lift. | verification-lift verification remains 100% -> 100%, while repeated calls and token usage fall slightly. |" if verification_lift else "",
        "| Verification-lift-v2 ordinary retest does not support a verification-rate lift. | verification-lift-v2 verification remains 100% -> 100%, while repeated calls and token usage fall. |" if verification_lift_v2 else "",
        f"| Trace-only process rules have a semantic boundary. | {boundary_name.lower()} label evaluation has {hidden_scores.get('fn', 0)} false negatives for `hidden_semantic_edge_case`, while detecting observed process positives such as `repetitive_exploration`. |",
        f"| RQ4 signal analysis explains the detector boundary. | {boundary_name.lower()} `verification_rate` and `unresolved_error` are equal for successful and failed runs. |",
        "| Strong task oracles remain necessary. | hard-tier failures are only visible through hidden graders, not process-rule findings. |",
    ])
    return "\n".join(lines) + "\n"


def write_results_summary_outputs(result: dict[str, Any], json_path: str | Path | None = None, markdown_path: str | Path | None = None) -> None:
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if markdown_path:
        path = Path(markdown_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_results_summary_markdown(result), encoding="utf-8")


def taxonomy_distribution(run_rows: list[dict[str, Any]], labels: dict[tuple[str, str], set[str]] | None = None) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    examples: dict[str, str] = {}
    total = 0
    for row in run_rows:
        key = (str(row["task_id"]), str(row["prompt_type"]))
        tags = sorted(labels.get(key, set())) if labels else row.get("taxonomy_tags", [])
        for tag in tags:
            counts[tag] += 1
            total += 1
            examples.setdefault(tag, f"{row['task_id']}/{row['prompt_type']}")
    return [
        {
            "failure_tag": tag,
            "count": count,
            "percentage": round(100 * count / total, 2) if total else 0,
            "example_task": examples.get(tag, "-"),
        }
        for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def outcome_counts(run_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter(str(row.get("outcome", "unknown")) for row in run_rows)
    for outcome in ("success", "failure", "unknown"):
        counts.setdefault(outcome, 0)
    return dict(counts)


def paired_task_deltas(run_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task: dict[str, dict[str, dict[str, Any]]] = {}
    for row in run_rows:
        by_task.setdefault(str(row["task_id"]), {})[str(row["prompt_type"])] = row

    rows = []
    for task_id, prompts in sorted(by_task.items()):
        baseline = prompts.get("baseline")
        intervention = prompts.get("intervention")
        if not baseline or not intervention:
            continue
        rows.append({
            "task_id": task_id,
            "baseline_outcome": baseline["outcome"],
            "intervention_outcome": intervention["outcome"],
            "success_delta": intervention["success"] - baseline["success"],
            "verification_delta": intervention["verification_rate"] - baseline["verification_rate"],
            "success_check_verification_delta": (
                intervention["success_check_verification_rate"] - baseline["success_check_verification_rate"]
            ),
            "repeated_tool_call_delta": intervention["repeated_tool_call_count"] - baseline["repeated_tool_call_count"],
            "token_usage_delta": intervention["token_usage"] - baseline["token_usage"],
            "failure_score_delta": intervention["failure_score"] - baseline["failure_score"],
        })
    return rows


def paired_task_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    directions = {
        "success_delta": 1,
        "verification_delta": 1,
        "success_check_verification_delta": 1,
        "repeated_tool_call_delta": -1,
        "token_usage_delta": -1,
        "failure_score_delta": -1,
    }
    summary = {}
    for key, direction in directions.items():
        values = [float(row[key]) for row in rows]
        summary[key] = {
            "n": len(values),
            "improved": sum(value * direction > 0 for value in values),
            "regressed": sum(value * direction < 0 for value in values),
            "unchanged": sum(value == 0 for value in values),
            "avg_delta": round(mean(values), 4) if values else 0,
        }
    return summary


def signal_summary_by_outcome(run_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failure_rows = [row for row in run_rows if row.get("outcome") == "failure"]
    success_rows = [row for row in run_rows if row.get("outcome") == "success"]
    rows = []
    for key in PAPER_SIGNAL_KEYS:
        failure_mean = _mean(failure_rows, key) if failure_rows else 0
        success_mean = _mean(success_rows, key) if success_rows else 0
        rows.append({
            "signal": key,
            "failure_mean": failure_mean,
            "success_mean": success_mean,
            "delta_success_minus_failure": round(success_mean - failure_mean, 4),
        })
    return rows


def signal_summary_by_label(run_rows: list[dict[str, Any]], labels: dict[tuple[str, str], set[str]]) -> list[dict[str, Any]]:
    if not labels:
        return []

    rows = []
    overall_rows = [row for row in run_rows if row.get("outcome") == "failure"]
    if not overall_rows:
        overall_rows = run_rows
    for tag in sorted({tag for tags in labels.values() for tag in tags}):
        tagged_rows = [
            row for row in run_rows
            if tag in labels.get((str(row["task_id"]), str(row["prompt_type"])), set())
        ]
        if not tagged_rows:
            continue
        for key in PAPER_SIGNAL_KEYS:
            label_mean = _mean(tagged_rows, key)
            overall_mean = _mean(overall_rows, key) if overall_rows else 0
            rows.append({
                "failure_tag": tag,
                "n": len(tagged_rows),
                "signal": key,
                "label_mean": label_mean,
                "overall_mean": overall_mean,
                "delta_label_minus_overall": round(label_mean - overall_mean, 4),
            })
    return rows


def generate_label_template(manifest_path: str | Path, include_predictions: bool = False) -> list[dict[str, Any]]:
    rows = []
    for record, raw_trace_path in _load_run_manifest_items(manifest_path):
        row: dict[str, Any] = {
            "task_id": record.task_id,
            "prompt_type": record.prompt_type,
            "trace_path": raw_trace_path,
            "outcome": record.outcome,
            "failure_tags": [],
            "notes": "",
        }
        if include_predictions:
            trace = parse_jsonl(record.trace_path)
            diagnosis = diagnose(trace)
            row["suggested_tags"] = sorted({canonical_label(finding.code) for finding in diagnosis.findings})
            row["failure_score"] = diagnosis.failure_score
        rows.append(row)
    return rows


def render_label_template_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


def write_label_template(rows: list[dict[str, Any]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_label_template_jsonl(rows), encoding="utf-8")


def evaluate_detector_labels(manifest_path: str | Path, labels_path: str | Path) -> dict[str, Any]:
    records = load_run_manifest(manifest_path)
    labels = load_manual_labels(labels_path)
    rows = []
    for record in records:
        key = (record.task_id, record.prompt_type)
        expected = set(labels.get(key, set()))
        trace = parse_jsonl(record.trace_path)
        diagnosis = diagnose(trace)
        predicted = {canonical_label(finding.code) for finding in diagnosis.findings}
        rows.append({
            "task_id": record.task_id,
            "prompt_type": record.prompt_type,
            "expected": sorted(expected),
            "predicted": sorted(predicted),
            "true_positive": sorted(expected & predicted),
            "false_positive": sorted(predicted - expected),
            "false_negative": sorted(expected - predicted),
        })
    return {
        "runs": rows,
        "labels": _label_scores(rows),
        "summary": _label_summary(_label_scores(rows)),
    }


def load_manual_labels(path: str | Path) -> dict[tuple[str, str], set[str]]:
    label_path = Path(path)
    labels: dict[tuple[str, str], set[str]] = {}
    for line in label_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        key = (str(item["task_id"]), str(item["prompt_type"]))
        tags = item.get("failure_tags", [])
        labels[key] = {canonical_label(str(tag)) for tag in tags}
    return labels


def canonical_label(label: str) -> str:
    return TAXONOMY_ALIASES.get(label, label)


def render_label_evaluation_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Detector Label Evaluation",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in result["summary"].items():
        lines.append(f"| {key} | {_fmt(value)} |")

    lines.extend(["", "## Per-Label Scores", "", "| Label | TP | FP | FN | Precision | Recall | F1 |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for label, scores in sorted(result["labels"].items()):
        lines.append(
            f"| {label} | {scores['tp']} | {scores['fp']} | {scores['fn']} | "
            f"{_fmt(scores['precision'])} | {_fmt(scores['recall'])} | {_fmt(scores['f1'])} |"
        )

    lines.extend(["", "## Runs", "", "| Task | Prompt | Expected | Predicted | FP | FN |", "| --- | --- | --- | --- | --- | --- |"])
    for row in result["runs"]:
        lines.append(
            f"| {row['task_id']} | {row['prompt_type']} | {_join_labels(row['expected'])} | "
            f"{_join_labels(row['predicted'])} | {_join_labels(row['false_positive'])} | {_join_labels(row['false_negative'])} |"
        )
    return "\n".join(lines) + "\n"


def write_label_evaluation_outputs(result: dict[str, Any], json_path: str | Path | None = None, markdown_path: str | Path | None = None) -> None:
    if json_path:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if markdown_path:
        path = Path(markdown_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_label_evaluation_markdown(result), encoding="utf-8")


def _run_metrics(record: RunRecord, trace: Trace, diagnosis: Diagnosis) -> dict[str, Any]:
    metrics = diagnosis.metrics
    finding_codes = [finding.code for finding in diagnosis.findings]
    taxonomy_tags = [canonical_label(code) for code in finding_codes]
    phase_counts = _phase_counts(trace)
    visible_success_check = _visible_success_check(record)
    return {
        "task_id": record.task_id,
        "prompt_type": record.prompt_type,
        "trace_path": str(record.trace_path),
        "outcome": record.outcome,
        "success": 1 if record.outcome == "success" else 0,
        "verification_rate": 1 if metrics.get("post_edit_verification_commands", 0) > 0 else 0,
        "success_check_verification_rate": _has_post_edit_success_check(trace, visible_success_check),
        "visible_success_check": visible_success_check,
        "unresolved_error": 1 if "command_failure_unhandled" in finding_codes else 0,
        "repeated_tool_call_count": _repeated_tool_call_count(trace),
        "retry_count": _retry_count(trace),
        "command_failure_count": metrics.get("failed_commands", 0),
        "token_usage": metrics.get("input_tokens", 0) + metrics.get("output_tokens", 0),
        "failure_score": diagnosis.failure_score,
        "turn_count": sum(event.kind == "turn" and event.status == "completed" for event in trace.events),
        "time_to_first_edit": _index_of_first(trace, "file_change"),
        "time_to_first_test": _index_of_first_verification(trace),
        "phase_setup_events": phase_counts["setup"],
        "phase_inspect_events": phase_counts["inspect"],
        "phase_edit_events": phase_counts["edit"],
        "phase_verify_events": phase_counts["verify"],
        "phase_recover_events": phase_counts["recover"],
        "phase_complete_events": phase_counts["complete"],
        "phase_other_events": phase_counts["other"],
        "finding_codes": finding_codes,
        "taxonomy_tags": taxonomy_tags,
    }


def _visible_success_check(record: RunRecord) -> str:
    if record.prompt_path and record.prompt_path.exists():
        lines = record.prompt_path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines[:-1]):
            if line.strip().lower() in {"success check:", "visible success check:"}:
                return lines[index + 1].strip()
    return record.success_check.strip()


def _has_post_edit_success_check(trace: Trace, success_check: str) -> int:
    normalized_check = _normalize_command_for_match(success_check)
    if not normalized_check:
        return 0
    saw_edit = False
    for event in trace.events:
        if event.kind == "file_change":
            saw_edit = True
        elif saw_edit and event.kind == "command" and event.command:
            if normalized_check in _normalize_command_for_match(event.command):
                return 1
    return 0


def _normalize_command_for_match(command: str) -> str:
    return re.sub(r"\s+", " ", command.strip().lower())


def _label_scores(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    labels = sorted({label for row in rows for label in row["expected"] + row["predicted"]})
    scores = {}
    for label in labels:
        tp = sum(label in row["true_positive"] for row in rows)
        fp = sum(label in row["false_positive"] for row in rows)
        fn = sum(label in row["false_negative"] for row in rows)
        scores[label] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": _safe_div(tp, tp + fp),
            "recall": _safe_div(tp, tp + fn),
            "f1": _safe_f1(tp, fp, fn),
        }
    return scores


def _label_summary(scores: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not scores:
        return {"labels": 0, "micro_precision": 0, "micro_recall": 0, "micro_f1": 0, "macro_f1": 0}
    tp = sum(score["tp"] for score in scores.values())
    fp = sum(score["fp"] for score in scores.values())
    fn = sum(score["fn"] for score in scores.values())
    return {
        "labels": len(scores),
        "micro_precision": _safe_div(tp, tp + fp),
        "micro_recall": _safe_div(tp, tp + fn),
        "micro_f1": _safe_f1(tp, fp, fn),
        "macro_f1": round(mean(score["f1"] for score in scores.values()), 4),
    }


def _safe_div(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0


def _safe_f1(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return round((2 * precision * recall / (precision + recall)), 4) if precision + recall else 0


def _join_labels(labels: list[str]) -> str:
    return ", ".join(labels) if labels else "-"


def _append_metric_rows(lines: list[str], result: dict[str, Any], keys: tuple[str, ...]) -> None:
    for key in keys:
        baseline = result["summary"].get("baseline", {}).get(key, 0)
        intervention = result["summary"].get("intervention", {}).get(key, 0)
        delta = result["deltas"].get(key, 0)
        lines.append(f"| {key} | {_fmt_result_metric(key, baseline)} | {_fmt_result_metric(key, intervention)} | {_fmt_result_metric(key, delta)} |")


def _fmt_result_metric(key: str, value: Any) -> str:
    numeric = float(value or 0)
    if key == "avg_token_usage":
        return f"{numeric / 1000:.1f}k"
    if key.endswith("_rate"):
        return f"{numeric:.2f}"
    return _fmt(value)


def _fmt_signal_metric(signal: str, value: Any) -> str:
    numeric = float(value or 0)
    if signal == "token_usage":
        return f"{numeric / 1000:.1f}k"
    if signal.endswith("_rate"):
        return f"{numeric:.2f}"
    return _fmt(value)


def _summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        "success_rate": _mean(rows, "success"),
        "verification_rate": _mean(rows, "verification_rate"),
        "success_check_verification_rate": _mean(rows, "success_check_verification_rate"),
        "unresolved_error_rate": _mean(rows, "unresolved_error"),
        "avg_repeated_tool_calls": _mean(rows, "repeated_tool_call_count"),
        "avg_retry_count": _mean(rows, "retry_count"),
        "avg_command_failures": _mean(rows, "command_failure_count"),
        "avg_token_usage": _mean(rows, "token_usage"),
        "avg_failure_score": _mean(rows, "failure_score"),
        "avg_turn_count": _mean(rows, "turn_count"),
        "avg_time_to_first_edit": _mean_present(rows, "time_to_first_edit"),
        "avg_time_to_first_test": _mean_present(rows, "time_to_first_test"),
        "avg_inspect_events": _mean(rows, "phase_inspect_events"),
        "avg_edit_events": _mean(rows, "phase_edit_events"),
        "avg_verify_events": _mean(rows, "phase_verify_events"),
        "avg_recover_events": _mean(rows, "phase_recover_events"),
    }


def _deltas(baseline: dict[str, Any], intervention: dict[str, Any]) -> dict[str, float]:
    keys = sorted(set(baseline) | set(intervention))
    return {
        key: float(intervention.get(key, 0) or 0) - float(baseline.get(key, 0) or 0)
        for key in keys
        if key != "n"
    }


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    return round(mean(float(row.get(key, 0) or 0) for row in rows), 4)


def _mean_present(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return round(mean(values), 4) if values else 0


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _repeated_tool_call_count(trace: Trace) -> int:
    commands = [event.command for event in trace.events if event.kind == "command" and event.command]
    counts = {}
    repeated = 0
    for command in commands:
        counts[command] = counts.get(command, 0) + 1
        if counts[command] > 1:
            repeated += 1
    return repeated


def _retry_count(trace: Trace) -> int:
    failed_commands: set[str] = set()
    retries = 0
    for event in trace.events:
        if event.kind != "command" or not event.command:
            continue
        command = " ".join(event.command.strip().split())
        if command in failed_commands:
            retries += 1
        if event.exit_code not in (None, 0):
            failed_commands.add(command)
        elif command in failed_commands:
            failed_commands.remove(command)
    return retries


def _phase_counts(trace: Trace) -> Counter[str]:
    counts: Counter[str] = Counter(event.phase for event in trace.events)
    for phase in ("setup", "inspect", "edit", "verify", "recover", "complete", "other"):
        counts.setdefault(phase, 0)
    return counts


def _index_of_first(trace: Trace, kind: str) -> int | None:
    for index, event in enumerate(trace.events):
        if event.kind == kind:
            return index
    return None


def _index_of_first_verification(trace: Trace) -> int | None:
    for index, event in enumerate(trace.events):
        if event.kind == "command" and is_verification_command(event.command or ""):
            return index
    return None


def _resolve_optional_path(base_dir: Path, value: Any) -> str:
    if not value:
        return ""
    path = Path(str(value))
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def _relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _clean_git_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    if extra:
        env.update(extra)
    return env
