# CodexTrace Submission Package Map

This generated map turns the current evidence into reviewer-facing paper claims.

## Summary

- RQs mapped: 4
- Ready for original thesis: no
- Ready for boundary-result paper: yes
- Package ready for boundary paper: yes
- Unsupported claims: 2
- Partial claims: 2
- Required boundary: ordinary verification-rate lift remains unsupported; no-verify lift is an ablation only

## RQ-To-Evidence Map

| RQ | Status | Evidence | Boundary | Paper action |
| --- | --- | --- | --- | --- |
| RQ1 | satisfied | `docs/failure_taxonomy.md`, `benchmark/detector-fixtures/label-eval.md`, `docs/results_summary.md` | Use the six-label process taxonomy; do not imply the current real pilots cover every label equally. | Frame RQ1 as an observable process taxonomy plus limited natural positives. |
| RQ2 | partial | `benchmark/detector-fixtures/label-eval.md`, `benchmark/hard/pilot/hard30-real/label-eval.md`, `benchmark/pilot/full30-real/process-label-eval.md` | Supported for rule fixtures and observed process positives; not supported for hidden semantic failures. | Report trace-only detection as a boundary result, with hidden semantic false negatives explicit. |
| RQ3 | supported | `docs/results_summary.md`, `docs/hard30_task_diagnosis.md`, `docs/paper_claim_audit.md` | Waste reduction is supported; success lift is pilot-qualified; ordinary verification-rate lift is unsupported. | Lead with hard30 paired waste reduction and treat no-verify verification lift as mechanism ablation only. |
| RQ4 | satisfied | `docs/rq4_signal_audit.md`, `docs/results_summary.md`, `benchmark/hard/pilot/hard30-real/paper-report-labeled.md` | Signals explain observable process positives and the hidden-semantic boundary, not hidden correctness by themselves. | Show the signal table as an explanation of where trace diagnosis works and where task oracles are still required. |

## Unsupported Claims To Avoid

- Harness intervention increases verification rate. Evidence: hard30 verification delta is +0.00 and exact success-check delta is +0.00; process-stress verification delta is +0.00 and exact success-check delta is +0.00; verification-lift verification delta is +0.00 and exact success-check delta is +0.00; verification-lift-v2 verification delta is +0.00 and exact success-check delta is +0.00; stored ordinary/weak-baseline pilots are saturated. Action: Do not claim verification-rate lift for current stored pilots; frame verification as saturated.
- Trace signals explain whether hidden semantic failures will fail. Evidence: hard30 verification-rate signal delta is +0.00; unresolved-error delta is +0.00. Action: Say process signals explain the detector boundary, not hidden correctness.

## Partial Claims Requiring Qualifiers

- Harness intervention increases success rate. Evidence: hard10 success delta is +0.10; hard30 success delta is +0.00. Action: State that success improves in the early hard10 pilot but is flat on hard30.
- Trace-based process rules detect most failure processes. Evidence: controlled detector fixtures cover 6 labels with micro-F1=1.00; hard30 includes 4 detected repetitive-exploration process positives (F1=1.00); full30 includes sandbox/permission TP=1, FP=0, FN=0, with 2 repetitive-exploration FP in the process-label slice. Hidden semantic recall is 0.00 with FN=30; process-stress hidden semantic FN=2; verification-lift hidden semantic FN=2. Action: Claim rule-level taxonomy coverage and observed process-positive detection; do not claim most real-world outcome failures are detected.

## Required Reviewer Files

- `README.md`
- `docs/submission_package.md`
- `docs/goal_completion_audit.md`
- `docs/verification_lift_next_experiment.md`
- `docs/verification_lift_v2_plan_audit.md`
- `docs/paper_draft.md`
- `docs/claim_text_guard.md`
- `docs/paper_number_guard.md`
- `docs/reviewer_path_audit.md`
- `docs/results_summary.md`
- `docs/paper_claim_audit.md`
- `docs/thesis_readiness.md`
- `docs/rq4_signal_audit.md`
- `docs/hard30_task_diagnosis.md`
- `docs/reproducibility_checklist.md`
