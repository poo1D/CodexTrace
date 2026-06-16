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
- Run manifest provenance fields: 600 / 600
- Manifest prompt paths present: 60 / 60
- Manifest success checks recorded: 60 / 60
- Manifest Codex exit codes recorded: 60 / 60
- Outcome rows with grader results: 60 / 60
- Manual label rows: 60 / 60
- Labeled failure rows: 30
- Prompt-type balance ready: yes
- Tasks manifest: `benchmark/hard/pilot/hard30-selection/tasks.jsonl`
- Run manifest: `benchmark/hard/pilot/hard30-real/runs.jsonl`
- Manual labels: `benchmark/hard/pilot/hard30-real/manual-labels.jsonl`

## Run Manifest Provenance

| Field | Rows with field | Committed path exists | Notes |
| --- | ---: | ---: | --- |
| `trace_path` | 60 | 60 | raw `codex exec --json` trace |
| `prompt_path` | 60 | 60 | prompt used for the run |
| `success_check` | 60 | - | visible command recorded in manifest |
| `codex_exit_code` | 60 | - | Codex process exit status recorded in manifest |
| `grader_path` | 60 | 0 | hidden-grader path reference; grader directory is not committed |
| `workdir` | 60 | 0 | run worktree path reference; mutable workdir is not committed |

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

## Prompt-Type Balance

| Prompt type | Run rows | Nonempty traces | Parseable traces | Outcome rows | Label rows | Balanced |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline` | 30 | 30 | 30 | 30 | 30 | yes |
| `intervention` | 30 | 30 | 30 | 30 | 30 | yes |

## Consistency Checks

- Missing run keys: 0
- Extra run keys: 0
- Missing label keys: 0
- Extra label keys: 0

Interpretation: this audit proves the committed hard30 paper artifact has paired task/run/trace/label records and run-manifest provenance for trace, prompt, success-check, outcome, and Codex exit status. It does not rerun Codex or hidden graders, and it treats grader/workdir paths as provenance references rather than committed directories.
