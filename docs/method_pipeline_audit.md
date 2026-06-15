# Method Pipeline Audit

This generated audit checks that the CodexTrace method pipeline described in the paper maps to source code and offline CLI smoke outputs.

## Summary

- Ready: yes
- Pipeline stages covered: 7 / 7
- CLI method commands covered: 4 / 4
- Smoke checks covered: 6 / 6
- Paper draft: `docs/paper_draft.md`

## Pipeline Stage Mapping

| Stage | Paper | Source | Covered |
| --- | --- | --- | --- |
| `codex_jsonl_trace_input` | yes | `demo/real-codex-run.jsonl` | yes |
| `jsonl_event_parser` | yes | `codex_trace/parser.py` | yes |
| `normalized_trace_schema` | yes | `codex_trace/schema.py` | yes |
| `phase_segmentation` | yes | `codex_trace/parser.py` | yes |
| `failure_pattern_detector` | yes | `codex_trace/diagnose.py` | yes |
| `diagnosis_report` | yes | `codex_trace/report.py` | yes |
| `baseline_vs_intervention_comparison` | yes | `codex_trace/research.py` | yes |

## CLI Checks

| Command | Covered |
| --- | --- |
| `collect_command` | yes |
| `diagnose_command` | yes |
| `aggregate_command` | yes |
| `paper_report_command` | yes |

## Smoke Checks

| Check | Covered |
| --- | --- |
| `collect_normalized_trace` | yes |
| `collect_phase_segmentation` | yes |
| `diagnose_failure_patterns` | yes |
| `diagnose_event_ids` | yes |
| `aggregate_baseline_intervention` | yes |
| `aggregate_report_output` | yes |

## Smoke Metrics

- Diagnosis findings: 5
- Findings with event IDs: 5 / 5
- Aggregate run rows: 4
- Aggregate prompt types: baseline, intervention

Interpretation: this audit exercises the offline parser, diagnosis, and aggregate surfaces on committed inputs. It does not execute live Codex collection.
