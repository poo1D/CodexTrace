# Rule Implementation Audit

This generated audit checks that each paper-facing taxonomy label is backed by an implemented diagnosis rule and a paper-label alias.

## Summary

- Ready: yes
- Rules covered: 6 / 6
- Context drift v1 proxy disclosed: yes
- Real-pilot-positive rules: 2 / 6
- Ablation-positive rules: 2 / 6
- Fixture-only rules: 2 / 6
- Diagnosis source: `codex_trace/diagnose.py`
- Label alias source: `codex_trace/research.py`
- Detector evidence source: `docs/detector_evaluation_audit.json`

## Rule Coverage

| Label | Finding code | Scope | Evidence tier | Real TP | Ablation TP | Code | Markers | Alias | Docs | Covered |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| `verification_gap` | `verification_gap` | `direct` | `ablation-positive` | 0 | 4 | yes | yes | yes | yes | yes |
| `unrecovered_tool_error` | `command_failure_unhandled` | `direct` | `fixture-only` | 0 | 0 | yes | yes | yes | yes | yes |
| `repetitive_exploration` | `repeated_search_or_read` | `direct` | `real-pilot-positive` | 4 | 0 | yes | yes | yes | yes | yes |
| `context_drift` | `long_context_no_progress` | `v1_proxy` | `fixture-only` | 0 | 0 | yes | yes | yes | yes | yes |
| `premature_completion` | `premature_completion` | `direct` | `ablation-positive` | 0 | 3 | yes | yes | yes | yes | yes |
| `sandbox_permission_deadlock` | `sandbox_or_permission_block` | `direct` | `real-pilot-positive` | 1 | 0 | yes | yes | yes | yes | yes |

Interpretation: this audit checks implementation coverage, label mapping, and the detector evidence tier for each rule. It also records that `context_drift` is a v1 proxy based on high context with weak progress, not a full semantic task-keyword drift detector.
