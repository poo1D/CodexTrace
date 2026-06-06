# Hard Pilot Part 1

This directory contains the first half of the hard-tier CodexTrace pilot for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 10 real `codex exec --json` runs:

- 5 hard tasks: `HARD-001` through `HARD-005`
- 2 prompt conditions per task: `baseline` and `intervention`
- hidden external graders copied only after the Codex run finished

## Results

- baseline success rate: `0.8`
- intervention success rate: `1.0`
- repeated tool calls: `9.6 -> 6.8`
- average token usage: about `249.3k -> 204.5k`

`HARD-001` is the key outcome failure in this batch: the baseline run failed a
hidden half-open interval edge case, while the intervention run passed.

## Included Artifacts

- `runs.jsonl`: run manifest for this batch
- `aggregate.md` / `aggregate.json`: grouped metrics
- `paper-report.md` / `paper-report.json`: RQ table scaffold
- `runs.csv`: per-run metrics
- `labels.jsonl`: manual-label template with detector suggestions
- per-run `trace.jsonl`, `prompt.md`, and `success_check.txt`

Runtime worktrees, `codex.stderr`, and hidden grader files are intentionally not
stored here.
