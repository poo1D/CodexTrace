# Trace adapters

CodexTrace keeps one normalized `Trace` / `TraceEvent` schema while making
the source format explicit. This avoids heuristic format detection and keeps
existing Codex behavior backward compatible.

## Supported sources

| Adapter | Input contract | Status |
| --- | --- | --- |
| `codex` | `codex exec --json` JSONL events | Default and backward compatible |
| `openai-agents` | JSONL containing `Trace.export()` and `Span.export()` objects | Supported for documented trace/span exports |

Select the adapter at the CLI boundary:

```bash
codex-trace collect traces/codex.jsonl --adapter codex
codex-trace collect traces/agents-sdk.jsonl --adapter openai-agents
codex-trace diagnose traces/agents-sdk.jsonl --adapter openai-agents
```

Python callers can use:

```python
from codex_trace import load_trace

trace = load_trace("traces/agents-sdk.jsonl", adapter="openai-agents")
```

## OpenAI Agents SDK contract

The adapter consumes one trace plus its exported spans:

```json
{"object":"trace","id":"trace_...","workflow_name":"Repository repair","metadata":{}}
{"object":"trace.span","id":"span_...","trace_id":"trace_...","parent_id":null,"started_at":"...","ended_at":"...","span_data":{"type":"function","name":"exec_command","input":"{\"command\":\"pytest -q\"}","output":"{\"exit_code\":0}","mcp_data":null},"error":null}
```

The SDK documents traces as end-to-end workflows and spans as timed operations
with `trace_id`, `parent_id`, `span_data`, and optional errors. Default
tracing covers agent runs, generations, function tools, guardrails, and
handoffs; custom processors can persist the exported objects. See the official
[tracing guide](https://openai.github.io/openai-agents-python/tracing/),
[trace reference](https://openai.github.io/openai-agents-python/ref/tracing/traces/),
and [span reference](https://openai.github.io/openai-agents-python/ref/tracing/spans/).

The adapter has no runtime dependency on `openai-agents`. The SDK is only
needed to regenerate the provenance fixture.

## Conservative mapping

| Agents SDK span data | Normalized event |
| --- | --- |
| `agent` | `agent_message` |
| `generation` / `response` | `usage` |
| known shell function names with structured `command` / `cmd` input | `command` |
| known file-edit function names with a structured path or patch header | `file_change` |
| other `function`, `handoff`, `mcp_tools`, non-triggered guardrail | `mcp_tool` |
| custom `task` / `turn` | `turn` |
| triggered guardrail or non-tool span error | `error` |
| unrecognized span or custom name | `unknown` |

Agents SDK function spans do not inherently prove that a function is a shell
or file-edit tool. CodexTrace therefore recognizes a small documented name and
argument convention; every other function remains a generic tool event.

Usage selection avoids nested double counting per field: task values win over
turn values, then missing fields fall back to summed generation/response
values. Unknown trace, span, and `span_data` fields remain untouched in each
event's `metadata`.

## Boundaries

- One input file must contain at most one trace ID.
- Spans are ordered by `started_at`, then original position.
- The adapter does not fetch traces from the OpenAI platform.
- It does not infer file changes from arbitrary tool output.
- It does not claim protocol support for every custom trace processor.
- Trace inputs may contain sensitive model or tool data; sanitize before
  committing fixtures. The SDK exposes controls for excluding sensitive trace
  data in its [configuration guide](https://openai.github.io/openai-agents-python/config/#tracing).
