# Benchmark Scaffold

This directory is the starting point for the paper experiment:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

## Contents

- `tasks.jsonl`: 30 seed coding tasks covering bug fixes, small features, tests,
  refactors, CI failures, error localization, and multi-turn changes.
- `repos/`: runnable fixture repositories plus external grader directories for
  the 30 seed tasks.
- `prompts/baseline.txt`: the normal Codex prompt template.
- `prompts/intervention.txt`: the harness-constrained prompt template.
- `runs.example.jsonl`: a tiny manifest that reuses demo traces to exercise the
  aggregation pipeline before collecting the full benchmark.
- `labels.example.jsonl`: example manual failure tags for detector precision and
  recall evaluation.
- `pilot/smoke-real`: 6 real `codex exec --json` pilot traces for the runnable
  smoke tasks.
- `pilot/batch1-real`: 14 real non-smoke pilot traces across seven task
  categories, with aggregate and paper-report outputs.

## Render a Prompt

```bash
codex-trace research prompt --tasks benchmark/tasks.jsonl CT-001 baseline
codex-trace research prompt --tasks benchmark/tasks.jsonl CT-001 intervention
```

## Full Collection Plan

For each task:

```bash
codex-trace research run \
  --tasks benchmark/tasks.jsonl \
  --output-dir runs/full \
  --timeout-seconds 300
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

Generate a manual-label template after collection:

```bash
codex-trace research label-template benchmark/runs.example.jsonl \
  --include-predictions \
  --output reports/example-label-template.jsonl
```

Evaluate detector labels:

```bash
codex-trace research evaluate-labels benchmark/runs.example.jsonl benchmark/labels.example.jsonl \
  --json-output reports/example-label-eval.json \
  --markdown-output reports/example-label-eval.md
```

Generate paper-ready RQ tables:

```bash
codex-trace research paper-report benchmark/runs.example.jsonl \
  --labels benchmark/labels.example.jsonl \
  --json-output reports/example-paper-report.json \
  --markdown-output reports/example-paper-report.md
```
