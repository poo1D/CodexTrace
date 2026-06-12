# Verification-Lift V2 Ordinary-Baseline Tier

This tier is the next experiment for the unresolved original CodexTrace thesis claim that harness intervention can raise verification behavior under a non-ablation baseline.

It reuses materialized process-stress fixtures but changes the prompt contrast from the first verification-lift tier:

- `baseline`: an ordinary coding-agent workflow. The visible success check is available, but verification is left to the agent's normal judgment.
- `intervention`: an evidence-gated workflow that requires running the visible success check and citing the result.

This tier is deliberately separate from `benchmark/verification-ablation`, whose baseline forbids verification. A no-verify ablation can show harness control, but it cannot close the ordinary-baseline verification-lift claim.

Acceptance criteria for closing the original verification-lift claim:

- at least 8 tasks and 16 real Codex JSONL runs,
- baseline/intervention pairs for every task,
- baseline prompt does not forbid verification and does not explicitly tell the agent to skip verification,
- intervention prompt requires the visible success check,
- intervention verification rate or exact visible success-check verification rate is greater than the non-ablation baseline,
- if broad and exact verification remain saturated, report the result as a boundary finding and use verification-depth metrics only as secondary evidence.
