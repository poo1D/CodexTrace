# Rule Implementation Audit

This generated audit checks that each paper-facing taxonomy label is backed by an implemented diagnosis rule and a paper-label alias.

## Summary

- Ready: yes
- Rules covered: 6 / 6
- Context drift v1 proxy disclosed: yes
- Diagnosis source: `codex_trace/diagnose.py`
- Label alias source: `codex_trace/research.py`

## Rule Coverage

| Label | Finding code | Scope | Code | Markers | Alias | Docs | Covered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `verification_gap` | `verification_gap` | `direct` | yes | yes | yes | yes | yes |
| `unrecovered_tool_error` | `command_failure_unhandled` | `direct` | yes | yes | yes | yes | yes |
| `repetitive_exploration` | `repeated_search_or_read` | `direct` | yes | yes | yes | yes | yes |
| `context_drift` | `long_context_no_progress` | `v1_proxy` | yes | yes | yes | yes | yes |
| `premature_completion` | `premature_completion` | `direct` | yes | yes | yes | yes | yes |
| `sandbox_permission_deadlock` | `sandbox_or_permission_block` | `direct` | yes | yes | yes | yes | yes |

Interpretation: this audit checks implementation coverage and label mapping. It also records that `context_drift` is a v1 proxy based on high context with weak progress, not a full semantic task-keyword drift detector.
