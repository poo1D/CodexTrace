from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.parser import parse_lines


DEFAULT_PARSER = Path("codex_trace/parser.py")
DEFAULT_SCHEMA = Path("codex_trace/schema.py")
DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")

EXPECTED_KINDS = (
    "thread",
    "turn",
    "agent_message",
    "reasoning",
    "command",
    "file_change",
    "mcp_tool",
    "web_search",
    "plan",
    "error",
    "unknown",
)
EXPECTED_PHASES = ("setup", "inspect", "edit", "verify", "recover", "complete", "other")
EXPECTED_SOURCE_MARKERS = (
    "thread.",
    "turn.",
    "agent_message",
    "reasoning",
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "web_search",
    "plan_update",
    'raw_type == "error"',
    "unknown",
)


def build_parser_event_coverage_audit(
    parser_path: Path = DEFAULT_PARSER,
    schema_path: Path = DEFAULT_SCHEMA,
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
) -> dict[str, Any]:
    trace = parse_lines(_synthetic_jsonl_lines(), source="synthetic-parser-coverage")
    kinds = {event.kind for event in trace.events}
    phases = {event.phase for event in trace.events}
    parser_text = parser_path.read_text(encoding="utf-8")
    schema_text = schema_path.read_text(encoding="utf-8")
    paper_text = paper_draft_path.read_text(encoding="utf-8")

    kind_rows = [
        {
            "kind": kind,
            "present": kind in kinds,
            "event_count": sum(1 for event in trace.events if event.kind == kind),
        }
        for kind in EXPECTED_KINDS
    ]
    phase_rows = [
        {
            "phase": phase,
            "present": phase in phases,
            "event_count": sum(1 for event in trace.events if event.phase == phase),
        }
        for phase in EXPECTED_PHASES
    ]
    source_rows = [
        {
            "marker": marker,
            "present": marker in parser_text,
        }
        for marker in EXPECTED_SOURCE_MARKERS
    ]
    feature_checks = {
        "thread_id": trace.thread_id == "parser-coverage-thread",
        "usage_input_tokens": trace.usage.get("input_tokens") == 123,
        "usage_output_tokens": trace.usage.get("output_tokens") == 45,
        "failed_command_status": any(
            event.kind == "command" and event.status == "failed" and event.exit_code == 2
            for event in trace.events
        ),
        "file_paths": any(event.kind == "file_change" and event.files == ["src/app.py"] for event in trace.events),
        "mcp_tool_name": any(event.kind == "mcp_tool" and event.title == "github.fetch" for event in trace.events),
        "web_search_query": any(event.kind == "web_search" and event.detail == "codex trace parser" for event in trace.events),
        "schema_event_kind_literal": "EventKind = Literal" in schema_text,
        "paper_pipeline_mentions_parser": "JSONL event parser" in paper_text,
        "paper_schema_mentions_event_type": "`Step.event_type`" in paper_text,
    }

    return {
        "summary": {
            "ready": all(row["present"] for row in kind_rows)
            and all(row["present"] for row in phase_rows)
            and all(row["present"] for row in source_rows)
            and all(feature_checks.values()),
            "event_count": len(trace.events),
            "kind_count": len(EXPECTED_KINDS),
            "covered_kind_count": sum(1 for row in kind_rows if row["present"]),
            "phase_count": len(EXPECTED_PHASES),
            "covered_phase_count": sum(1 for row in phase_rows if row["present"]),
            "source_marker_count": len(EXPECTED_SOURCE_MARKERS),
            "covered_source_marker_count": sum(1 for row in source_rows if row["present"]),
            "parser_path": str(parser_path),
            "schema_path": str(schema_path),
            "paper_draft_path": str(paper_draft_path),
        },
        "kinds": kind_rows,
        "phases": phase_rows,
        "source_markers": source_rows,
        "feature_checks": feature_checks,
    }


def render_parser_event_coverage_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Parser Event Coverage Audit",
        "",
        "This generated audit checks that the JSONL parser normalizes the event variants used by CodexTrace reports and paper-facing schema claims.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Synthetic events parsed: {summary['event_count']}",
        f"- Event kinds covered: {summary['covered_kind_count']} / {summary['kind_count']}",
        f"- Phases covered: {summary['covered_phase_count']} / {summary['phase_count']}",
        f"- Parser source markers covered: {summary['covered_source_marker_count']} / {summary['source_marker_count']}",
        f"- Parser source: `{summary['parser_path']}`",
        f"- Schema source: `{summary['schema_path']}`",
        f"- Paper draft: `{summary['paper_draft_path']}`",
        "",
        "## Event Kind Coverage",
        "",
        "| Event kind | Present | Events |",
        "| --- | --- | ---: |",
    ]
    for row in result["kinds"]:
        lines.append(f"| `{row['kind']}` | {_yes(row['present'])} | {row['event_count']} |")

    lines.extend([
        "",
        "## Phase Coverage",
        "",
        "| Phase | Present | Events |",
        "| --- | --- | ---: |",
    ])
    for row in result["phases"]:
        lines.append(f"| `{row['phase']}` | {_yes(row['present'])} | {row['event_count']} |")

    lines.extend([
        "",
        "## Feature Checks",
        "",
        "| Feature | Covered |",
        "| --- | --- |",
    ])
    for name, covered in result["feature_checks"].items():
        lines.append(f"| `{name}` | {_yes(covered)} |")

    lines.extend([
        "",
        "Interpretation: this audit covers parser branch coverage for the normalized event schema. It does not claim compatibility with every future Codex JSONL variant; unknown events are preserved as `unknown` with raw metadata.",
    ])
    return "\n".join(lines) + "\n"


def _synthetic_jsonl_lines() -> list[str]:
    payloads = [
        {"type": "thread.started", "thread_id": "parser-coverage-thread"},
        {"type": "unrecognized.top_level", "payload": {"value": 0}},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "Starting work."}},
        {"type": "item.completed", "item": {"type": "reasoning", "summary": "Need inspect then edit."}},
        {"type": "item.completed", "item": {"type": "command_execution", "command": "rg target", "exit_code": 0, "stdout": "src/app.py"}},
        {"type": "item.completed", "item": {"type": "file_change", "files": ["src/app.py"]}},
        {"type": "item.completed", "item": {"type": "command", "cmd": "pytest -q", "exit_code": 0, "stdout": "passed"}},
        {"type": "item.completed", "item": {"type": "command_execution", "command": "npm test", "exit_code": 2, "stderr": "permission denied"}},
        {"type": "item.completed", "item": {"type": "mcp_tool_call", "name": "github.fetch", "arguments": {"path": "README.md"}, "status": "completed"}},
        {"type": "item.completed", "item": {"type": "web_search", "query": "codex trace parser"}},
        {"type": "item.completed", "item": {"type": "plan_update", "steps": [{"step": "verify", "status": "done"}]}},
        {"type": "error", "message": "runtime error"},
        {"type": "item.completed", "item": {"type": "mystery_event", "value": 1}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "Completed after verification."}},
        {"type": "turn.completed", "usage": {"input_tokens": 123, "output_tokens": 45, "reasoning_output_tokens": 6}},
    ]
    return [json.dumps(payload, sort_keys=True) for payload in payloads]


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_parser_event_coverage_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit JSONL parser event-kind and phase coverage.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_parser_event_coverage_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_parser_event_coverage_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
