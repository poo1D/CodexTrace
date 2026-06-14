from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_submission_readiness import VALID_FAILURE_TAGS


DEFAULT_RUN_DIR = Path("benchmark/hard/pilot/hard30-real")
REQUIRED_LABEL_FIELDS = (
    "task_id",
    "prompt_type",
    "outcome",
    "trace_path",
    "failure_score",
    "failure_tags",
    "suggested_tags",
    "notes",
)


def build_label_provenance_audit(run_dir: Path = DEFAULT_RUN_DIR) -> dict[str, Any]:
    runs = _read_jsonl(run_dir / "runs.jsonl")
    template_rows = _read_jsonl(run_dir / "labels.jsonl")
    manual_rows = _read_jsonl(run_dir / "manual-labels.jsonl")
    label_eval = _read_json(run_dir / "label-eval.json")
    report = _read_json(run_dir / "paper-report-labeled.json")

    run_by_key = {_key(row): row for row in runs}
    template_by_key = {_key(row): row for row in template_rows}
    manual_by_key = {_key(row): row for row in manual_rows}
    run_keys = set(run_by_key)
    template_keys = set(template_by_key)
    manual_keys = set(manual_by_key)

    missing_template_keys = sorted(run_keys - template_keys)
    missing_manual_keys = sorted(run_keys - manual_keys)
    extra_template_keys = sorted(template_keys - run_keys)
    extra_manual_keys = sorted(manual_keys - run_keys)
    field_coverage = [
        {
            "field": field,
            "template_present": all(field in row for row in template_rows),
            "manual_present": all(field in row for row in manual_rows),
        }
        for field in REQUIRED_LABEL_FIELDS
    ]
    for row in field_coverage:
        row["covered"] = row["template_present"] and row["manual_present"]

    outcome_mismatches = []
    trace_mismatches = []
    for key in sorted(run_keys & manual_keys):
        run = run_by_key[key]
        manual = manual_by_key[key]
        if run.get("outcome") != manual.get("outcome"):
            outcome_mismatches.append(_render_key(key))
        if run.get("trace_path") != manual.get("trace_path"):
            trace_mismatches.append(_render_key(key))

    unknown_tags = sorted({
        str(tag)
        for row in manual_rows
        for tag in row.get("failure_tags", [])
        if str(tag) not in VALID_FAILURE_TAGS
    })
    failure_rows = [row for row in manual_rows if row.get("outcome") == "failure"]
    labeled_failure_rows = [row for row in failure_rows if row.get("failure_tags")]
    failure_notes = [row for row in failure_rows if str(row.get("notes", "")).strip()]
    tag_counts = Counter(str(tag) for row in manual_rows for tag in row.get("failure_tags", []))
    outcome_counts = Counter(str(row.get("outcome", "")) for row in manual_rows)

    label_eval_summary = label_eval.get("summary", {})
    report_eval_summary = (report.get("detector_evaluation") or {}).get("summary", {})
    eval_summary_matches = {
        key: label_eval_summary.get(key) == report_eval_summary.get(key)
        for key in ("labels", "micro_precision", "micro_recall", "micro_f1", "macro_f1")
    }
    eval_labels_match = (
        set((label_eval.get("labels") or {}).keys())
        == set(((report.get("detector_evaluation") or {}).get("labels") or {}).keys())
    )

    ready = (
        len(runs) == 60
        and len(template_rows) == 60
        and len(manual_rows) == 60
        and not missing_template_keys
        and not missing_manual_keys
        and not extra_template_keys
        and not extra_manual_keys
        and not outcome_mismatches
        and not trace_mismatches
        and not unknown_tags
        and len(failure_rows) == 30
        and len(labeled_failure_rows) == 30
        and len(failure_notes) == 30
        and all(row["covered"] for row in field_coverage)
        and all(eval_summary_matches.values())
        and eval_labels_match
    )
    return {
        "summary": {
            "ready": ready,
            "run_dir": str(run_dir),
            "run_count": len(runs),
            "template_label_count": len(template_rows),
            "manual_label_count": len(manual_rows),
            "failure_label_count": len(failure_rows),
            "labeled_failure_count": len(labeled_failure_rows),
            "failure_note_count": len(failure_notes),
            "field_count": len(REQUIRED_LABEL_FIELDS),
            "covered_field_count": sum(1 for row in field_coverage if row["covered"]),
            "eval_summary_match_count": sum(1 for ok in eval_summary_matches.values() if ok),
            "eval_summary_key_count": len(eval_summary_matches),
            "eval_labels_match": eval_labels_match,
        },
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "tag_counts": dict(sorted(tag_counts.items())),
        "field_coverage": field_coverage,
        "eval_summary_matches": eval_summary_matches,
        "missing_template_keys": [_render_key(key) for key in missing_template_keys],
        "missing_manual_keys": [_render_key(key) for key in missing_manual_keys],
        "extra_template_keys": [_render_key(key) for key in extra_template_keys],
        "extra_manual_keys": [_render_key(key) for key in extra_manual_keys],
        "outcome_mismatches": outcome_mismatches,
        "trace_mismatches": trace_mismatches,
        "unknown_tags": unknown_tags,
    }


def render_label_provenance_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Label Provenance Audit",
        "",
        "This generated audit checks that hard30 label templates, manual labels, detector-label evaluation, and the labeled paper report agree on row identity, schema fields, outcomes, trace paths, and evaluation summaries.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Run rows: {summary['run_count']} / 60",
        f"- Template label rows: {summary['template_label_count']} / 60",
        f"- Manual label rows: {summary['manual_label_count']} / 60",
        f"- Failure rows with labels: {summary['labeled_failure_count']} / {summary['failure_label_count']}",
        f"- Failure rows with notes: {summary['failure_note_count']} / {summary['failure_label_count']}",
        f"- Label fields covered: {summary['covered_field_count']} / {summary['field_count']}",
        f"- Label-eval summary matches paper report: {summary['eval_summary_match_count']} / {summary['eval_summary_key_count']}",
        f"- Label set matches paper report: {'yes' if summary['eval_labels_match'] else 'no'}",
        f"- Run directory: `{summary['run_dir']}`",
        "",
        "## Manual Label Tags",
        "",
        "| Tag | Count |",
        "| --- | ---: |",
    ]
    for tag, count in result["tag_counts"].items():
        lines.append(f"| `{tag}` | {count} |")

    lines.extend([
        "",
        "## Label Schema Fields",
        "",
        "| Field | Template | Manual | Covered |",
        "| --- | --- | --- | --- |",
    ])
    for row in result["field_coverage"]:
        lines.append(
            f"| `{row['field']}` | {'yes' if row['template_present'] else 'no'} | "
            f"{'yes' if row['manual_present'] else 'no'} | {'yes' if row['covered'] else 'no'} |"
        )

    lines.extend([
        "",
        "## Consistency Checks",
        "",
        f"- Missing template keys: {len(result['missing_template_keys'])}",
        f"- Missing manual keys: {len(result['missing_manual_keys'])}",
        f"- Extra template keys: {len(result['extra_template_keys'])}",
        f"- Extra manual keys: {len(result['extra_manual_keys'])}",
        f"- Outcome mismatches: {len(result['outcome_mismatches'])}",
        f"- Trace path mismatches: {len(result['trace_mismatches'])}",
        f"- Unknown tags: {len(result['unknown_tags'])}",
        "",
        "Interpretation: this audit proves label-file provenance and evaluation-file consistency for the committed hard30 artifact. It does not prove inter-annotator agreement or relabel the traces.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_label_provenance_markdown(result), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("task_id", "")), str(row.get("prompt_type", ""))


def _render_key(key: tuple[str, str]) -> str:
    return f"{key[0]}/{key[1]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit hard30 label provenance and evaluation consistency.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_label_provenance_audit(args.run_dir)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_label_provenance_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
