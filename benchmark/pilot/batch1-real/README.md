# Batch 1 Real Pilot

This directory contains the first non-smoke CodexTrace pilot batch for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 14 real `codex exec --json` runs:

- 7 benchmark tasks: `CT-001`, `CT-006`, `CT-011`, `CT-016`, `CT-021`, `CT-026`, `CT-028`
- 2 prompt conditions per task: `baseline` and `intervention`
- task categories: bug fix, feature, test writing, refactor, CI failure, error localization, and multi-turn change

## Interpretation

All 14 runs passed their external grader checks. This batch is therefore not a
final failure-prevalence dataset. It is useful as an early process-difference
pilot:

- fixture repos and external graders are runnable
- the trace parser recognizes external grader commands as verification
- intervention prompts reduced repeated tool calls, command failures, recovery events, and token usage in this batch
- outcome-failure examples are still needed for the final paper benchmark

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
