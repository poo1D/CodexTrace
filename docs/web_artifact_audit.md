# Web Artifact Audit

This generated audit checks that the committed Web replay fixture matches the current demo diagnosis and that the TypeScript UI preserves the event-ID highlight path.

## Summary

- Ready: yes
- Trace: `demo/failing-codex-trace.jsonl`
- Web report: `web/public/report.json`
- Findings with matching event IDs: 5 / 5
- Report checks covered: 5 / 5
- Source checks covered: 9 / 9

## Finding Event-ID Coverage

| Finding | Present | Event IDs match |
| --- | --- | --- |
| `command_failure_unhandled` | yes | yes |
| `verification_gap` | yes | yes |
| `premature_completion` | yes | yes |
| `repeated_search_or_read` | yes | yes |
| `sandbox_or_permission_block` | yes | yes |

## UI Source Checks

| Check | Covered |
| --- | --- |
| `fetch_report` | yes |
| `fallback_report` | yes |
| `finding_event_flatmap` | yes |
| `highlighted_class` | yes |
| `highlighted_style` | yes |
| `responsive_css` | yes |
| `vite_build_script` | yes |
| `react_dependency` | yes |
| `root_mount` | yes |

Interpretation: this audit covers the committed static Web artifact and source path. It does not install npm dependencies or start the Vite dev server.
