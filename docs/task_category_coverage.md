# Task Category Coverage Audit

This generated audit checks that benchmark task manifests cover the task categories named in the experiment design.

## Summary

- Ready: yes
- Seed design categories covered: 7 / 7
- Seed tasks: 30
- Hard tasks: 50
- Hard30 selected tasks: 30
- Hard30 distinct categories: 12
- Missing category rows: 0

## Required Design Categories

| Category | Seed | Hard pool | Hard30 selection |
| --- | ---: | ---: | ---: |
| `bug_fix` | 5 | 7 | 4 |
| `feature` | 5 | 8 | 4 |
| `test_writing` | 5 | 0 | 0 |
| `refactor` | 5 | 4 | 1 |
| `ci_failure` | 5 | 3 | 2 |
| `error_localization` | 2 | 4 | 2 |
| `multi_turn_change` | 3 | 7 | 3 |

## Tier Category Counts

- `seed`: `bug_fix`=5, `ci_failure`=5, `error_localization`=2, `feature`=5, `multi_turn_change`=3, `refactor`=5, `test_writing`=5
- `hard`: `bug_fix`=7, `ci_failure`=3, `data_migration`=2, `dependency_friction`=3, `error_localization`=4, `error_recovery`=3, `feature`=8, `multi_turn_change`=7, `multi_turn_tool_debug`=3, `refactor`=4, `sandbox_friction`=1, `stateful_regression`=5
- `hard30`: `bug_fix`=4, `ci_failure`=2, `data_migration`=1, `dependency_friction`=3, `error_localization`=2, `error_recovery`=3, `feature`=4, `multi_turn_change`=3, `multi_turn_tool_debug`=2, `refactor`=1, `sandbox_friction`=1, `stateful_regression`=4

Interpretation: the seed benchmark covers all task categories named in the original design. The hard30 paper-facing tier is selected for hidden-grader difficulty and broad category diversity; it is not required to preserve every seed category one-for-one.
