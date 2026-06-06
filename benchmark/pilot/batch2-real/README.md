# Batch 2 Real Pilot

This directory contains the second non-smoke CodexTrace pilot batch for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 16 real `codex exec --json` runs:

- 8 benchmark tasks: `CT-002`, `CT-003`, `CT-004`, `CT-005`, `CT-007`, `CT-008`, `CT-009`, `CT-010`
- 2 prompt conditions per task: `baseline` and `intervention`
- task categories: bug fix and feature tasks across Python and TypeScript

## Interpretation

All 16 runs passed their external grader checks. This batch extends the
successful-process dataset but does not add outcome failures. It is useful for
RQ3 process metrics because intervention prompts reduced repeated tool calls,
verification events, and token usage while preserving success.

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
