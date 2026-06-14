# CLI Surface Audit

This generated audit smoke-tests the offline CLI entry points used to normalize traces, diagnose failures, and regenerate paper-facing research artifacts.

## Summary

- Ready: yes
- CLI commands covered: 9 / 9
- Parser subcommands present: 9 / 9
- Documentation checks covered: 6 / 6
- CLI source: `codex_trace/cli.py`
- README: `README.md`
- Reproducibility checklist: `docs/reproducibility_checklist.md`

## Command Smoke Tests

| Command | Exit | Outputs | Expected text | Covered |
| --- | ---: | --- | --- | --- |
| `collect` | 0 | yes | yes | yes |
| `diagnose_json` | 0 | yes | yes | yes |
| `research_prompt` | 0 | yes | yes | yes |
| `research_aggregate` | 0 | yes | yes | yes |
| `research_label_template` | 0 | yes | yes | yes |
| `research_evaluate_labels` | 0 | yes | yes | yes |
| `research_paper_report` | 0 | yes | yes | yes |
| `research_summary` | 0 | yes | yes | yes |
| `research_run_dry` | 0 | yes | yes | yes |

## Subcommand Checks

| Subcommand | Present |
| --- | --- |
| `collect` | yes |
| `diagnose` | yes |
| `research_prompt` | yes |
| `research_aggregate` | yes |
| `research_label_template` | yes |
| `research_evaluate_labels` | yes |
| `research_paper_report` | yes |
| `research_summary` | yes |
| `research_run` | yes |

Interpretation: this audit proves the offline CLI surface can regenerate representative trace, diagnosis, aggregate, label, paper-report, summary, and dry-run harness artifacts from committed inputs. It does not execute live Codex collection.
