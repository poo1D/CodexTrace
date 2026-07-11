# OpenAI Agents SDK fixtures

These compact JSONL files exercise the public export contract used by the
OpenAI Agents SDK:

- a trace record from `Trace.export()`;
- span records from `Span.export()`;
- operation-specific payloads under `span_data`.

`tool_run.jsonl` is generated without a model or API call by
`scripts/generate_openai_agents_fixture.py`. The committed fixture was
generated with `openai-agents 0.18.2`; IDs and timestamps are deterministic,
and all inputs and outputs are synthetic. Regenerate it with:

```bash
uv run --with openai-agents python scripts/generate_openai_agents_fixture.py
```

The other files cover an errored tool, field-level task/turn/generation usage
priority, forward-compatible unknown fields, and invalid mixed-trace input.
They are intentionally hand-authored edge cases.

Format references:

- [Tracing guide](https://openai.github.io/openai-agents-python/tracing/)
- [Trace export reference](https://openai.github.io/openai-agents-python/ref/tracing/traces/)
- [Span export reference](https://openai.github.io/openai-agents-python/ref/tracing/spans/)
- [Span data reference](https://openai.github.io/openai-agents-python/ref/tracing/span_data/)

Agents SDK traces can include model and tool inputs and outputs. New fixtures
must be synthetic or sanitized before they are committed.
