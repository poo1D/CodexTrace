# Hard 10-Task Real Pilot

This directory aggregates the hard-tier CodexTrace pilot for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It includes 20 real `codex exec --json` runs:

- 10 hard tasks: `HARD-001` through `HARD-010`
- 2 prompt conditions per task: `baseline` and `intervention`
- source batches: `../part1-real` and `../part2-real`

## Interpretation

Unlike the 30-task seed pilot, this hard tier produces genuine outcome failures:

- total outcomes: 15 success, 5 failure
- baseline success rate: `0.7`
- intervention success rate: `0.8`
- repeated tool calls dropped from `9.2 -> 6.2`
- average token usage dropped from about `248.9k -> 187.5k`

This is the first pilot result that supports outcome-level RQ3 claims: the
intervention improves success rate on this small hard slice while also reducing
repeated exploration and token usage.

The same result also sharpens RQ2. The current trace-based rules assign
`failure_score=0` to these hidden semantic failures because the agents did run
public verification commands and did not visibly deadlock. That is a useful
limitation: trace-only detectors expose many process failures, but they cannot
guarantee detection of semantic edge cases when the visible tests are incomplete.

## Leakage Control

Hard tasks expose only a public success check in the prompt, such as
`python3 -m unittest discover -s tests` or `npm test`. The hidden grader is
copied into the isolated run directory only after the Codex process exits, then
the collection runner executes the hidden `success_check` to assign the final
outcome.

## Included Artifacts

- `runs.jsonl`: combined run manifest referencing the two source batches
- `aggregate.md` / `aggregate.json`: grouped metrics
- `paper-report.md` / `paper-report.json`: RQ table scaffold
- `runs.csv`: per-run metrics
- `labels.jsonl`: manual-label template with detector suggestions

Trace files remain in the source batch directories to avoid duplicating raw
events.
