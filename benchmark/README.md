# Benchmark Scaffold

This directory is the starting point for the paper experiment:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

## Contents

- `tasks.jsonl`: 30 seed coding tasks covering bug fixes, small features, tests,
  refactors, CI failures, error localization, and multi-turn changes.
- `prompts/baseline.txt`: the normal Codex prompt template.
- `prompts/intervention.txt`: the harness-constrained prompt template.
- `runs.example.jsonl`: a tiny manifest that reuses demo traces to exercise the
  aggregation pipeline before collecting the full benchmark.

## Render a Prompt

```bash
codex-trace research prompt CT-001 baseline
codex-trace research prompt CT-001 intervention
```

## Full Collection Plan

For each task:

```bash
codex exec --json "$(codex-trace research prompt CT-001 baseline)" > runs/CT-001/baseline.jsonl
codex exec --json "$(codex-trace research prompt CT-001 intervention)" > runs/CT-001/intervention.jsonl
```

Record final task outcomes in the run manifest:

```jsonl
{"task_id":"CT-001","prompt_type":"baseline","trace_path":"runs/CT-001/baseline.jsonl","outcome":"failure"}
{"task_id":"CT-001","prompt_type":"intervention","trace_path":"runs/CT-001/intervention.jsonl","outcome":"success"}
```

Then aggregate:

```bash
codex-trace research aggregate benchmark/runs.example.jsonl \
  --json-output reports/example-aggregate.json \
  --markdown-output reports/example-aggregate.md \
  --csv-output reports/example-runs.csv
```
