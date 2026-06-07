from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.research import canonical_label, load_run_manifest
from scripts.check_submission_readiness import VALID_FAILURE_TAGS


DEFAULT_RUN_DIR = Path("benchmark/hard/pilot/hard30-real")


def load_label_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def audit_manual_labels(manifest_path: Path, labels_path: Path) -> dict[str, Any]:
    records = load_run_manifest(manifest_path)
    label_rows = load_label_rows(labels_path)
    labels_by_key = {
        (str(row.get("task_id")), str(row.get("prompt_type"))): row
        for row in label_rows
    }
    failed_keys = [
        (record.task_id, record.prompt_type)
        for record in records
        if record.outcome == "failure"
    ]
    missing_rows = [
        f"{task_id}/{prompt_type}"
        for task_id, prompt_type in failed_keys
        if (task_id, prompt_type) not in labels_by_key
    ]
    unlabeled_failures = []
    missing_notes = []
    unknown_tags = set()
    tag_counts: Counter[str] = Counter()
    for task_id, prompt_type in failed_keys:
        row = labels_by_key.get((task_id, prompt_type))
        if not row:
            continue
        tags = [canonical_label(str(tag)) for tag in row.get("failure_tags", [])]
        if not tags:
            unlabeled_failures.append(f"{task_id}/{prompt_type}")
        if not str(row.get("notes", "")).strip():
            missing_notes.append(f"{task_id}/{prompt_type}")
        for tag in tags:
            if tag not in VALID_FAILURE_TAGS:
                unknown_tags.add(tag)
            else:
                tag_counts[tag] += 1
    labeled_failure_count = len(failed_keys) - len(missing_rows) - len(unlabeled_failures)
    required_process_tags = VALID_FAILURE_TAGS - {"hidden_semantic_edge_case"}
    covered_process_tags = sorted(tag for tag in required_process_tags if tag_counts.get(tag, 0))
    ok = not (missing_rows or unlabeled_failures or missing_notes or unknown_tags)
    return {
        "ok": ok,
        "manifest_path": str(manifest_path),
        "labels_path": str(labels_path),
        "run_count": len(records),
        "failure_count": len(failed_keys),
        "label_row_count": len(label_rows),
        "labeled_failure_count": labeled_failure_count,
        "missing_rows": missing_rows,
        "unlabeled_failures": unlabeled_failures,
        "missing_notes": missing_notes,
        "unknown_tags": sorted(unknown_tags),
        "tag_counts": dict(sorted(tag_counts.items())),
        "covered_process_tags": covered_process_tags,
        "process_tag_coverage_count": len(covered_process_tags),
    }


def render_audit(report: dict[str, Any]) -> str:
    lines = [
        "# Manual Label Audit",
        "",
        f"Ready: {'yes' if report['ok'] else 'no'}",
        f"Runs: {report['run_count']}",
        f"Failures: {report['failure_count']}",
        f"Label rows: {report['label_row_count']}",
        f"Labeled failures: {report['labeled_failure_count']} / {report['failure_count']}",
        f"Process tags covered: {report['process_tag_coverage_count']}",
    ]
    if report["tag_counts"]:
        lines.extend(["", "## Tag Counts", "", "| Tag | Count |", "| --- | ---: |"])
        for tag, count in report["tag_counts"].items():
            lines.append(f"| {tag} | {count} |")
    for key, title in (
        ("missing_rows", "Missing Rows"),
        ("unlabeled_failures", "Unlabeled Failures"),
        ("missing_notes", "Missing Notes"),
        ("unknown_tags", "Unknown Tags"),
    ):
        values = report[key]
        if values:
            lines.extend(["", f"## {title}", ""])
            lines.extend(f"- {value}" for value in values)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit manual failure labels for hard30 trace analysis.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    manifest_path = args.manifest or args.run_dir / "runs.jsonl"
    labels_path = args.labels or args.run_dir / "manual-labels.jsonl"
    report = audit_manual_labels(manifest_path, labels_path)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_audit(report)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
