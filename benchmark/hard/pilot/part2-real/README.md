# Hard Pilot Part 2

This directory contains the second half of the hard-tier CodexTrace pilot for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 10 real `codex exec --json` runs:

- 5 hard tasks: `HARD-006` through `HARD-010`
- 2 prompt conditions per task: `baseline` and `intervention`
- hidden external graders copied only after the Codex run finished

## Results

- baseline success rate: `0.6`
- intervention success rate: `0.6`
- repeated tool calls: `8.8 -> 5.6`
- average token usage: about `248.5k -> 170.4k`

`HARD-006` and `HARD-009` failed under both prompts. These failures are useful
negative examples for RQ2 because the traces look procedurally clean but the
hidden grader catches semantic edge cases.

## Included Artifacts

- `runs.jsonl`: run manifest for this batch
- `aggregate.md` / `aggregate.json`: grouped metrics
- `paper-report.md` / `paper-report.json`: RQ table scaffold
- `runs.csv`: per-run metrics
- `labels.jsonl`: manual-label template with detector suggestions
- per-run `trace.jsonl`, `prompt.md`, and `success_check.txt`

Runtime worktrees, `codex.stderr`, and hidden grader files are intentionally not
stored here.
