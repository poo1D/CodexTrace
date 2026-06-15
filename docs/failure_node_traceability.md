# Failure Node Traceability Audit

This generated audit checks that diagnosis findings carry trace event IDs from parser output through JSON reports, Markdown reports, and the Web UI highlight path.

## Summary

- Ready: yes
- Demo trace: `demo/failing-codex-trace.jsonl`
- Demo findings: 5
- Expected demo findings present: 5 / 5
- Findings with event IDs: 5 / 5
- JSON findings with event IDs: 5 / 5
- Markdown Event IDs lines: 5 / 5
- Highlighted event nodes: 6
- Benchmark manifest: `benchmark/hard/pilot/hard30-real/runs.jsonl`
- Benchmark traces checked: 60
- Benchmark findings with event IDs: 4 / 4
- Benchmark findings missing event IDs: 0

## Source Path Checks

| Check | Covered |
| --- | --- |
| `schema_event_ids` | yes |
| `diagnose_event_ids` | yes |
| `markdown_event_ids` | yes |
| `web_flatmap_event_ids` | yes |
| `web_highlight_class` | yes |
| `web_highlight_style` | yes |

## Finding Node Coverage

| Finding | Severity | Evidence | Recommendation | Event IDs | Covered |
| --- | --- | ---: | --- | ---: | --- |
| `command_failure_unhandled` | `high` | 2 | yes | 2 | yes |
| `verification_gap` | `high` | 1 | yes | 1 | yes |
| `premature_completion` | `high` | 1 | yes | 1 | yes |
| `repeated_search_or_read` | `medium` | 1 | yes | 2 | yes |
| `sandbox_or_permission_block` | `medium` | 1 | yes | 1 | yes |

## Benchmark Finding Counts

| Finding | Count |
| --- | ---: |
| `repeated_search_or_read` | 4 |

Interpretation: this audit covers process-finding node traceability. It does not claim that hidden semantic failures have visible failure nodes; those remain a separate detector-boundary result.
