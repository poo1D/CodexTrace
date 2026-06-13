# Thesis Revision Decision

This generated decision memo records how the original thesis should be revised given the current evidence.

## Verdict

- Ready: yes
- Decision: revise_to_boundary_result_paper
- Ready for original thesis: no
- Ready for boundary-result paper: yes
- Claim revision required: yes
- Additional ordinary-baseline experiment required: no
- Ordinary verification-rate lift supported: no
- Recommended thesis: Coding-agent traces can diagnose observable multi-turn process failures and quantify harness-level waste reduction, but ordinary Codex baselines already verify on these small tasks, so verification-rate lift should be reported as a negative boundary result.

## Claim Decisions

| Claim area | Decision | Paper framing | Evidence |
| --- | --- | --- | --- |
| `failure_taxonomy` | keep | Use the six-label process taxonomy as a contribution. | docs/failure_taxonomy.md contains 6 target process labels. |
| `trace_rule_detection` | narrow | Claim trace-only rules detect observable process positives and expose hidden-semantic limits. | controlled detector fixtures cover 6 labels with micro-F1=1.00; hard30 repetitive_exploration detector has TP=4, FP=0, FN=0; full30 sandbox_permission_deadlock has TP=1, FP=0, FN=0; full30 process-label repetitive_exploration has FP=2; hidden_semantic_edge_case recall=0.00. |
| `verification_rate_lift` | drop_as_finding | Report saturated ordinary baselines as a negative result and limitation. | hard30 verification delta is +0.00 and exact success-check delta is +0.00; process-stress verification delta is +0.00 and exact success-check delta is +0.00; verification-lift verification delta is +0.00 and exact success-check delta is +0.00; verification-lift-v2 verification delta is +0.00 and exact success-check delta is +0.00; stored ordinary/weak-baseline pilots are saturated. |
| `no_verify_ablation` | keep_as_mechanism_check | Use only as an auxiliary mechanism check, not as ordinary-baseline evidence. | mechanism check only; not an ordinary baseline |
| `waste_reduction` | keep | Lead RQ3 with paired hard30 waste reduction and supporting pilots. | hard30 repeated tool calls change -3.73, token usage -98656.8; process-stress repeated tool calls change -0.92, token usage -23868.4; verification-lift repeated tool calls change -0.75, token usage -4661.8; verification-lift-v2 repeated tool calls change -3.12, token usage -39165.2. |
| `success_lift` | qualify | Report hard10 lift as pilot-qualified and hard30 as flat. | hard10 success delta is +0.10; hard30 success delta is +0.00. |
| `rq4_signals` | narrow | Explain observable process failure signals and the hidden-semantic boundary, not all correctness failures. | RQ4 signal audit ready=True; hard30 hidden failures have verification delta +0.00 and unresolved-error delta +0.00, while real process positives have large repeated-call, token, failure-score, command-failure, or recover-phase deltas. |

Interpretation: the paper can be submitted as a boundary-result artifact if it drops the ordinary verification-rate-lift finding, keeps the no-verify ablation separate, and leads RQ3 with waste reduction rather than verification-rate lift.
