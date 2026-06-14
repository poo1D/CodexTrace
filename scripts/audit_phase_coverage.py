from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, get_args

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.research import aggregate_runs
from codex_trace.schema import EventPhase


DEFAULT_MANIFEST = Path("benchmark/hard/pilot/hard30-real/runs.jsonl")
DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_RESULTS_SUMMARY = Path("docs/results_summary.json")

EXPECTED_PHASES = (
    "setup",
    "inspect",
    "edit",
    "verify",
    "recover",
    "complete",
    "other",
)


def build_phase_coverage_audit(
    manifest_path: Path = DEFAULT_MANIFEST,
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    results_summary_path: Path = DEFAULT_RESULTS_SUMMARY,
) -> dict[str, Any]:
    aggregate = aggregate_runs(manifest_path)
    run_keys = set().union(*(row.keys() for row in aggregate["runs"]))
    paper_text = paper_draft_path.read_text(encoding="utf-8")
    results = json.loads(results_summary_path.read_text(encoding="utf-8"))
    signal_names = {
        row.get("signal")
        for key in (
            "hard30_signal_by_outcome",
            "hard30_repetitive_exploration_top_signals",
            "full30_sandbox_permission_top_signals",
        )
        for row in results.get(key, [])
    }

    schema_phases = set(get_args(EventPhase))
    rows = []
    for phase in EXPECTED_PHASES:
        run_key = f"phase_{phase}_events"
        rows.append({
            "phase": phase,
            "schema": phase in schema_phases,
            "paper_draft": phase in paper_text,
            "run_key": run_key,
            "run_level": run_key in run_keys,
            "rq4_signal": run_key in signal_names,
            "covered": phase in schema_phases and phase in paper_text and run_key in run_keys,
        })

    core_signal_rows = [row for row in rows if row["phase"] in {"inspect", "edit", "verify", "recover"}]
    return {
        "summary": {
            "ready": all(row["covered"] for row in rows) and all(row["rq4_signal"] for row in core_signal_rows),
            "phase_count": len(EXPECTED_PHASES),
            "covered_phase_count": sum(1 for row in rows if row["covered"]),
            "rq4_core_signal_count": sum(1 for row in core_signal_rows if row["rq4_signal"]),
            "rq4_core_signal_expected": len(core_signal_rows),
            "manifest": str(manifest_path),
            "paper_draft": str(paper_draft_path),
            "results_summary": str(results_summary_path),
        },
        "phases": rows,
    }


def render_phase_coverage_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Phase Coverage Audit",
        "",
        "This generated audit checks that phase segmentation is represented in the schema, paper draft, hard30 run rows, and RQ4 signal outputs.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Phases covered: {summary['covered_phase_count']} / {summary['phase_count']}",
        f"- RQ4 core phase signals: {summary['rq4_core_signal_count']} / {summary['rq4_core_signal_expected']}",
        f"- Manifest checked: `{summary['manifest']}`",
        f"- Paper draft: `{summary['paper_draft']}`",
        f"- Results summary: `{summary['results_summary']}`",
        "",
        "## Phase Coverage",
        "",
        "| Phase | Schema | Paper draft | Run key | RQ4 signal | Covered |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["phases"]:
        lines.append(
            f"| `{row['phase']}` | {'yes' if row['schema'] else 'no'} | "
            f"{'yes' if row['paper_draft'] else 'no'} | `{row['run_key']}` "
            f"{'yes' if row['run_level'] else 'no'} | {'yes' if row['rq4_signal'] else 'no'} | "
            f"{'yes' if row['covered'] else 'no'} |"
        )
    lines.extend([
        "",
        "Interpretation: all phases must exist in the schema, paper draft, and run-level hard30 rows. RQ4 is required to expose the core process phases inspect, edit, verify, and recover as explanatory signals; setup, complete, and other remain run-level accounting fields.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_phase_coverage_markdown(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit phase segmentation coverage for CodexTrace paper artifacts.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--results-summary", type=Path, default=DEFAULT_RESULTS_SUMMARY)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_phase_coverage_audit(args.manifest, args.paper_draft, args.results_summary)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_phase_coverage_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
