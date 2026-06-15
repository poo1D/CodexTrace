from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.research import aggregate_runs, render_aggregate_markdown, write_runs_csv


DEFAULT_MANIFEST = Path("benchmark/hard/pilot/hard30-real/runs.jsonl")
DEFAULT_MANIFESTS = (
    Path("benchmark/pilot/full30-real/runs.jsonl"),
    Path("benchmark/hard/pilot/hard10-real/runs.jsonl"),
    Path("benchmark/hard/pilot/hard30-real/runs.jsonl"),
    Path("benchmark/process-stress/pilot/full-real/runs.jsonl"),
    Path("benchmark/verification-lift/pilot/full-real/runs.jsonl"),
    Path("benchmark/verification-lift-v2/pilot/full-real/runs.jsonl"),
    Path("benchmark/verification-ablation/pilot/full-real/runs.jsonl"),
)
EXPECTED_METRICS = (
    "success_rate",
    "verification_rate",
    "unresolved_error_rate",
    "repeated_tool_call_count",
    "retry_count",
    "turn_count",
    "token_usage",
    "command_failure_count",
    "time_to_first_edit",
    "time_to_first_test",
    "failure_score",
)
SUMMARY_KEYS = {
    "success_rate": "success_rate",
    "verification_rate": "verification_rate",
    "unresolved_error_rate": "unresolved_error_rate",
    "repeated_tool_call_count": "avg_repeated_tool_calls",
    "retry_count": "avg_retry_count",
    "turn_count": "avg_turn_count",
    "token_usage": "avg_token_usage",
    "command_failure_count": "avg_command_failures",
    "time_to_first_edit": "avg_time_to_first_edit",
    "time_to_first_test": "avg_time_to_first_test",
    "failure_score": "avg_failure_score",
}
RUN_KEYS = {
    "success_rate": "success",
    "unresolved_error_rate": "unresolved_error",
}


def build_metric_coverage_audit(manifest_path: Path | Iterable[Path] | None = None) -> dict[str, Any]:
    manifest_paths = _manifest_paths(manifest_path)
    manifest_rows = [_build_manifest_metric_coverage(path) for path in manifest_paths]
    rows = [
        row
        for manifest in manifest_rows
        for row in manifest["metrics"]
    ]
    ready = all(manifest["ready"] for manifest in manifest_rows)
    covered_metric_names = {
        row["metric"]
        for row in rows
        if all(candidate["covered"] for candidate in rows if candidate["metric"] == row["metric"])
    }
    return {
        "summary": {
            "ready": ready,
            "manifest_count": len(manifest_rows),
            "ready_manifest_count": sum(1 for row in manifest_rows if row["ready"]),
            "expected_metric_count": len(EXPECTED_METRICS),
            "covered_metric_count": len(covered_metric_names),
            "coverage_cell_count": sum(1 for row in rows if row["covered"]),
            "expected_coverage_cell_count": len(rows),
        },
        "manifests": manifest_rows,
        "metrics": rows,
    }


def _build_manifest_metric_coverage(manifest_path: Path) -> dict[str, Any]:
    aggregate = aggregate_runs(manifest_path)
    run_keys = set().union(*(row.keys() for row in aggregate["runs"]))
    summary_keys = set()
    for prompt_summary in aggregate["summary"].values():
        summary_keys.update(prompt_summary.keys())
    markdown = render_aggregate_markdown(aggregate)

    rows = []
    for metric in EXPECTED_METRICS:
        run_key = RUN_KEYS.get(metric, metric)
        summary_key = SUMMARY_KEYS[metric]
        row = {
            "manifest": str(manifest_path),
            "metric": metric,
            "run_key": run_key,
            "summary_key": summary_key,
            "run_level": run_key in run_keys,
            "summary_level": summary_key in summary_keys,
            "aggregate_markdown": summary_key in markdown,
            "csv_field": run_key in _runs_csv_fieldnames(aggregate),
        }
        row["covered"] = all(row[key] for key in ("run_level", "summary_level", "aggregate_markdown", "csv_field"))
        rows.append(row)

    ready = all(row["covered"] for row in rows)
    return {
        "manifest": str(manifest_path),
        "ready": ready,
        "covered_metric_count": sum(1 for row in rows if row["covered"]),
        "expected_metric_count": len(EXPECTED_METRICS),
        "metrics": rows,
    }


def render_metric_coverage_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Metric Coverage Audit",
        "",
        "This generated audit checks that the metrics named in the experiment design are collected at run level, summarized for baseline/intervention comparison, emitted to CSV, and visible in generated aggregate Markdown.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Manifests checked: {summary['ready_manifest_count']} / {summary['manifest_count']}",
        f"- Metrics covered: {summary['covered_metric_count']} / {summary['expected_metric_count']}",
        f"- Coverage cells covered: {summary['coverage_cell_count']} / {summary['expected_coverage_cell_count']}",
        "",
        "## Manifests",
        "",
        "| Manifest | Metrics covered | Ready |",
        "| --- | ---: | --- |",
    ]
    for manifest in result["manifests"]:
        lines.append(
            f"| `{manifest['manifest']}` | {manifest['covered_metric_count']} / {manifest['expected_metric_count']} | "
            f"{'yes' if manifest['ready'] else 'no'} |"
        )
    lines.extend([
        "",
        "## Coverage",
        "",
        "| Manifest | Metric | Run key | Summary key | CSV | Markdown | Covered |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in result["metrics"]:
        lines.append(
            f"| `{row['manifest']}` | {row['metric']} | `{row['run_key']}` {'yes' if row['run_level'] else 'no'} | `{row['summary_key']}` "
            f"{'yes' if row['summary_level'] else 'no'} | {'yes' if row['csv_field'] else 'no'} | "
            f"{'yes' if row['aggregate_markdown'] else 'no'} | {'yes' if row['covered'] else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_metric_coverage_audit_markdown(result), encoding="utf-8")


def _runs_csv_fieldnames(aggregate: dict[str, Any]) -> set[str]:
    scratch = Path("/tmp/codextrace-metric-coverage-runs.csv")
    write_runs_csv(aggregate, scratch)
    header = scratch.read_text(encoding="utf-8").splitlines()[0]
    return set(header.split(","))


def _manifest_paths(manifest_path: Path | Iterable[Path] | None) -> tuple[Path, ...]:
    if manifest_path is None:
        return DEFAULT_MANIFESTS
    if isinstance(manifest_path, Path):
        return (manifest_path,)
    return tuple(manifest_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit coverage for the experiment-design metrics.")
    parser.add_argument("--manifest", action="append", type=Path, help="Run manifest to audit. Defaults to all paper-facing pilot manifests.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    manifests = tuple(args.manifest) if args.manifest else None
    result = build_metric_coverage_audit(manifests)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_metric_coverage_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
