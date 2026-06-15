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
- Seed tasks: 30
- Hard tasks: 50
- Hard30 selected tasks: 30
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

## Tier Category Counts

- `seed`: `bug_fix`=5, `ci_failure`=5, `error_localization`=2, `feature`=5, `multi_turn_change`=3, `refactor`=5, `test_writing`=5
- `hard`: `bug_fix`=7, `ci_failure`=3, `data_migration`=2, `dependency_friction`=3, `error_localization`=4, `error_recovery`=3, `feature`=8, `multi_turn_change`=7, `multi_turn_tool_debug`=3, `refactor`=4, `sandbox_friction`=1, `stateful_regression`=5
- `hard30`: `bug_fix`=4, `ci_failure`=2, `data_migration`=1, `dependency_friction`=3, `error_localization`=2, `error_recovery`=3, `feature`=4, `multi_turn_change`=3, `multi_turn_tool_debug`=2, `refactor`=1, `sandbox_friction`=1, `stateful_regression`=4

Interpretation: the seed benchmark covers all task categories named in the original design. The hard pool and hard30 paper-facing tier are selected for hidden-grader difficulty and broad category diversity; they are not required to preserve every seed category one-for-one, and missing direct or family-level design categories such as `test_writing` must be treated as coverage boundaries.
