# Full 30-Task Real Pilot

This directory aggregates the first complete CodexTrace 30-task benchmark pass:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 60 real `codex exec --json` runs:

- 30 runnable benchmark tasks: `CT-001` through `CT-030`
- 2 prompt conditions per task: `baseline` and `intervention`
- source batches: `../batch1-real`, `../batch2-real`, and `../batch3-real`

## Interpretation

All 60 runs passed their external grader checks. This complete pilot validates
the collection harness and provides process-efficiency evidence, but it is not a
final failure-prevalence benchmark.

Observed process effects:

- success rate stayed at `1.0 -> 1.0`
- verification rate stayed at `1.0 -> 1.0`
- repeated tool calls dropped from `10.43 -> 7.00`
- command failures dropped from `0.50 -> 0.20`
- recovery events dropped from `2.07 -> 0.40`
- average token usage dropped from about `218.7k -> 184.8k`

The next required research step is a harder task tier or more realistic
repository tasks that produce genuine outcome failures. Without that, RQ1, RQ2,
and RQ4 cannot be evaluated for failure outcomes.

## Included Artifacts

- `runs.jsonl`: combined run manifest referencing the three source batches
- `aggregate.md` / `aggregate.json`: grouped metrics
- `paper-report.md` / `paper-report.json`: RQ table scaffold
- `runs.csv`: per-run metrics
- `labels.jsonl`: manual-label template with detector suggestions

Trace files remain in the source batch directories to avoid duplicating raw
events.
