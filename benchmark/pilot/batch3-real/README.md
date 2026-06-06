# Batch 3 Real Pilot

This directory contains the third non-smoke CodexTrace pilot batch for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 30 real `codex exec --json` runs:

- 15 benchmark tasks: `CT-012`, `CT-013`, `CT-014`, `CT-015`, `CT-017`,
  `CT-018`, `CT-019`, `CT-020`, `CT-022`, `CT-023`, `CT-024`, `CT-025`,
  `CT-027`, `CT-029`, `CT-030`
- 2 prompt conditions per task: `baseline` and `intervention`
- task categories: test writing, refactor, CI failure, error localization, and
  multi-turn change

## Interpretation

All 30 runs passed their external grader checks. Like the prior non-smoke
batches, this batch contributes process metrics but not outcome-failure cases.
Intervention prompts reduced repeated tool calls, command failures, recovery
events, and token usage while preserving success.

## Included Artifacts

- `runs.jsonl`: run manifest
- `*/baseline/trace.jsonl` and `*/intervention/trace.jsonl`: raw Codex event streams
- `*/prompt.md`: rendered prompt used for each run
- `*/success_check.txt`: external grader output
- `aggregate.md` / `aggregate.json`: grouped metrics
- `paper-report.md` / `paper-report.json`: RQ table scaffold
- `runs.csv`: per-run metrics
- `labels.jsonl`: manual-label template with detector suggestions

Runtime repositories, external grader copies, and `codex.stderr` are intentionally
excluded from this directory.
