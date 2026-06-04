from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from .diagnose import diagnose
from .parser import parse_jsonl
from .schema import Diagnosis, Trace


PROMPT_TYPES = ("baseline", "intervention")


@dataclass
class BenchmarkTask:
    task_id: str
    category: str
    instruction: str
    success_check: str
    repo_hint: str = ""


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
        ))
    return tasks


def load_run_manifest(path: str | Path) -> list[RunRecord]:
    manifest_path = Path(path)
    records = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        records.append(RunRecord(
            task_id=str(item["task_id"]),
            prompt_type=str(item["prompt_type"]),
            trace_path=(manifest_path.parent / str(item["trace_path"])).resolve(),
            outcome=str(item.get("outcome", "unknown")),
        ))
    return records


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
        "avg_command_failures",
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
        "command_failure_count",
        "token_usage",
        "failure_score",
        "turn_count",
        "time_to_first_edit",
        "time_to_first_test",
        "finding_codes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result["runs"]:
            serialized = dict(row)
            serialized["finding_codes"] = ";".join(row["finding_codes"])
            writer.writerow({key: serialized.get(key, "") for key in fieldnames})


def _run_metrics(record: RunRecord, trace: Trace, diagnosis: Diagnosis) -> dict[str, Any]:
    metrics = diagnosis.metrics
    finding_codes = [finding.code for finding in diagnosis.findings]
    return {
        "task_id": record.task_id,
        "prompt_type": record.prompt_type,
        "trace_path": str(record.trace_path),
        "outcome": record.outcome,
        "success": 1 if record.outcome == "success" else 0,
        "verification_rate": 1 if metrics.get("post_edit_verification_commands", 0) > 0 else 0,
        "unresolved_error": 1 if "command_failure_unhandled" in finding_codes else 0,
        "repeated_tool_call_count": _repeated_tool_call_count(trace),
        "command_failure_count": metrics.get("failed_commands", 0),
        "token_usage": metrics.get("input_tokens", 0) + metrics.get("output_tokens", 0),
        "failure_score": diagnosis.failure_score,
        "turn_count": sum(event.kind == "turn" and event.status == "completed" for event in trace.events),
        "time_to_first_edit": _index_of_first(trace, "file_change"),
        "time_to_first_test": _index_of_first_verification(trace),
        "finding_codes": finding_codes,
    }


def _summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        "success_rate": _mean(rows, "success"),
        "verification_rate": _mean(rows, "verification_rate"),
        "unresolved_error_rate": _mean(rows, "unresolved_error"),
        "avg_repeated_tool_calls": _mean(rows, "repeated_tool_call_count"),
        "avg_command_failures": _mean(rows, "command_failure_count"),
        "avg_token_usage": _mean(rows, "token_usage"),
        "avg_failure_score": _mean(rows, "failure_score"),
        "avg_turn_count": _mean(rows, "turn_count"),
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


def _index_of_first(trace: Trace, kind: str) -> int | None:
    for index, event in enumerate(trace.events):
        if event.kind == kind:
            return index
    return None


def _index_of_first_verification(trace: Trace) -> int | None:
    verification_words = ("pytest", "npm test", "npm run test", "ruff", "mypy", "tsc", "build")
    for index, event in enumerate(trace.events):
        command = (event.command or "").lower()
        if event.kind == "command" and any(word in command for word in verification_words):
            return index
    return None
