from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.diagnose import diagnose
from codex_trace.parser import parse_jsonl


DEFAULT_TASKS = Path("benchmark/hard/pilot/hard30-selection/tasks.jsonl")
DEFAULT_RUNS = Path("benchmark/hard/pilot/hard30-real/runs.jsonl")
DEFAULT_LABELS = Path("benchmark/hard/pilot/hard30-real/manual-labels.jsonl")
DEFAULT_RUN_DIR = Path("benchmark/hard/pilot/hard30-real")
PROMPT_TYPES = ("baseline", "intervention")


def build_benchmark_trace_artifact_audit(
    tasks_path: Path = DEFAULT_TASKS,
    runs_path: Path = DEFAULT_RUNS,
    labels_path: Path = DEFAULT_LABELS,
    run_dir: Path = DEFAULT_RUN_DIR,
) -> dict[str, Any]:
    tasks = _read_jsonl(tasks_path)
    runs = _read_jsonl(runs_path)
    labels = _read_jsonl(labels_path)

    task_ids = [str(row.get("task_id", "")) for row in tasks]
    task_id_set = set(task_ids)
    run_keys = [(str(row.get("task_id", "")), str(row.get("prompt_type", ""))) for row in runs]
    label_keys = [(str(row.get("task_id", "")), str(row.get("prompt_type", ""))) for row in labels]
    expected_keys = {(task_id, prompt_type) for task_id in task_id_set for prompt_type in PROMPT_TYPES}
    run_key_set = set(run_keys)
    label_key_set = set(label_keys)

    trace_rows = []
    for row in runs:
        trace_path = run_dir / str(row.get("trace_path", ""))
        exists = trace_path.exists()
        event_lines = _count_nonempty_lines(trace_path) if exists else 0
        parsed_events = 0
        diagnosis_outcome = ""
        parse_error = ""
        if exists:
            try:
                trace = parse_jsonl(trace_path)
                parsed_events = len(trace.events)
                diagnosis_outcome = diagnose(trace).outcome
            except (OSError, json.JSONDecodeError, ValueError) as error:
                parse_error = str(error)
        run_sidecar_dir = trace_path.parent
        prompt_path = run_sidecar_dir / "prompt.md"
        success_check_path = run_sidecar_dir / "success_check.txt"
        stderr_path = run_sidecar_dir / "codex.stderr"
        trace_rows.append({
            "task_id": str(row.get("task_id", "")),
            "prompt_type": str(row.get("prompt_type", "")),
            "trace_path": str(row.get("trace_path", "")),
            "exists": exists,
            "event_lines": event_lines,
            "nonempty": event_lines > 0,
            "parseable": parsed_events > 0 and not parse_error,
            "parsed_events": parsed_events,
            "diagnosis_outcome": diagnosis_outcome,
            "parse_error": parse_error,
            "prompt_exists": prompt_path.exists(),
            "success_check_exists": success_check_path.exists(),
            "stderr_exists": stderr_path.exists(),
            "sidecars_complete": prompt_path.exists() and success_check_path.exists() and stderr_path.exists(),
        })

    outcome_rows = [
        row for row in runs
        if row.get("outcome") in {"success", "failure"}
        and row.get("success_check_exit_code") is not None
        and row.get("codex_exit_code") is not None
    ]
    labeled_failure_rows = [
        row for row in labels
        if row.get("outcome") == "failure" and row.get("failure_tags")
    ]
    category_counts = Counter(str(row.get("category", "")) for row in tasks)
    outcome_counts = Counter(str(row.get("outcome", "")) for row in runs)

    paired_task_ids = sorted(
        task_id for task_id in task_id_set
        if all((task_id, prompt_type) in run_key_set for prompt_type in PROMPT_TYPES)
    )
    missing_run_keys = sorted(expected_keys - run_key_set)
    extra_run_keys = sorted(run_key_set - expected_keys)
    missing_label_keys = sorted(run_key_set - label_key_set)
    extra_label_keys = sorted(label_key_set - run_key_set)

    task_rows_ready = (
        len(tasks) == 30
        and len(task_id_set) == 30
        and all(row.get("instruction") and row.get("category") and row.get("success_check") for row in tasks)
    )
    run_rows_ready = (
        len(runs) == 60
        and len(paired_task_ids) == 30
        and not missing_run_keys
        and not extra_run_keys
        and len(outcome_rows) == 60
    )
    trace_rows_ready = len(trace_rows) == 60 and all(row["nonempty"] for row in trace_rows)
    trace_parse_ready = len(trace_rows) == 60 and all(row["parseable"] for row in trace_rows)
    trace_sidecars_ready = len(trace_rows) == 60 and all(row["sidecars_complete"] for row in trace_rows)
    label_rows_ready = (
        len(labels) == 60
        and not missing_label_keys
        and not extra_label_keys
        and all(row.get("outcome") != "failure" or row.get("failure_tags") for row in labels)
    )

    return {
        "summary": {
            "ready": task_rows_ready and run_rows_ready and trace_rows_ready and trace_parse_ready and trace_sidecars_ready and label_rows_ready,
            "task_count": len(tasks),
            "unique_task_count": len(task_id_set),
            "run_count": len(runs),
            "paired_task_count": len(paired_task_ids),
            "trace_count": len(trace_rows),
            "nonempty_trace_count": sum(1 for row in trace_rows if row["nonempty"]),
            "trace_event_lines": sum(row["event_lines"] for row in trace_rows),
            "parseable_trace_count": sum(1 for row in trace_rows if row["parseable"]),
            "parsed_trace_events": sum(row["parsed_events"] for row in trace_rows),
            "diagnosed_trace_count": sum(1 for row in trace_rows if row["diagnosis_outcome"]),
            "trace_sidecar_count": sum(1 for row in trace_rows if row["sidecars_complete"]),
            "label_count": len(labels),
            "labeled_failure_count": len(labeled_failure_rows),
            "outcome_rows_with_grader_count": len(outcome_rows),
            "task_rows_ready": task_rows_ready,
            "run_rows_ready": run_rows_ready,
            "trace_rows_ready": trace_rows_ready,
            "trace_parse_ready": trace_parse_ready,
            "trace_sidecars_ready": trace_sidecars_ready,
            "label_rows_ready": label_rows_ready,
            "tasks_path": str(tasks_path),
            "runs_path": str(runs_path),
            "labels_path": str(labels_path),
            "run_dir": str(run_dir),
        },
        "category_counts": dict(sorted(category_counts.items())),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "missing_run_keys": _render_keys(missing_run_keys),
        "extra_run_keys": _render_keys(extra_run_keys),
        "missing_label_keys": _render_keys(missing_label_keys),
        "extra_label_keys": _render_keys(extra_label_keys),
        "trace_rows": trace_rows,
    }


def render_benchmark_trace_artifact_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Benchmark Trace Artifact Audit",
        "",
        "This generated audit checks that the paper-facing hard30 benchmark has paired baseline/intervention Codex JSONL traces, task metadata, grader outcomes, and manual labels.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Tasks covered: {summary['task_count']} / 30",
        f"- Unique task IDs: {summary['unique_task_count']} / 30",
        f"- Run rows covered: {summary['run_count']} / 60",
        f"- Paired baseline/intervention tasks: {summary['paired_task_count']} / 30",
        f"- Codex JSONL traces covered: {summary['nonempty_trace_count']} / {summary['trace_count']}",
        f"- Trace event lines: {summary['trace_event_lines']}",
        f"- Parseable traces: {summary['parseable_trace_count']} / {summary['trace_count']}",
        f"- Parsed trace events: {summary['parsed_trace_events']}",
        f"- Diagnosable traces: {summary['diagnosed_trace_count']} / {summary['trace_count']}",
        f"- Trace sidecar bundles: {summary['trace_sidecar_count']} / {summary['trace_count']}",
        f"- Outcome rows with grader results: {summary['outcome_rows_with_grader_count']} / 60",
        f"- Manual label rows: {summary['label_count']} / 60",
        f"- Labeled failure rows: {summary['labeled_failure_count']}",
        f"- Tasks manifest: `{summary['tasks_path']}`",
        f"- Run manifest: `{summary['runs_path']}`",
        f"- Manual labels: `{summary['labels_path']}`",
        "",
        "## Category Counts",
        "",
        "| Category | Tasks |",
        "| --- | ---: |",
    ]
    for category, count in result["category_counts"].items():
        lines.append(f"| `{category}` | {count} |")

    lines.extend([
        "",
        "## Outcome Counts",
        "",
        "| Outcome | Runs |",
        "| --- | ---: |",
    ])
    for outcome, count in result["outcome_counts"].items():
        lines.append(f"| `{outcome}` | {count} |")

    lines.extend([
        "",
        "## Consistency Checks",
        "",
        f"- Missing run keys: {len(result['missing_run_keys'])}",
        f"- Extra run keys: {len(result['extra_run_keys'])}",
        f"- Missing label keys: {len(result['missing_label_keys'])}",
        f"- Extra label keys: {len(result['extra_label_keys'])}",
        "",
        "Interpretation: this audit proves the committed hard30 paper artifact has paired task/run/trace/label records. It does not rerun Codex or hidden graders.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_benchmark_trace_artifact_markdown(result), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _count_nonempty_lines(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _render_keys(keys: list[tuple[str, str]]) -> list[str]:
    return [f"{task_id}/{prompt_type}" for task_id, prompt_type in keys]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the hard30 benchmark trace artifact.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_benchmark_trace_artifact_audit(args.tasks, args.runs, args.labels, args.run_dir)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_benchmark_trace_artifact_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
