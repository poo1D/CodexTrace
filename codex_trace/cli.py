from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diagnose import diagnose
from .parser import parse_jsonl
from .report import render_json, render_markdown


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
