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


DEFAULT_CLI = Path("codex_trace/cli.py")
DEFAULT_README = Path("README.md")
DEFAULT_REPRO_CHECKLIST = Path("docs/reproducibility_checklist.md")


COMMANDS = (
    {
        "id": "collect",
        "argv": lambda tmp: ["collect", "demo/failing-codex-trace.jsonl", "-o", str(tmp / "trace.json")],
        "outputs": ("trace.json",),
        "expected": ("events", "thread_id"),
    },
    {
        "id": "diagnose_json",
        "argv": lambda tmp: ["diagnose", "demo/failing-codex-trace.jsonl", "--format", "json", "-o", str(tmp / "diagnosis.json")],
        "outputs": ("diagnosis.json",),
        "expected": ("diagnosis", "event_ids"),
    },
    {
        "id": "research_prompt",
        "argv": lambda tmp: ["research", "prompt", "--tasks", "benchmark/tasks.jsonl", "CT-001", "baseline"],
        "outputs": (),
        "stdout_expected": ("Fix an off-by-one bug", "Complete the task with your normal coding workflow"),
    },
    {
        "id": "research_aggregate",
        "argv": lambda tmp: [
            "research",
            "aggregate",
            "benchmark/runs.example.jsonl",
            "--json-output",
            str(tmp / "aggregate.json"),
            "--markdown-output",
            str(tmp / "aggregate.md"),
            "--csv-output",
            str(tmp / "runs.csv"),
        ],
        "outputs": ("aggregate.json", "aggregate.md", "runs.csv"),
        "expected": ("summary", "taxonomy_tags"),
    },
    {
        "id": "research_label_template",
        "argv": lambda tmp: ["research", "label-template", "benchmark/runs.example.jsonl", "--output", str(tmp / "labels.jsonl")],
        "outputs": ("labels.jsonl",),
        "expected": ("failure_tags", "task_id"),
    },
    {
        "id": "research_evaluate_labels",
        "argv": lambda tmp: [
            "research",
            "evaluate-labels",
            "benchmark/runs.example.jsonl",
            "benchmark/labels.example.jsonl",
            "--json-output",
            str(tmp / "label-eval.json"),
            "--markdown-output",
            str(tmp / "label-eval.md"),
        ],
        "outputs": ("label-eval.json", "label-eval.md"),
        "expected": ("micro_f1", "Label Evaluation"),
    },
    {
        "id": "research_paper_report",
        "argv": lambda tmp: [
            "research",
            "paper-report",
            "benchmark/runs.example.jsonl",
            "--labels",
            "benchmark/labels.example.jsonl",
            "--json-output",
            str(tmp / "paper-report.json"),
            "--markdown-output",
            str(tmp / "paper-report.md"),
        ],
        "outputs": ("paper-report.json", "paper-report.md"),
        "expected": ("RQ3 Baseline vs Intervention", "paired_task_summary"),
    },
    {
        "id": "research_summary",
        "argv": lambda tmp: [
            "research",
            "summary",
            "--json-output",
            str(tmp / "summary.json"),
            "--markdown-output",
            str(tmp / "summary.md"),
        ],
        "outputs": ("summary.json", "summary.md"),
        "expected": ("hard30", "RQ4"),
    },
    {
        "id": "research_run_dry",
        "argv": lambda tmp: [
            "research",
            "run",
            "--tasks",
            "benchmark/smoke/tasks.jsonl",
            "--output-dir",
            str(tmp / "smoke-dry"),
            "--dry-run",
        ],
        "outputs": ("smoke-dry/runs.jsonl",),
        "expected": ("not_run", "trace_path"),
    },
)


def build_cli_surface_audit(
    cli_path: Path = DEFAULT_CLI,
    readme_path: Path = DEFAULT_README,
    repro_checklist_path: Path = DEFAULT_REPRO_CHECKLIST,
) -> dict[str, Any]:
    cli_text = cli_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")
    checklist_text = repro_checklist_path.read_text(encoding="utf-8")
    command_rows = []
    with tempfile.TemporaryDirectory(prefix="codextrace-cli-audit-") as tmp_name:
        tmp = Path(tmp_name)
        for command in COMMANDS:
            stdout = io.StringIO()
            stderr = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = cli_main(command["argv"](tmp))
            except SystemExit as error:
                exit_code = int(error.code or 0)
            output_text = _read_outputs(tmp, command.get("outputs", ())) + stdout.getvalue()
            expected = tuple(command.get("expected", ())) + tuple(command.get("stdout_expected", ()))
            output_present = all((tmp / output).exists() for output in command.get("outputs", ()))
            expected_present = all(phrase in output_text for phrase in expected)
            command_rows.append({
                "id": command["id"],
                "exit_code": exit_code,
                "outputs": list(command.get("outputs", ())),
                "output_present": output_present,
                "expected_phrases": list(expected),
                "expected_present": expected_present,
                "stderr": stderr.getvalue(),
                "covered": exit_code == 0 and output_present and expected_present,
            })

    subcommand_checks = {
        "collect": 'subparsers.add_parser("collect"' in cli_text,
        "diagnose": 'subparsers.add_parser("diagnose"' in cli_text,
        "research_prompt": 'add_parser("prompt"' in cli_text,
        "research_aggregate": 'add_parser("aggregate"' in cli_text,
        "research_label_template": 'add_parser("label-template"' in cli_text,
        "research_evaluate_labels": 'add_parser("evaluate-labels"' in cli_text,
        "research_paper_report": 'add_parser("paper-report"' in cli_text,
        "research_summary": 'add_parser("summary"' in cli_text,
        "research_run": 'add_parser("run"' in cli_text,
    }
    doc_checks = {
        "readme_diagnose": "codex-trace diagnose" in readme_text,
        "readme_collect": "codex-trace collect" in readme_text,
        "readme_research_aggregate": "codex-trace research aggregate" in readme_text,
        "readme_research_run": "codex-trace research run" in readme_text,
        "checklist_summary": "codex_trace.cli research summary" in checklist_text,
        "checklist_aggregate": "codex_trace.cli research aggregate" in checklist_text,
    }
    return {
        "summary": {
            "ready": all(row["covered"] for row in command_rows)
            and all(subcommand_checks.values())
            and all(doc_checks.values()),
            "command_count": len(command_rows),
            "covered_command_count": sum(1 for row in command_rows if row["covered"]),
            "subcommand_count": len(subcommand_checks),
            "covered_subcommand_count": sum(1 for value in subcommand_checks.values() if value),
            "doc_check_count": len(doc_checks),
            "covered_doc_check_count": sum(1 for value in doc_checks.values() if value),
            "cli_path": str(cli_path),
            "readme_path": str(readme_path),
            "repro_checklist_path": str(repro_checklist_path),
        },
        "commands": command_rows,
        "subcommand_checks": subcommand_checks,
        "doc_checks": doc_checks,
    }


def render_cli_surface_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# CLI Surface Audit",
        "",
        "This generated audit smoke-tests the offline CLI entry points used to normalize traces, diagnose failures, and regenerate paper-facing research artifacts.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- CLI commands covered: {summary['covered_command_count']} / {summary['command_count']}",
        f"- Parser subcommands present: {summary['covered_subcommand_count']} / {summary['subcommand_count']}",
        f"- Documentation checks covered: {summary['covered_doc_check_count']} / {summary['doc_check_count']}",
        f"- CLI source: `{summary['cli_path']}`",
        f"- README: `{summary['readme_path']}`",
        f"- Reproducibility checklist: `{summary['repro_checklist_path']}`",
        "",
        "## Command Smoke Tests",
        "",
        "| Command | Exit | Outputs | Expected text | Covered |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in result["commands"]:
        lines.append(
            f"| `{row['id']}` | {row['exit_code']} | {_yes(row['output_present'])} | "
            f"{_yes(row['expected_present'])} | {_yes(row['covered'])} |"
        )

    lines.extend([
        "",
        "## Subcommand Checks",
        "",
        "| Subcommand | Present |",
        "| --- | --- |",
    ])
    for name, present in result["subcommand_checks"].items():
        lines.append(f"| `{name}` | {_yes(present)} |")

    lines.extend([
        "",
        "Interpretation: this audit proves the offline CLI surface can regenerate representative trace, diagnosis, aggregate, label, paper-report, summary, and dry-run harness artifacts from committed inputs. It does not execute live Codex collection.",
    ])
    return "\n".join(lines) + "\n"


def _read_outputs(root: Path, outputs: tuple[str, ...]) -> str:
    chunks = []
    for output in outputs:
        path = root / output
        if path.exists() and path.is_file():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_cli_surface_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the CodexTrace offline CLI command surface.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_cli_surface_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_cli_surface_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
