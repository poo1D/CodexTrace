from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA = Path("codex_trace/schema.py")
DEFAULT_PARSER = Path("codex_trace/parser.py")
DEFAULT_RESEARCH = Path("codex_trace/research.py")
DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")


RUN_FIELDS = (
    {
        "field": "Run.task_id",
        "implementation": "RunRecord.task_id and run manifest rows",
        "scope": "direct",
        "markers": ("task_id: str", 'item["task_id"]'),
    },
    {
        "field": "Run.prompt_type",
        "implementation": "RunRecord.prompt_type and PROMPT_TYPES",
        "scope": "direct",
        "markers": ("prompt_type: str", "PROMPT_TYPES"),
    },
    {
        "field": "Run.outcome",
        "implementation": "RunRecord.outcome and finalized run rows",
        "scope": "direct",
        "markers": ('outcome: str = "unknown"', '"outcome": outcome'),
    },
    {
        "field": "Run.usage",
        "implementation": "Trace.usage from turn.completed plus aggregate token_usage",
        "scope": "trace_level",
        "markers": ("usage: dict[str, Any]", 'payload.get("usage")', '"token_usage"'),
    },
)


STEP_FIELDS = (
    {
        "field": "Step.timestamp",
        "implementation": "TraceEvent.timestamp",
        "scope": "direct",
        "markers": ("timestamp: str | None", '"timestamp": self.timestamp'),
    },
    {
        "field": "Step.event_type",
        "implementation": "TraceEvent.kind plus TraceEvent.raw_type",
        "scope": "direct",
        "markers": ("kind: EventKind", "raw_type: str"),
    },
    {
        "field": "Step.content",
        "implementation": "TraceEvent.title and TraceEvent.detail",
        "scope": "direct",
        "markers": ("title: str", "detail: str"),
    },
    {
        "field": "Step.tool_name",
        "implementation": "MCP tool name normalized into TraceEvent.title with metadata retained",
        "scope": "representational",
        "markers": (
            'item_type in {"mcp_tool_call", "tool_call", "function_call"}',
            'item.get("name") or item.get("tool_name")',
        ),
    },
    {
        "field": "Step.command",
        "implementation": "TraceEvent.command",
        "scope": "direct",
        "markers": ("command: str | None", 'item.get("command")'),
    },
    {
        "field": "Step.status",
        "implementation": "TraceEvent.status plus command exit_code",
        "scope": "direct",
        "markers": ("status: str", "_status(payload)", "exit_code"),
    },
    {
        "field": "Step.error",
        "implementation": "error events, failed statuses, and failed command detail",
        "scope": "representational",
        "markers": ('raw_type == "error"', '"failed"', "event_status"),
    },
    {
        "field": "Step.file_paths",
        "implementation": "TraceEvent.files from file_change events",
        "scope": "alias",
        "markers": ("files: list[str]", "_extract_files", '"files": self.files'),
    },
    {
        "field": "Step.token_usage",
        "implementation": "Trace.usage and turn-event usage detail, surfaced as run-level token_usage metrics",
        "scope": "trace_level",
        "markers": ("trace.usage", "_usage_detail", '"token_usage"'),
    },
    {
        "field": "Step.phase",
        "implementation": "TraceEvent.phase assigned by assign_phases",
        "scope": "direct",
        "markers": ("phase: EventPhase", "assign_phases", '"phase": self.phase'),
    },
    {
        "field": "Step.failure_tags",
        "implementation": "diagnosis findings and manual-label failure_tags",
        "scope": "derived",
        "markers": ("TAXONOMY_ALIASES", "evaluate_detector_labels", "failure_tags"),
    },
)


def build_schema_field_audit(
    schema_path: Path = DEFAULT_SCHEMA,
    parser_path: Path = DEFAULT_PARSER,
    research_path: Path = DEFAULT_RESEARCH,
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
) -> dict[str, Any]:
    texts = {
        "schema": schema_path.read_text(encoding="utf-8"),
        "parser": parser_path.read_text(encoding="utf-8"),
        "research": research_path.read_text(encoding="utf-8"),
    }
    combined = "\n".join(texts.values())
    paper_text = paper_draft_path.read_text(encoding="utf-8")

    run_rows = [_row(field, combined, paper_text) for field in RUN_FIELDS]
    step_rows = [_row(field, combined, paper_text) for field in STEP_FIELDS]
    representational_scopes = {"alias", "derived", "representational", "trace_level"}
    representational_rows = [row for row in run_rows + step_rows if row["scope"] in representational_scopes]
    objective_rows = run_rows + step_rows

    return {
        "summary": {
            "ready": all(row["covered"] for row in run_rows + step_rows),
            "objective_schema_field_count": len(objective_rows),
            "objective_schema_fields_covered": sum(1 for row in objective_rows if row["covered"]),
            "run_field_count": len(run_rows),
            "run_fields_covered": sum(1 for row in run_rows if row["covered"]),
            "step_field_count": len(step_rows),
            "step_fields_covered": sum(1 for row in step_rows if row["covered"]),
            "representational_mapping_count": len(representational_rows),
            "schema_path": str(schema_path),
            "parser_path": str(parser_path),
            "research_path": str(research_path),
            "paper_draft_path": str(paper_draft_path),
        },
        "run_fields": run_rows,
        "step_fields": step_rows,
    }


def _row(field: dict[str, Any], combined_text: str, paper_text: str) -> dict[str, Any]:
    markers = list(field["markers"])
    paper_marker = f"`{field['field']}`"
    markers_present = [marker for marker in markers if marker in combined_text]
    paper_present = paper_marker in paper_text
    return {
        "field": field["field"],
        "implementation": field["implementation"],
        "scope": field["scope"],
        "boundary": _boundary_note(field["scope"]),
        "markers": markers,
        "markers_present": markers_present,
        "implementation_present": len(markers_present) == len(markers),
        "paper_present": paper_present,
        "covered": len(markers_present) == len(markers) and paper_present,
    }


def _boundary_note(scope: str) -> str:
    if scope == "direct":
        return "direct normalized field"
    if scope == "alias":
        return "renamed implementation field"
    if scope == "derived":
        return "detector or label output, not a raw event field"
    if scope == "trace_level":
        return "run/trace-level aggregate, not always a per-step field"
    if scope == "representational":
        return "preserved through title/detail/metadata rather than a same-named field"
    return "implementation-specific mapping"


def render_schema_field_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    objective_rows = result["run_fields"] + result["step_fields"]
    lines = [
        "# Schema Field Audit",
        "",
        "This generated audit checks that the paper-facing Run/Step schema maps to concrete CodexTrace parser, schema, and research outputs.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Objective schema fields checked: {summary['objective_schema_fields_covered']} / {summary['objective_schema_field_count']}",
        f"- Run fields covered: {summary['run_fields_covered']} / {summary['run_field_count']}",
        f"- Step fields covered: {summary['step_fields_covered']} / {summary['step_field_count']}",
        f"- Representational mappings: {summary['representational_mapping_count']}",
        f"- Schema source: `{summary['schema_path']}`",
        f"- Parser source: `{summary['parser_path']}`",
        f"- Research source: `{summary['research_path']}`",
        f"- Paper draft: `{summary['paper_draft_path']}`",
        "",
        "## Objective Schema Boundary",
        "",
        "The original protocol-level Run/Step schema is fully checked here, but not all objective fields are direct `TraceEvent` attributes. CodexTrace keeps those fields through aliases, trace-level aggregates, detector outputs, or event metadata when Codex JSONL does not expose a stable same-named event field.",
        "",
        "| Objective field | Scope | Boundary | Covered |",
        "| --- | --- | --- | --- |",
    ]
    for row in objective_rows:
        lines.append(
            f"| `{row['field']}` | `{row['scope']}` | {row['boundary']} | {_yes(row['covered'])} |"
        )

    lines.extend([
        "",
        "## Run Fields",
        "",
        "| Paper field | Implementation source | Scope | Code | Paper | Covered |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in result["run_fields"]:
        lines.append(_field_row(row))

    lines.extend([
        "",
        "## Step Fields",
        "",
        "| Paper field | Implementation source | Scope | Code | Paper | Covered |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for row in result["step_fields"]:
        lines.append(_field_row(row))

    lines.extend([
        "",
        "Interpretation: the schema mapping is representational for fields such as `Step.tool_name`, `Step.token_usage`, and `Step.failure_tags`. These are retained through normalized event title/detail/metadata, trace-level usage records, diagnosis findings, and manual-label outputs rather than always appearing as one same-named `TraceEvent` attribute.",
    ])
    return "\n".join(lines) + "\n"


def _field_row(row: dict[str, Any]) -> str:
    return (
        f"| `{row['field']}` | {row['implementation']} | `{row['scope']}` | "
        f"{_yes(row['implementation_present'])} | {_yes(row['paper_present'])} | {_yes(row['covered'])} |"
    )


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_schema_field_audit_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit paper-facing Run/Step schema fields against CodexTrace implementation sources."
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--parser", type=Path, default=DEFAULT_PARSER)
    parser.add_argument("--research", type=Path, default=DEFAULT_RESEARCH)
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_schema_field_audit(args.schema, args.parser, args.research, args.paper_draft)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_schema_field_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
