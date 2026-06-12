# CodexTrace Paper Claim Audit

This generated audit maps the original thesis-style claims to the evidence currently stored in the repository.

## Summary

- Claims audited: 10
- Supported: 6
- Partial: 2
- Unsupported: 2
- Hard30 artifact: 30 tasks, 60 runs, 30 failures, readiness=yes
- Hard30 detected repetitive-exploration positives: TP=4, FN=0
- Full30 detected sandbox/permission positives: TP=1, FP=0, FN=0
- Controlled detector fixture labels: 6, micro-F1=1.00
- Process-stress artifact: 12 tasks, 24 runs, 2 failures, success delta=+0.00
- Verification-lift artifact: 8 tasks, 16 runs, 2 failures, verification delta=+0.00, exact success-check delta=+0.00
- Verification-ablation artifact: 4 tasks, 8 runs, 2 failures, verification delta=+1.00, exact success-check delta=+1.00
- RQ4 signal audit ready: yes

## Claim Status

| Claim | Status | Evidence | Writing action |
| --- | --- | --- | --- |
| CodexTrace is a GPU-free offline parser and diagnosis engine for Codex JSONL traces. | supported | Parser, diagnosis CLI, reports, demo traces, and CI-tested package exist; stored pilots can be analyzed without Codex or GPU. | Keep as a headline artifact claim. |
| The benchmark has 30-50 coding tasks with baseline and intervention traces. | supported | full30 has 30 seed tasks; hard30 has 30 selected hard tasks and 60 real runs; readiness=True. | Describe as a 30-task paper-facing hard artifact plus a 30-task seed pilot, not as a broad benchmark. |
| Harness intervention increases success rate. | partial | hard10 success delta is +0.10; hard30 success delta is +0.00. | State that success improves in the early hard10 pilot but is flat on hard30. |
| Harness intervention increases verification rate. | unsupported | hard30 verification delta is +0.00 and exact success-check delta is +0.00; process-stress verification delta is +0.00 and exact success-check delta is +0.00; verification-lift verification delta is +0.00 and exact success-check delta is +0.00; stored ordinary/weak-baseline pilots are saturated. | Do not claim verification-rate lift for current stored pilots; frame verification as saturated. |
| Harness constraints can control verification behavior under a no-verify ablation. | supported | verification-ablation verification delta is +1.00; exact success-check delta is +1.00; failure-score delta is -61.25. | Use only as a mechanism ablation, not as ordinary-baseline evidence. |
| Harness intervention reduces repeated tool-call and token waste. | supported | hard30 repeated tool calls change -3.73, token usage -98656.8; process-stress repeated tool calls change -0.92, token usage -23868.4; verification-lift repeated tool calls change -0.75, token usage -4661.8. | Use as the strongest current RQ3 result. |
| Trace-based process rules detect most failure processes. | partial | controlled detector fixtures cover 6 labels with micro-F1=1.00; hard30 includes 4 detected repetitive-exploration process positives (F1=1.00); full30 includes sandbox/permission TP=1, FP=0, FN=0, with 2 repetitive-exploration FP in the process-label slice. Hidden semantic recall is 0.00 with FN=30; process-stress hidden semantic FN=2; verification-lift hidden semantic FN=2. | Claim rule-level taxonomy coverage and observed process-positive detection; do not claim most real-world outcome failures are detected. |
| Trace signals explain whether hidden semantic failures will fail. | unsupported | hard30 verification-rate signal delta is +0.00; unresolved-error delta is +0.00. | Say process signals explain the detector boundary, not hidden correctness. |
| Trace signals explain observable process failures and the hidden-semantic boundary. | supported | RQ4 signal audit ready=True; hard30 hidden failures have verification delta +0.00 and unresolved-error delta +0.00, while real process positives have large repeated-call, token, failure-score, command-failure, or recover-phase deltas. | Use as the paper's RQ4 framing. |
| Strong task-level oracles remain necessary. | supported | hard30 visible traces often verify cleanly, but hidden graders expose 30 failures and 30 trace-only false negatives; process-stress adds 2 failures and 2 false negatives; verification-lift adds 2 failures and 2 false negatives. | Keep as a limitation and contribution. |

## Paper Writing Rule

Use `supported` claims as paper/CV headline claims. Use `partial` claims only with pilot qualifiers. Do not state `unsupported` claims as findings; turn them into limitations or next experiments.
