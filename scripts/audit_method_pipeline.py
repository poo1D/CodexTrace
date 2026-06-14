from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.cli import main as cli_main


DEFAULT_PAPER = Path("docs/paper_draft.md")
DEFAULT_CLI = Path("codex_trace/cli.py")
DEFAULT_PARSER = Path("codex_trace/parser.py")
DEFAULT_DIAGNOSE = Path("codex_trace/diagnose.py")
DEFAULT_RESEARCH = Path("codex_trace/research.py")


PIPELINE_STAGES = (
    {
        "id": "jsonl_event_parser",
        "paper_phrase": "JSONL event parser",
        "source_path": DEFAULT_PARSER,
        "source_phrases": ("def parse_jsonl", "def parse_lines", "_event_from_payload"),
    },
    {
        "id": "normalized_trace_schema",
        "paper_phrase": "normalized trace schema",
        "source_path": Path("codex_trace/schema.py"),
        "source_phrases": ("class TraceEvent", "class Trace", "to_dict"),
    },
    {
        "id": "phase_segmentation",
        "paper_phrase": "phase segmentation",
        "source_path": DEFAULT_PARSER,
        "source_phrases": ("def assign_phases", "def _infer_event_phase", "is_verification_command"),
    },
    {
        "id": "failure_pattern_detector",
        "paper_phrase": "failure pattern detector",
        "source_path": DEFAULT_DIAGNOSE,
        "source_phrases": ("def diagnose", "verification_gap", "command_failure_unhandled"),
    },
    {
        "id": "diagnosis_report",
        "paper_phrase": "diagnosis report",
        "source_path": Path("codex_trace/report.py"),
        "source_phrases": ("def render_markdown", "def render_json", "Event IDs"),
    },
    {
        "id": "baseline_vs_intervention_comparison",
        "paper_phrase": "baseline vs intervention comparison",
        "source_path": DEFAULT_RESEARCH,
        "source_phrases": ("def aggregate_runs", "PROMPT_TYPES", "baseline", "intervention"),
    },
)


def build_method_pipeline_audit(
    paper_path: Path = DEFAULT_PAPER,
    cli_path: Path = DEFAULT_CLI,
) -> dict[str, Any]:
    paper_text = paper_path.read_text(encoding="utf-8")
    cli_text = cli_path.read_text(encoding="utf-8")
    stage_rows = []
    for stage in PIPELINE_STAGES:
        source_path = Path(stage["source_path"])
        source_text = source_path.read_text(encoding="utf-8")
        source_present = all(phrase in source_text for phrase in stage["source_phrases"])
        stage_rows.append({
            "id": stage["id"],
            "paper_present": stage["paper_phrase"] in paper_text,
            "source_path": str(source_path),
            "source_phrases": list(stage["source_phrases"]),
            "source_present": source_present,
            "covered": stage["paper_phrase"] in paper_text and source_present,
        })

    smoke = _run_pipeline_smoke()
    cli_checks = {
        "collect_command": 'subparsers.add_parser("collect"' in cli_text,
        "diagnose_command": 'subparsers.add_parser("diagnose"' in cli_text,
        "aggregate_command": 'add_parser("aggregate"' in cli_text,
        "paper_report_command": 'add_parser("paper-report"' in cli_text,
    }
    return {
        "summary": {
            "ready": all(row["covered"] for row in stage_rows)
            and all(cli_checks.values())
            and smoke["ready"],
            "stage_count": len(stage_rows),
            "covered_stage_count": sum(1 for row in stage_rows if row["covered"]),
            "cli_check_count": len(cli_checks),
            "covered_cli_check_count": sum(1 for value in cli_checks.values() if value),
            "smoke_check_count": smoke["summary"]["check_count"],
            "covered_smoke_check_count": smoke["summary"]["covered_check_count"],
            "paper_path": str(paper_path),
        },
        "stages": stage_rows,
        "cli_checks": cli_checks,
        "smoke": smoke,
    }


def render_method_pipeline_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Method Pipeline Audit",
        "",
        "This generated audit checks that the CodexTrace method pipeline described in the paper maps to source code and offline CLI smoke outputs.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Pipeline stages covered: {summary['covered_stage_count']} / {summary['stage_count']}",
        f"- CLI method commands covered: {summary['covered_cli_check_count']} / {summary['cli_check_count']}",
        f"- Smoke checks covered: {summary['covered_smoke_check_count']} / {summary['smoke_check_count']}",
        f"- Paper draft: `{summary['paper_path']}`",
        "",
        "## Pipeline Stage Mapping",
        "",
        "| Stage | Paper | Source | Covered |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["stages"]:
        lines.append(
            f"| `{row['id']}` | {'yes' if row['paper_present'] else 'no'} | `{row['source_path']}` | {'yes' if row['covered'] else 'no'} |"
        )

    lines.extend([
        "",
        "## CLI Checks",
        "",
        "| Command | Covered |",
        "| --- | --- |",
    ])
    for name, covered in result["cli_checks"].items():
        lines.append(f"| `{name}` | {'yes' if covered else 'no'} |")

    lines.extend([
        "",
        "## Smoke Checks",
        "",
        "| Check | Covered |",
        "| --- | --- |",
    ])
    for row in result["smoke"]["checks"]:
        lines.append(f"| `{row['id']}` | {'yes' if row['covered'] else 'no'} |")

    lines.extend([
        "",
        "Interpretation: this audit exercises the offline parser, diagnosis, and aggregate surfaces on committed inputs. It does not execute live Codex collection.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_method_pipeline_markdown(result), encoding="utf-8")


def _run_pipeline_smoke() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="codextrace-method-pipeline-") as tmp_name:
        tmp = Path(tmp_name)
        collect_path = tmp / "trace.json"
        diagnosis_path = tmp / "diagnosis.json"
        aggregate_path = tmp / "aggregate.json"
        aggregate_md_path = tmp / "aggregate.md"
        checks = []

        collect_exit = _run_cli(["collect", "demo/failing-codex-trace.jsonl", "-o", str(collect_path)])
        collect = json.loads(collect_path.read_text(encoding="utf-8")) if collect_path.exists() else {}
        checks.append({
            "id": "collect_normalized_trace",
            "covered": collect_exit == 0 and bool(collect.get("events")) and "thread_id" in collect,
        })
        event_phases = {event.get("phase") for event in collect.get("events", [])}
        checks.append({
            "id": "collect_phase_segmentation",
            "covered": {"inspect", "verify", "recover"} & event_phases == {"inspect", "verify", "recover"},
        })

        diagnose_exit = _run_cli([
            "diagnose",
            "demo/failing-codex-trace.jsonl",
            "--format",
            "json",
            "-o",
            str(diagnosis_path),
        ])
        diagnosis = json.loads(diagnosis_path.read_text(encoding="utf-8")) if diagnosis_path.exists() else {}
        finding_codes = {finding.get("code") for finding in diagnosis.get("diagnosis", {}).get("findings", [])}
        checks.append({
            "id": "diagnose_failure_patterns",
            "covered": diagnose_exit == 0 and {"command_failure_unhandled", "repeated_search_or_read"} <= finding_codes,
        })
        checks.append({
            "id": "diagnose_event_ids",
            "covered": any(finding.get("event_ids") for finding in diagnosis.get("diagnosis", {}).get("findings", [])),
        })

        aggregate_exit = _run_cli([
            "research",
            "aggregate",
            "benchmark/runs.example.jsonl",
            "--json-output",
            str(aggregate_path),
            "--markdown-output",
            str(aggregate_md_path),
        ])
        aggregate = json.loads(aggregate_path.read_text(encoding="utf-8")) if aggregate_path.exists() else {}
        summary = aggregate.get("summary", {})
        checks.append({
            "id": "aggregate_baseline_intervention",
            "covered": aggregate_exit == 0
            and "baseline" in summary
            and "intervention" in summary,
        })
        aggregate_markdown = aggregate_md_path.read_text(encoding="utf-8") if aggregate_md_path.exists() else ""
        checks.append({
            "id": "aggregate_report_output",
            "covered": "# CodexTrace Research Aggregate" in aggregate_markdown
            and "| Metric | Baseline | Intervention | Delta |" in aggregate_markdown,
        })

    return {
        "ready": all(row["covered"] for row in checks),
        "summary": {
            "check_count": len(checks),
            "covered_check_count": sum(1 for row in checks if row["covered"]),
        },
        "checks": checks,
    }


def _run_cli(argv: list[str]) -> int:
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            return int(cli_main(argv) or 0)
    except SystemExit as error:
        return int(error.code or 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit CodexTrace method pipeline coverage.")
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--cli", type=Path, default=DEFAULT_CLI)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_method_pipeline_audit(args.paper, args.cli)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_method_pipeline_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
