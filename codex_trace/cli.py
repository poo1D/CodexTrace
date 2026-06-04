from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diagnose import diagnose
from .parser import parse_jsonl
from .report import render_json, render_markdown
from .research import aggregate_runs, load_tasks, render_aggregate_markdown, render_prompt, write_aggregate_outputs, write_runs_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codex-trace", description="Diagnose Codex exec --json traces.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Normalize a Codex JSONL trace into schema JSON.")
    collect.add_argument("trace", type=Path)
    collect.add_argument("-o", "--output", type=Path)

    diagnose_cmd = subparsers.add_parser("diagnose", help="Diagnose a Codex JSONL trace.")
    diagnose_cmd.add_argument("trace", type=Path)
    diagnose_cmd.add_argument("--format", choices=["markdown", "json"], default="markdown")
    diagnose_cmd.add_argument("-o", "--output", type=Path)

    research = subparsers.add_parser("research", help="Research benchmark helpers.")
    research_subparsers = research.add_subparsers(dest="research_command", required=True)

    prompt_cmd = research_subparsers.add_parser("prompt", help="Render a baseline or intervention prompt for one task.")
    prompt_cmd.add_argument("task_id")
    prompt_cmd.add_argument("prompt_type", choices=["baseline", "intervention"])
    prompt_cmd.add_argument("--tasks", type=Path, default=Path("benchmark/tasks.jsonl"))
    prompt_cmd.add_argument("--prompt-dir", type=Path, default=Path("benchmark/prompts"))

    aggregate_cmd = research_subparsers.add_parser("aggregate", help="Aggregate baseline vs intervention trace runs.")
    aggregate_cmd.add_argument("manifest", type=Path)
    aggregate_cmd.add_argument("--json-output", type=Path)
    aggregate_cmd.add_argument("--markdown-output", type=Path)
    aggregate_cmd.add_argument("--csv-output", type=Path)

    args = parser.parse_args(argv)

    if args.command == "collect":
        trace = parse_jsonl(args.trace)
        output = render_trace_json(trace)
        _write_or_print(output, args.output)
        return 0

    if args.command == "diagnose":
        trace = parse_jsonl(args.trace)
        diagnosis = diagnose(trace)
        output = render_json(trace, diagnosis) if args.format == "json" else render_markdown(trace, diagnosis)
        _write_or_print(output, args.output)
        return 0

    if args.command == "research" and args.research_command == "prompt":
        tasks = {task.task_id: task for task in load_tasks(args.tasks)}
        if args.task_id not in tasks:
            raise SystemExit(f"Unknown task_id: {args.task_id}")
        print(render_prompt(tasks[args.task_id], args.prompt_type, args.prompt_dir))
        return 0

    if args.command == "research" and args.research_command == "aggregate":
        result = aggregate_runs(args.manifest)
        if args.csv_output:
            write_runs_csv(result, args.csv_output)
        if args.json_output or args.markdown_output:
            write_aggregate_outputs(result, args.json_output, args.markdown_output)
        else:
            print(render_aggregate_markdown(result), end="")
        return 0

    parser.print_help(sys.stderr)
    return 2


def render_trace_json(trace) -> str:
    import json

    return json.dumps(trace.to_dict(), ensure_ascii=False, indent=2) + "\n"


def _write_or_print(content: str, output: Path | None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    raise SystemExit(main())
