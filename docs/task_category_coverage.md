# Task Category Coverage Audit

This generated audit checks that benchmark task manifests cover the task categories named in the experiment design.

## Summary

- Ready: yes
- Seed design categories covered: 7 / 7
- Hard pool design categories covered: 6 / 7
- Hard pool missing design categories: `test_writing`
- Hard pool design-family categories covered: 6 / 7
- Hard pool missing design-family categories: `test_writing`
- Hard30 design-family categories covered: 6 / 7
- Hard30 missing design-family categories: `test_writing`
- Design task-count window: 30-50
- Seed tasks: 30
- Seed tasks in design window: yes
- Hard tasks: 50
- Hard tasks in design window: yes
- Hard30 selected tasks: 30
- Hard30 selected tasks in design window: yes
- Hard30 distinct categories: 12
- Missing category rows: 0

## Required Design Categories

| Category | Seed | Hard pool | Hard30 selection | Hard family | Hard30 family |
| --- | ---: | ---: | ---: | ---: | ---: |
| `bug_fix` | 5 | 7 | 4 | 15 | 11 |
| `feature` | 5 | 8 | 4 | 10 | 5 |
| `test_writing` | 5 | 0 | 0 | 0 | 0 |
| `refactor` | 5 | 4 | 1 | 4 | 1 |
| `ci_failure` | 5 | 3 | 2 | 6 | 5 |
| `error_localization` | 2 | 4 | 2 | 7 | 4 |
| `multi_turn_change` | 3 | 7 | 3 | 7 | 3 |

## Hard Category Family Mapping

Hard-tier categories refine the original design categories. Family counts aggregate those refinements back to the design-level task types; direct category counts are still reported separately so missing categories such as `test_writing` remain visible.

| Design category | Hard-tier categories counted in family |
| --- | --- |
| `bug_fix` | `bug_fix`, `error_recovery`, `stateful_regression` |
| `feature` | `feature`, `data_migration` |
| `test_writing` | `test_writing` |
| `refactor` | `refactor` |
| `ci_failure` | `ci_failure`, `dependency_friction` |
| `error_localization` | `error_localization`, `multi_turn_tool_debug` |
| `multi_turn_change` | `multi_turn_change` |

## Category Exemplars

Each row names a seed task that directly represents the original design category and, when available, a hard30 task that represents the mapped hard-tier family. The public success check is the visible verification command available to the agent during the run.

| Design category | Seed exemplar | Seed check | Hard30 family exemplar | Hard30 check |
| --- | --- | --- | --- | --- |
| `bug_fix` | `CT-001` / `python/toy_calc` | `python3 -m unittest discover -s tests` | `HARD-001` / `python/interval_merge` (bug_fix) | `python3 -m unittest discover -s tests` |
| `feature` | `CT-006` / `python/text_stats` | `python3 -m unittest discover -s tests` | `HARD-003` / `python/cent_allocation` (feature) | `python3 -m unittest discover -s tests` |
| `test_writing` | `CT-011` / `python/email_validator` | `python3 -m unittest discover -s tests` | boundary: none | `-` |
| `refactor` | `CT-016` / `python/csv_importer` | `python3 -m unittest discover -s tests` | `HARD-007` / `python/config_merge` (refactor) | `python3 -m unittest discover -s tests` |
| `ci_failure` | `CT-021` / `python/package_metadata` | `python3 -m unittest discover -s tests` | `HARD-015` / `typescript/package_exports` (ci_failure) | `npm run build` |
| `error_localization` | `CT-026` / `python/json_reader` | `python3 -m unittest discover -s tests` | `HARD-004` / `python/toposort` (error_localization) | `python3 -m unittest discover -s tests` |
| `multi_turn_change` | `CT-028` / `python/search_index` | `python3 -m unittest discover -s tests` | `HARD-009` / `python/booking_policy` (multi_turn_change) | `python3 -m unittest discover -s tests` |

## Tier Category Counts

- `seed`: `bug_fix`=5, `ci_failure`=5, `error_localization`=2, `feature`=5, `multi_turn_change`=3, `refactor`=5, `test_writing`=5
- `hard`: `bug_fix`=7, `ci_failure`=3, `data_migration`=2, `dependency_friction`=3, `error_localization`=4, `error_recovery`=3, `feature`=8, `multi_turn_change`=7, `multi_turn_tool_debug`=3, `refactor`=4, `sandbox_friction`=1, `stateful_regression`=5
- `hard30`: `bug_fix`=4, `ci_failure`=2, `data_migration`=1, `dependency_friction`=3, `error_localization`=2, `error_recovery`=3, `feature`=4, `multi_turn_change`=3, `multi_turn_tool_debug`=2, `refactor`=1, `sandbox_friction`=1, `stateful_regression`=4

Interpretation: the seed benchmark covers all task categories named in the original design. The hard pool and hard30 paper-facing tier are selected for hidden-grader difficulty and broad category diversity; they are not required to preserve every seed category one-for-one, and missing direct or family-level design categories such as `test_writing` must be treated as coverage boundaries.
