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
    write_aggregate_outputs,
    write_label_evaluation_outputs,
    write_label_template,
    write_paper_report_outputs,
    write_runs_csv,
)


DEFAULT_RUN_DIR = Path("benchmark/hard/pilot/hard30-real")
DEFAULT_SELECTION_DIR = Path("benchmark/hard/pilot/hard30-selection")
EXPECTED_PROMPT_TYPES = ("baseline", "intervention")


def load_selected_task_ids(selection_dir: Path = DEFAULT_SELECTION_DIR) -> list[str]:
    task_id_path = selection_dir / "task_ids.txt"
    return [line.strip() for line in task_id_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def preflight(run_dir: Path, selection_dir: Path = DEFAULT_SELECTION_DIR) -> dict[str, Any]:
    manifest = run_dir / "runs.jsonl"
    selected_task_ids = load_selected_task_ids(selection_dir)
    if not manifest.exists():
        return {
            "ok": False,
            "manifest": str(manifest),
            "expected_task_count": len(selected_task_ids),
            "expected_run_records": len(selected_task_ids) * len(EXPECTED_PROMPT_TYPES),
            "run_records": 0,
            "missing_tasks": selected_task_ids,
            "missing_prompt_pairs": [
                {"task_id": task_id, "prompt_type": prompt_type}
                for task_id in selected_task_ids
                for prompt_type in EXPECTED_PROMPT_TYPES
            ],
            "duplicate_prompt_pairs": [],
            "missing_trace_paths": [],
            "unexpected_tasks": [],
        }

    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = {}
    duplicates = []
    missing_trace_paths = []
    selected_set = set(selected_task_ids)
    unexpected_tasks = sorted({str(row.get("task_id", "")) for row in rows if str(row.get("task_id", "")) not in selected_set})
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
        for task_id in selected_task_ids
        for prompt_type in EXPECTED_PROMPT_TYPES
        if (task_id, prompt_type) not in seen
    ]
    missing_tasks = [
        task_id for task_id in selected_task_ids
        if all((task_id, prompt_type) not in seen for prompt_type in EXPECTED_PROMPT_TYPES)
    ]
    expected_records = len(selected_task_ids) * len(EXPECTED_PROMPT_TYPES)
    ok = not (
        len(rows) != expected_records
        or missing_prompt_pairs
        or duplicates
        or missing_trace_paths
        or unexpected_tasks
    )
    return {
        "ok": ok,
        "manifest": str(manifest),
        "expected_task_count": len(selected_task_ids),
        "expected_run_records": expected_records,
        "run_records": len(rows),
        "missing_tasks": missing_tasks,
        "missing_prompt_pairs": missing_prompt_pairs,
        "duplicate_prompt_pairs": duplicates,
        "missing_trace_paths": missing_trace_paths,
        "unexpected_tasks": unexpected_tasks,
    }


def render_preflight(summary: dict[str, Any]) -> str:
    lines = [
        "# Hard30 Preflight",
        "",
        f"Manifest: {summary['manifest']}",
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
    write_paper_report_outputs(paper_report, paper_report_json, paper_report_md)
    written.extend([paper_report_json, paper_report_md])

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
    parser = argparse.ArgumentParser(description="Finalize hard30 pilot outputs from a completed runs.jsonl manifest.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--selection-dir", type=Path, default=DEFAULT_SELECTION_DIR)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--preflight-json", type=Path)
    args = parser.parse_args()

    summary = preflight(args.run_dir, args.selection_dir)
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
