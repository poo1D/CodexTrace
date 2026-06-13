# CodexTrace Thesis Readiness

This audit maps the original thesis objective to the current repository evidence.

## Summary

- Requirements audited: 7
- Satisfied: 6
- Partial: 0
- Missing: 1
- Ready for original thesis: no
- Ready for boundary-result paper: yes

## Requirement Status

| ID | Status | Requirement | Evidence | Gap / action |
| --- | --- | --- | --- | --- |
| taxonomy | satisfied | Define observable multi-turn coding-agent failure modes. | docs/failure_taxonomy.md contains 6 target process labels. | None for paper scope. |
| benchmark | satisfied | Provide a 30-50 task Codex JSONL benchmark with baseline and intervention traces. | hard30 has 30 tasks and 60 runs; readiness=True. | None for the current 30-task paper artifact. |
| codextrace | satisfied | Implement an offline parser and diagnosis engine without training or GPU. | Stored traces can be parsed, diagnosed, aggregated, and rendered from repository artifacts. | None for artifact scope. |
| process_rule_detection | satisfied | Show that trace-based rules detect observable failure processes. | controlled detector fixtures cover 6 labels with micro-F1=1.00; hard30 repetitive_exploration detector has TP=4, FP=0, FN=0; full30 sandbox_permission_deadlock has TP=1, FP=0, FN=0; full30 process-label repetitive_exploration has FP=2; hidden_semantic_edge_case recall=0.00. | Rule-level taxonomy coverage is satisfied; real-pilot natural positives still cover only part of the taxonomy and should be described as limited. |
| verification_lift | missing | Show that harness intervention increases verification rate. | verification is saturated in stored pilots: full30=1.00->1.00 (exact=1.00->1.00), hard10=1.00->1.00 (exact=1.00->1.00), hard30=1.00->1.00 (exact=1.00->1.00), process-stress=1.00->1.00 (exact=1.00->1.00), verification-lift=1.00->1.00 (exact=1.00->1.00), verification-lift-v2=1.00->1.00 (exact=1.00->1.00). | The ordinary and weak-baseline pilots are negative results; the no-verify ablation shows the harness can lift verification from 0.00 to 1.00, and exact success-check verification from 0.00 to 1.00, but this is not an ordinary-baseline result. |
| success_or_waste | satisfied | Show intervention improves success and/or reduces tool-call and token waste. | hard10 success delta=+0.10; hard30 success delta=+0.00; hard30 repeated calls delta=-3.73; token delta=-98656.8; paired improvements repeated=26/30, token=26/30; task diagnosis: double failures=14, repairs=1, regressions=1; process-stress success delta=+0.00, repeated calls=8.08->7.17, token usage=209.0k->185.1k; verification-lift success delta=+0.00, repeated calls=6.12->5.38, token usage=176.8k->172.2k; verification-lift-v2 success delta=+0.00, repeated calls=8.62->5.50, token usage=224.6k->185.5k. | Repeat hard30 or add a process-stress tier if a stable success-rate lift is required. |
| rq4_explanation | satisfied | Identify trace signals that explain whether a run fails. | hard30 hidden failures are not separated by process signals: verification delta=+0.00, exact success-check delta=+0.00, unresolved-error delta=+0.00; repetitive_exploration positives are explained by repeated calls, token usage, and failure score; RQ4 signal audit ready=True. | Boundary-style RQ4 is supported: process signals explain observable process failures, while hidden semantic correctness remains a limitation. |

## Next Experiment

Name: `optional process-stress expansion`

Future extension for broader natural process-positive coverage; the current boundary-result paper no longer depends on another verification-lift run.

Current scaffold: 12 materialized tasks in `benchmark/process-stress/tasks.jsonl`; audit ready=yes.

Current process-stress pilot: 12 task(s), 24 run(s), success 0.92->0.92, verification 1.00->1.00, exact success-check 1.00->1.00, repeated calls 8.08->7.17, token usage 209.0k->185.1k.

- Use only if expanding beyond the current boundary paper or seeking more natural process-positive labels.
- 10-15 tasks whose visible success checks are weak enough that baseline may skip or under-run verification.
- At least two tasks each targeting verification_gap, unrecovered_tool_error, premature_completion, context_drift, repetitive_exploration, and sandbox_permission_deadlock.
- Baseline/intervention Codex JSONL traces with manual process labels for every failure and high-waste success.
- Acceptance gate for future expansion: process-label recall >= 0.70 on observable labels, plus verification-depth improvement if verification rate remains saturated.

## Verification-Lift Experiment

Name: `verification-lift tier`

Directly test the missing verification-rate-lift claim under a prompt contrast where baseline verification is optional and intervention verification is evidence-gated.

Current scaffold: 8 task(s) in `benchmark/verification-lift/tasks.jsonl` with prompts in `benchmark/verification-lift/prompts`; audit ready=yes.

Current verification-lift pilot: 8 task(s), 16 run(s), verification 1.00->1.00, exact success-check 1.00->1.00, success 0.88->0.88.

- The first 8-task pilot is complete and is a negative result for verification-rate lift.
- If preserving the original verification-lift claim, design a stronger ablation where baseline verification is genuinely absent.
- Otherwise revise the thesis to claim robust waste reduction under already-saturated verification behavior.
- Report the existing verification-lift pilot as an auxiliary stress result, not a replacement for the ordinary hard30 baseline.

## Verification-Lift-V2 Experiment

Name: `verification-lift-v2 tier`

Ordinary-baseline rerun of the missing verification-rate-lift claim.

Current scaffold: tasks in `benchmark/verification-lift-v2/tasks.jsonl` with prompts in `benchmark/verification-lift-v2/prompts`.

Current verification-lift-v2 pilot: 8 task(s), 16 run(s), verification 1.00->1.00, exact success-check 1.00->1.00, success 0.88->0.88, repeated calls 8.62->5.50, token usage 224.6k->185.5k.

- The 8-task ordinary-baseline v2 pilot is complete and is a negative result for verification-rate lift.
- Use it as stronger evidence that ordinary Codex baselines already verify on these small tasks.
- Report the clear waste reduction separately from verification-rate lift.

## Verification Ablation Experiment

Name: `verification-ablation tier`

Auxiliary mechanism check: explicit no-verify baseline versus evidence-gated intervention.

Current scaffold: 4 task(s) in `benchmark/verification-ablation/tasks.jsonl` with prompts in `benchmark/verification-ablation/prompts`; audit ready=yes.

Current verification-ablation pilot: 4 task(s), 8 run(s), verification 0.00->1.00, exact success-check 0.00->1.00, success 0.75->0.75, failure score 61.25->0.00.

- Treat as an ablation only, not as the ordinary Codex baseline.
- Use to support harness control over verification behavior.
- Do not use it to mark the original verification-lift claim complete.
