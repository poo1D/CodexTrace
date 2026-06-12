from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.research import (
    aggregate_runs,
    build_paper_report,
    evaluate_detector_labels,
    generate_label_template,
    load_tasks,
    write_aggregate_outputs,
    write_label_evaluation_outputs,
    write_label_template,
    write_paired_task_deltas_csv,
    write_paired_task_summary_csv,
    write_paper_report_outputs,
    write_runs_csv,
)


DEFAULT_RUN_DIR = Path("benchmark/verification-lift-v2/pilot/full-real")
DEFAULT_TASKS = Path("benchmark/verification-lift-v2/tasks.jsonl")
EXPECTED_PROMPT_TYPES = ("baseline", "intervention")


def preflight(run_dir: Path, tasks_path: Path = DEFAULT_TASKS) -> dict[str, Any]:
    manifest = run_dir / "runs.jsonl"
    task_ids = [task.task_id for task in load_tasks(tasks_path)]
    if not manifest.exists():
        return _preflight_result(
            manifest=manifest,
            tasks_path=tasks_path,
            task_ids=task_ids,
            rows=[],
            missing_prompt_pairs=[
                {"task_id": task_id, "prompt_type": prompt_type}
                for task_id in task_ids
                for prompt_type in EXPECTED_PROMPT_TYPES
            ],
            missing_trace_paths=[],
            duplicate_prompt_pairs=[],
            unexpected_tasks=[],
        )

    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = {}
    duplicates = []
    missing_trace_paths = []
    expected_set = set(task_ids)
    unexpected_tasks = sorted({str(row.get("task_id", "")) for row in rows if str(row.get("task_id", "")) not in expected_set})
    for row in rows:
        key = (str(row.get("task_id", "")), str(row.get("prompt_type", "")))
        if key in seen:
            duplicates.append({"task_id": key[0], "prompt_type": key[1]})
        seen[key] = row
        trace_path = str(row.get("trace_path", ""))
        if trace_path and not (manifest.parent / trace_path).exists():
            missing_trace_paths.append({"task_id": key[0], "prompt_type": key[1], "trace_path": trace_path})

    missing_prompt_pairs = [
        {"task_id": task_id, "prompt_type": prompt_type}
        for task_id in task_ids
        for prompt_type in EXPECTED_PROMPT_TYPES
        if (task_id, prompt_type) not in seen
    ]
    return _preflight_result(
        manifest=manifest,
        tasks_path=tasks_path,
        task_ids=task_ids,
        rows=rows,
        missing_prompt_pairs=missing_prompt_pairs,
        missing_trace_paths=missing_trace_paths,
        duplicate_prompt_pairs=duplicates,
        unexpected_tasks=unexpected_tasks,
    )


def _preflight_result(
    manifest: Path,
    tasks_path: Path,
    task_ids: list[str],
    rows: list[dict[str, Any]],
    missing_prompt_pairs: list[dict[str, str]],
    missing_trace_paths: list[dict[str, str]],
    duplicate_prompt_pairs: list[dict[str, str]],
    unexpected_tasks: list[str],
) -> dict[str, Any]:
    expected_records = len(task_ids) * len(EXPECTED_PROMPT_TYPES)
    missing_tasks = [
        task_id for task_id in task_ids
        if all(row.get("task_id") != task_id for row in rows)
    ]
    ok = not (
        len(rows) != expected_records
        or missing_prompt_pairs
        or duplicate_prompt_pairs
        or missing_trace_paths
        or unexpected_tasks
    )
    return {
        "ok": ok,
        "manifest": str(manifest),
        "tasks_path": str(tasks_path),
        "expected_task_count": len(task_ids),
        "expected_run_records": expected_records,
        "run_records": len(rows),
        "missing_tasks": missing_tasks,
        "missing_prompt_pairs": missing_prompt_pairs,
        "duplicate_prompt_pairs": duplicate_prompt_pairs,
        "missing_trace_paths": missing_trace_paths,
        "unexpected_tasks": unexpected_tasks,
    }


def render_preflight(summary: dict[str, Any]) -> str:
    lines = [
        "# Benchmark Pilot Preflight",
        "",
        f"Manifest: {summary['manifest']}",
        f"Tasks: {summary['tasks_path']}",
        f"Run records: {summary['run_records']} / {summary['expected_run_records']}",
        f"Expected tasks: {summary['expected_task_count']}",
        f"Ready to finalize: {'yes' if summary['ok'] else 'no'}",
    ]
    if summary["missing_tasks"]:
        lines.extend(["", f"Missing tasks: {', '.join(summary['missing_tasks'])}"])
    if summary["missing_prompt_pairs"]:
        rendered = ", ".join(f"{row['task_id']}/{row['prompt_type']}" for row in summary["missing_prompt_pairs"])
        lines.extend(["", f"Missing prompt pairs: {rendered}"])
    if summary["duplicate_prompt_pairs"]:
        rendered = ", ".join(f"{row['task_id']}/{row['prompt_type']}" for row in summary["duplicate_prompt_pairs"])
        lines.extend(["", f"Duplicate prompt pairs: {rendered}"])
    if summary["missing_trace_paths"]:
        rendered = ", ".join(
            f"{row['task_id']}/{row['prompt_type']} -> {row['trace_path']}"
            for row in summary["missing_trace_paths"]
        )
        lines.extend(["", f"Missing trace files: {rendered}"])
    if summary["unexpected_tasks"]:
        lines.extend(["", f"Unexpected tasks: {', '.join(summary['unexpected_tasks'])}"])
    return "\n".join(lines) + "\n"


def finalize(run_dir: Path) -> list[Path]:
    manifest = run_dir / "runs.jsonl"
    if not manifest.exists():
        raise FileNotFoundError(f"Run manifest not found: {manifest}")

    written = []
    aggregate = aggregate_runs(manifest)
    aggregate_json = run_dir / "aggregate.json"
    aggregate_md = run_dir / "aggregate.md"
    runs_csv = run_dir / "runs.csv"
    write_aggregate_outputs(aggregate, aggregate_json, aggregate_md)
    write_runs_csv(aggregate, runs_csv)
    written.extend([aggregate_json, aggregate_md, runs_csv])

    labels_template = run_dir / "labels.jsonl"
    write_label_template(generate_label_template(manifest, include_predictions=True), labels_template)
    written.append(labels_template)

    paper_report = build_paper_report(manifest)
    paper_report_json = run_dir / "paper-report.json"
    paper_report_md = run_dir / "paper-report.md"
    paired_csv = run_dir / "paired-task-deltas.csv"
    paired_summary_csv = run_dir / "paired-task-summary.csv"
    write_paper_report_outputs(paper_report, paper_report_json, paper_report_md)
    write_paired_task_deltas_csv(paper_report, paired_csv)
    write_paired_task_summary_csv(paper_report, paired_summary_csv)
    written.extend([paper_report_json, paper_report_md, paired_csv, paired_summary_csv])

    manual_labels = run_dir / "manual-labels.jsonl"
    if manual_labels.exists():
        labeled_report = build_paper_report(manifest, labels_path=manual_labels)
        labeled_json = run_dir / "paper-report-labeled.json"
        labeled_md = run_dir / "paper-report-labeled.md"
        write_paper_report_outputs(labeled_report, labeled_json, labeled_md)
        label_eval = evaluate_detector_labels(manifest, manual_labels)
        label_eval_json = run_dir / "label-eval.json"
        label_eval_md = run_dir / "label-eval.md"
        write_label_evaluation_outputs(label_eval, label_eval_json, label_eval_md)
        written.extend([labeled_json, labeled_md, label_eval_json, label_eval_md])

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight and finalize a completed CodexTrace benchmark pilot.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--preflight-json", type=Path)
    args = parser.parse_args()

    summary = preflight(args.run_dir, args.tasks)
    print(render_preflight(summary), end="")
    if args.preflight_json:
        args.preflight_json.parent.mkdir(parents=True, exist_ok=True)
        args.preflight_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.preflight_only:
        return 0 if summary["ok"] else 1
    if not summary["ok"]:
        return 1

    written = finalize(args.run_dir)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
