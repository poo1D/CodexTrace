# Benchmark Trace Artifact Audit

This generated audit checks that the paper-facing hard30 benchmark has paired baseline/intervention Codex JSONL traces, task metadata, grader outcomes, and manual labels.

## Summary

- Ready: yes
- Tasks covered: 30 / 30
- Unique task IDs: 30 / 30
- Run rows covered: 60 / 60
- Paired baseline/intervention tasks: 30 / 30
- Codex JSONL traces covered: 60 / 60
- Trace event lines: 2074
- Parseable traces: 60 / 60
- Parsed trace events: 2074
- Diagnosable traces: 60 / 60
- Trace sidecar bundles: 60 / 60
- Outcome rows with grader results: 60 / 60
- Manual label rows: 60 / 60
- Labeled failure rows: 30
- Tasks manifest: `benchmark/hard/pilot/hard30-selection/tasks.jsonl`
- Run manifest: `benchmark/hard/pilot/hard30-real/runs.jsonl`
- Manual labels: `benchmark/hard/pilot/hard30-real/manual-labels.jsonl`

## Category Counts

| Category | Tasks |
| --- | ---: |
| `bug_fix` | 4 |
| `ci_failure` | 2 |
| `data_migration` | 1 |
| `dependency_friction` | 3 |
| `error_localization` | 2 |
| `error_recovery` | 3 |
| `feature` | 4 |
| `multi_turn_change` | 3 |
| `multi_turn_tool_debug` | 2 |
| `refactor` | 1 |
| `sandbox_friction` | 1 |
| `stateful_regression` | 4 |

## Outcome Counts

| Outcome | Runs |
| --- | ---: |
| `failure` | 30 |
| `success` | 30 |

## Consistency Checks

- Missing run keys: 0
- Extra run keys: 0
- Missing label keys: 0
- Extra label keys: 0

Interpretation: this audit proves the committed hard30 paper artifact has paired task/run/trace/label records. It does not rerun Codex or hidden graders.
