# Label Provenance Audit

This generated audit checks that hard30 label templates, manual labels, detector-label evaluation, and the labeled paper report agree on row identity, schema fields, outcomes, trace paths, and evaluation summaries.

## Summary

- Ready: yes
- Run rows: 60 / 60
- Template label rows: 60 / 60
- Manual label rows: 60 / 60
- Failure rows with labels: 30 / 30
- Failure rows with notes: 30 / 30
- Label fields covered: 8 / 8
- Label-eval summary matches paper report: 5 / 5
- Label set matches paper report: yes
- Run directory: `benchmark/hard/pilot/hard30-real`

## Manual Label Tags

| Tag | Count |
| --- | ---: |
| `hidden_semantic_edge_case` | 30 |
| `repetitive_exploration` | 4 |

## Label Schema Fields

| Field | Template | Manual | Covered |
| --- | --- | --- | --- |
| `task_id` | yes | yes | yes |
| `prompt_type` | yes | yes | yes |
| `outcome` | yes | yes | yes |
| `trace_path` | yes | yes | yes |
| `failure_score` | yes | yes | yes |
| `failure_tags` | yes | yes | yes |
| `suggested_tags` | yes | yes | yes |
| `notes` | yes | yes | yes |

## Consistency Checks

- Missing template keys: 0
- Missing manual keys: 0
- Extra template keys: 0
- Extra manual keys: 0
- Outcome mismatches: 0
- Trace path mismatches: 0
- Unknown tags: 0

Interpretation: this audit proves label-file provenance and evaluation-file consistency for the committed hard30 artifact. It does not prove inter-annotator agreement or relabel the traces.
