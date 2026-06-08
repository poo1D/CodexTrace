# CodexTrace Paper Claim Audit

This generated audit maps the original thesis-style claims to the evidence currently stored in the repository.

## Summary

- Claims audited: 8
- Supported: 4
- Partial: 1
- Unsupported: 3
- Hard30 artifact: 30 tasks, 60 runs, 30 failures, readiness=yes
- Hard30 detected repetitive-exploration positives: TP=4, FN=0

## Claim Status

| Claim | Status | Evidence | Writing action |
| --- | --- | --- | --- |
| CodexTrace is a GPU-free offline parser and diagnosis engine for Codex JSONL traces. | supported | Parser, diagnosis CLI, reports, demo traces, and CI-tested package exist; stored pilots can be analyzed without Codex or GPU. | Keep as a headline artifact claim. |
| The benchmark has 30-50 coding tasks with baseline and intervention traces. | supported | full30 has 30 seed tasks; hard30 has 30 selected hard tasks and 60 real runs; readiness=True. | Describe as a 30-task paper-facing hard artifact plus a 30-task seed pilot, not as a broad benchmark. |
| Harness intervention increases success rate. | partial | hard10 success delta is +0.10; hard30 success delta is +0.00. | State that success improves in the early hard10 pilot but is flat on hard30. |
| Harness intervention increases verification rate. | unsupported | hard30 verification delta is +0.00; both baseline and intervention verification rates are already 1.00. | Do not claim verification-rate lift for current stored pilots; frame verification as saturated. |
| Harness intervention reduces repeated tool-call and token waste. | supported | hard30 repeated tool calls change -3.73; token usage changes -98656.8; paired improvements are repeated=26/30, token=26/30. | Use as the strongest current RQ3 result. |
| Trace-based process rules detect most failure processes. | unsupported | hard30 includes 4 detected repetitive-exploration process positives (F1=1.00), but hidden semantic recall is 0.00 with FN=30. | Claim process-positive detection only for observed process labels; do not claim most overall failures are detected. |
| Trace signals explain whether hidden semantic failures will fail. | unsupported | hard30 verification-rate signal delta is +0.00; unresolved-error delta is +0.00. | Say process signals explain the detector boundary, not hidden correctness. |
| Strong task-level oracles remain necessary. | supported | hard30 visible traces often verify cleanly, but hidden graders expose 30 failures and 30 trace-only false negatives. | Keep as a limitation and contribution. |

## Paper Writing Rule

Use `supported` claims as paper/CV headline claims. Use `partial` claims only with pilot qualifiers. Do not state `unsupported` claims as findings; turn them into limitations or next experiments.
