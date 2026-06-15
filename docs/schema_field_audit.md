# Schema Field Audit

This generated audit checks that the paper-facing Run/Step schema maps to concrete CodexTrace parser, schema, and research outputs.

## Summary

- Ready: yes
- Objective schema fields checked: 15 / 15
- Run fields covered: 4 / 4
- Step fields covered: 11 / 11
- Representational mappings: 6
- Schema source: `codex_trace/schema.py`
- Parser source: `codex_trace/parser.py`
- Research source: `codex_trace/research.py`
- Paper draft: `docs/paper_draft.md`

## Objective Schema Boundary

The original protocol-level Run/Step schema is fully checked here, but not all objective fields are direct `TraceEvent` attributes. CodexTrace keeps those fields through aliases, trace-level aggregates, detector outputs, or event metadata when Codex JSONL does not expose a stable same-named event field.

| Objective field | Scope | Boundary | Covered |
| --- | --- | --- | --- |
| `Run.task_id` | `direct` | direct normalized field | yes |
| `Run.prompt_type` | `direct` | direct normalized field | yes |
| `Run.outcome` | `direct` | direct normalized field | yes |
| `Run.usage` | `trace_level` | run/trace-level aggregate, not always a per-step field | yes |
| `Step.timestamp` | `direct` | direct normalized field | yes |
| `Step.event_type` | `direct` | direct normalized field | yes |
| `Step.content` | `direct` | direct normalized field | yes |
| `Step.tool_name` | `representational` | preserved through title/detail/metadata rather than a same-named field | yes |
| `Step.command` | `direct` | direct normalized field | yes |
| `Step.status` | `direct` | direct normalized field | yes |
| `Step.error` | `representational` | preserved through title/detail/metadata rather than a same-named field | yes |
| `Step.file_paths` | `alias` | renamed implementation field | yes |
| `Step.token_usage` | `trace_level` | run/trace-level aggregate, not always a per-step field | yes |
| `Step.phase` | `direct` | direct normalized field | yes |
| `Step.failure_tags` | `derived` | detector or label output, not a raw event field | yes |

## Run Fields

| Paper field | Implementation source | Scope | Code | Paper | Covered |
| --- | --- | --- | --- | --- | --- |
| `Run.task_id` | RunRecord.task_id and run manifest rows | `direct` | yes | yes | yes |
| `Run.prompt_type` | RunRecord.prompt_type and PROMPT_TYPES | `direct` | yes | yes | yes |
| `Run.outcome` | RunRecord.outcome and finalized run rows | `direct` | yes | yes | yes |
| `Run.usage` | Trace.usage from turn.completed plus aggregate token_usage | `trace_level` | yes | yes | yes |

## Step Fields

| Paper field | Implementation source | Scope | Code | Paper | Covered |
| --- | --- | --- | --- | --- | --- |
| `Step.timestamp` | TraceEvent.timestamp | `direct` | yes | yes | yes |
| `Step.event_type` | TraceEvent.kind plus TraceEvent.raw_type | `direct` | yes | yes | yes |
| `Step.content` | TraceEvent.title and TraceEvent.detail | `direct` | yes | yes | yes |
| `Step.tool_name` | MCP tool name normalized into TraceEvent.title with metadata retained | `representational` | yes | yes | yes |
| `Step.command` | TraceEvent.command | `direct` | yes | yes | yes |
| `Step.status` | TraceEvent.status plus command exit_code | `direct` | yes | yes | yes |
| `Step.error` | error events, failed statuses, and failed command detail | `representational` | yes | yes | yes |
| `Step.file_paths` | TraceEvent.files from file_change events | `alias` | yes | yes | yes |
| `Step.token_usage` | Trace.usage and turn-event usage detail, surfaced as run-level token_usage metrics | `trace_level` | yes | yes | yes |
| `Step.phase` | TraceEvent.phase assigned by assign_phases | `direct` | yes | yes | yes |
| `Step.failure_tags` | diagnosis findings and manual-label failure_tags | `derived` | yes | yes | yes |

Interpretation: the schema mapping is representational for fields such as `Step.tool_name`, `Step.token_usage`, and `Step.failure_tags`. These are retained through normalized event title/detail/metadata, trace-level usage records, diagnosis findings, and manual-label outputs rather than always appearing as one same-named `TraceEvent` attribute.
