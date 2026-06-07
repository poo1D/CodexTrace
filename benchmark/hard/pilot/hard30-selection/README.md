# Hard30 Pilot Selection

This directory fixes the 30-task hard-tier pilot used for the next real
baseline/intervention collection pass.

The selection keeps `HARD-001` through `HARD-010` as the evaluated hard10
prefix, then adds 20 tasks from the expanded hard tier to cover every hard
category and several intended process-failure pressures.

Expected real run count: 30 tasks x 2 prompt conditions = 60 runs.

## Category Counts

{
  "bug_fix": 4,
  "ci_failure": 2,
  "data_migration": 1,
  "dependency_friction": 3,
  "error_localization": 2,
  "error_recovery": 3,
  "feature": 4,
  "multi_turn_change": 3,
  "multi_turn_tool_debug": 2,
  "refactor": 1,
  "sandbox_friction": 1,
  "stateful_regression": 4
}

## Selected Tasks

| ID | Category | Repo hint |
| --- | --- | --- |
| HARD-001 | bug_fix | python/interval_merge |
| HARD-002 | bug_fix | python/csv_records |
| HARD-003 | feature | python/cent_allocation |
| HARD-004 | error_localization | python/toposort |
| HARD-005 | bug_fix | typescript/router |
| HARD-006 | feature | typescript/retry |
| HARD-007 | refactor | python/config_merge |
| HARD-008 | bug_fix | typescript/undo_redo |
| HARD-009 | multi_turn_change | python/booking_policy |
| HARD-010 | feature | typescript/markdown_table |
| HARD-011 | error_recovery | python/json_patch |
| HARD-012 | dependency_friction | python/http_client |
| HARD-013 | multi_turn_change | typescript/filter_builder |
| HARD-015 | ci_failure | typescript/package_exports |
| HARD-020 | sandbox_friction | typescript/asset_loader |
| HARD-023 | error_recovery | python/cache_stampede |
| HARD-024 | feature | typescript/csv_stream |
| HARD-025 | ci_failure | python/typing_protocol |
| HARD-027 | dependency_friction | typescript/date_formatter |
| HARD-031 | multi_turn_tool_debug | python/env_manifest_resolver |
| HARD-032 | stateful_regression | typescript/undoable_queue |
| HARD-033 | error_recovery | python/log_redactor |
| HARD-035 | dependency_friction | python/retry_policy |
| HARD-038 | error_localization | typescript/source_map_ranges |
| HARD-039 | multi_turn_tool_debug | python/cli_report_writer |
| HARD-040 | stateful_regression | python/ledger_reconciler |
| HARD-043 | data_migration | python/migration_runner |
| HARD-045 | stateful_regression | python/stream_window_join |
| HARD-047 | stateful_regression | python/webhook_replay_guard |
| HARD-050 | multi_turn_change | python/config_overlay_resolver |

## Dry-Run Command

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/hard/pilot/hard30-selection/tasks.jsonl \
  --output-dir /tmp/codextrace-hard30-dry \
  --dry-run
```

## Real Collection Command

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/hard/pilot/hard30-selection/tasks.jsonl \
  --output-dir benchmark/hard/pilot/hard30-real \
  --timeout-seconds 600
```

## Finalize Reports

After the real run completes, generate aggregate tables, per-run CSV, label
templates, and paper-report artifacts:

```bash
PYTHONPATH=. python3 scripts/finalize_hard30_pilot.py \
  --run-dir benchmark/hard/pilot/hard30-real
```
