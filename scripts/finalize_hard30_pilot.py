from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    args = parser.parse_args()

    written = finalize(args.run_dir)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
