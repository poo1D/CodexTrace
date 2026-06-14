# Demo Audit

This generated audit runs the reviewer-facing offline demo script and checks that it emits JSON and Markdown diagnosis artifacts with traceable failure findings.

## Summary

- Ready: yes
- Script: `scripts/demo.sh`
- Exit code: 0
- Expected findings covered: 5 / 5
- Findings with event IDs: 5 / 5
- Stdout checks covered: 5 / 5
- Output checks covered: 5 / 5

## Finding Coverage

| Finding | Covered |
| --- | --- |
| `verification_gap` | yes |
| `command_failure_unhandled` | yes |
| `repeated_search_or_read` | yes |
| `sandbox_or_permission_block` | yes |
| `premature_completion` | yes |

## Demo Output Checks

| Check | Covered |
| --- | --- |
| `json_report` | yes |
| `markdown_report` | yes |
| `diagnosis_object` | yes |
| `event_ids` | yes |
| `markdown_title` | yes |

Interpretation: this audit proves the committed offline demo path works without re-running Codex. It does not start the optional Web UI.
