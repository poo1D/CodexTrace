from __future__ import annotations

import csv
import json
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
    repo_hint: str = ""
    fixture_path: str = ""
    grader_path: str = ""


@dataclass
class RunRecord:
    task_id: str
    prompt_type: str
    trace_path: Path
    outcome: str = "unknown"


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
        items.append((RunRecord(
            task_id=str(item["task_id"]),
            prompt_type=str(item["prompt_type"]),
            trace_path=(manifest_path.parent / raw_trace_path).resolve(),
            outcome=str(item.get("outcome", "unknown")),
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
        success_check=task.success_check,
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
    if task.grader_path:
        shutil.copytree(task.grader_path, grader_dir)
    initialize_git_repo(repo_dir)

    prompt = render_prompt(task, prompt_type, prompt_dir)
    prompt_path.write_text(prompt, encoding="utf-8")

    if dry_run:
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
        "unresolved_error_rate",
        "avg_repeated_tool_calls",
        "avg_retry_count",
        "avg_command_failures",
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
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result["runs"]:
            serialized = dict(row)
            serialized["finding_codes"] = ";".join(row["finding_codes"])
            serialized["taxonomy_tags"] = ";".join(row["taxonomy_tags"])
            writer.writerow({key: serialized.get(key, "") for key in fieldnames})


def build_paper_report(manifest_path: str | Path, labels_path: str | Path | None = None) -> dict[str, Any]:
    aggregate = aggregate_runs(manifest_path)
    labels = load_manual_labels(labels_path) if labels_path else {}
    taxonomy = taxonomy_distribution(aggregate["runs"], labels)
    label_evaluation = evaluate_detector_labels(manifest_path, labels_path) if labels_path else None
    return {
        "aggregate": aggregate,
        "taxonomy_distribution": taxonomy,
        "detector_evaluation": label_evaluation,
        "outcome_counts": outcome_counts(aggregate["runs"]),
        "signal_by_outcome": signal_summary_by_outcome(aggregate["runs"]),
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
        "unresolved_error_rate",
        "avg_repeated_tool_calls",
        "avg_retry_count",
        "avg_command_failures",
        "avg_token_usage",
        "avg_failure_score",
        "avg_recover_events",
        "avg_verify_events",
    ):
        baseline = aggregate["summary"].get("baseline", {}).get(key, 0)
        intervention = aggregate["summary"].get("intervention", {}).get(key, 0)
        delta = aggregate["deltas"].get(key, 0)
        lines.append(f"| {key} | {_fmt(baseline)} | {_fmt(intervention)} | {_fmt(delta)} |")

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

    lines.extend(["", "## Per-Run Appendix", "", "| Task | Prompt | Outcome | Failure score | Tags |", "| --- | --- | --- | ---: | --- |"])
    for row in aggregate["runs"]:
        tags = ", ".join(row["taxonomy_tags"]) or "-"
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
    return {
        "task_id": record.task_id,
        "prompt_type": record.prompt_type,
        "trace_path": str(record.trace_path),
        "outcome": record.outcome,
        "success": 1 if record.outcome == "success" else 0,
        "verification_rate": 1 if metrics.get("post_edit_verification_commands", 0) > 0 else 0,
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


def _summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        "success_rate": _mean(rows, "success"),
        "verification_rate": _mean(rows, "verification_rate"),
        "unresolved_error_rate": _mean(rows, "unresolved_error"),
        "avg_repeated_tool_calls": _mean(rows, "repeated_tool_call_count"),
        "avg_retry_count": _mean(rows, "retry_count"),
        "avg_command_failures": _mean(rows, "command_failure_count"),
        "avg_token_usage": _mean(rows, "token_usage"),
        "avg_failure_score": _mean(rows, "failure_score"),
        "avg_turn_count": _mean(rows, "turn_count"),
        "avg_inspect_events": _mean(rows, "phase_inspect_events"),
        "avg_edit_events": _mean(rows, "phase_edit_events"),
        "avg_verify_events": _mean(rows, "phase_verify_events"),
        "avg_recover_events": _mean(rows, "phase_recover_events"),
    }


def _deltas(baseline: dict[str, Any], intervention: dict[str, Any]) -> dict[str, float]:
    keys = set(baseline) | set(intervention)
    return {
        key: float(intervention.get(key, 0) or 0) - float(baseline.get(key, 0) or 0)
        for key in keys
        if key != "n"
    }


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    return round(mean(float(row.get(key, 0) or 0) for row in rows), 4)


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
