# Verification-Lift Stress Tier

This tier is a targeted experiment for the original CodexTrace thesis gap where existing real pilots have saturated verification rates.

It reuses materialized process-stress fixtures but changes the harness prompt contrast:

- `baseline`: a fast normal workflow that permits inspection-only completion when the fix looks obvious.
- `intervention`: an evidence-gated workflow that requires running the visible success check and citing the result.

The tier is not a replacement for the ordinary hard30 baseline. Its purpose is to test whether harness-level evidence gates can lift verification behavior when the baseline prompt leaves verification optional.

Acceptance criteria for a publishable auxiliary result:

- at least 8 tasks and 16 real Codex JSONL runs,
- baseline/intervention pairs for every task,
- successful materialized fixtures and graders,
- intervention verification rate greater than baseline verification rate,
- process-label recall reported for `verification_gap` and `premature_completion`.
