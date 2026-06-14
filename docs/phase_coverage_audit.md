# Phase Coverage Audit

This generated audit checks that phase segmentation is represented in the schema, paper draft, hard30 run rows, and RQ4 signal outputs.

## Summary

- Ready: yes
- Phases covered: 7 / 7
- RQ4 core phase signals: 4 / 4
- Manifest checked: `benchmark/hard/pilot/hard30-real/runs.jsonl`
- Paper draft: `docs/paper_draft.md`
- Results summary: `docs/results_summary.json`

## Phase Coverage

| Phase | Schema | Paper draft | Run key | RQ4 signal | Covered |
| --- | --- | --- | --- | --- | --- |
| `setup` | yes | yes | `phase_setup_events` yes | no | yes |
| `inspect` | yes | yes | `phase_inspect_events` yes | yes | yes |
| `edit` | yes | yes | `phase_edit_events` yes | yes | yes |
| `verify` | yes | yes | `phase_verify_events` yes | yes | yes |
| `recover` | yes | yes | `phase_recover_events` yes | yes | yes |
| `complete` | yes | yes | `phase_complete_events` yes | no | yes |
| `other` | yes | yes | `phase_other_events` yes | no | yes |

Interpretation: all phases must exist in the schema, paper draft, and run-level hard30 rows. RQ4 is required to expose the core process phases inspect, edit, verify, and recover as explanatory signals; setup, complete, and other remain run-level accounting fields.
