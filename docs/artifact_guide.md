# CodexTrace Artifact Guide

This guide is the fastest path through the repository for reviewers,
interviewers, or collaborators who want to understand what CodexTrace proves
without re-running the full Codex collection pipeline.

## What This Artifact Is

CodexTrace is a GPU-free research artifact for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

It treats coding-agent execution traces as first-class evidence. The artifact
parses `codex exec --json` JSONL traces, normalizes events, segments them into
tool-use phases, detects process-level failure patterns, and aggregates
baseline-vs-intervention experiments.

The core claim is intentionally narrow: trace analysis can expose observable
process failures and process waste, but it does not replace strong task-level
oracles for hidden semantic correctness.

## Fifteen-Minute Review Path

1. Read the project snapshot in `README.md`.
2. Open the paper draft in `docs/paper_draft.md`.
3. Inspect generated results in `docs/results_summary.md`.
4. Inspect the compact actual headline table in `docs/headline_results.md`.
5. Inspect the thesis revision decision in `docs/thesis_revision_decision.md`.
6. Inspect validity threats and safe wording in `docs/validity_threats.md`.
7. Inspect task-level hard30 repairs, regressions, and double failures in
   `docs/hard30_task_diagnosis.md`.
8. Check safe paper-claim framing in `docs/submission_package.md`.
9. Check thesis-level support status in `docs/paper_claim_audit.md`.
10. Check drift guards in `docs/claim_text_guard.md` and
   `docs/paper_number_guard.md`.
11. Check no-verify ablation scaffold coverage in
   `docs/verification_ablation_plan_audit.md`.
12. Check detector precision/recall evidence in
   `docs/detector_evaluation_audit.md`.
13. Check diagnosis-rule implementation coverage in
   `docs/rule_implementation_audit.md`.
14. Check Run/Step schema-field mapping in `docs/schema_field_audit.md`.
15. Check diagnosis-node traceability in `docs/failure_node_traceability.md`.
16. Check phase segmentation coverage in `docs/phase_coverage_audit.md`.
17. Check task-category coverage in `docs/task_category_coverage.md`.
18. Check harness protocol coverage in `docs/harness_protocol_audit.md`.
19. Check failure-taxonomy coverage in `docs/failure_taxonomy_audit.md`.
20. Check related-work positioning coverage in `docs/related_work_audit.md`.
21. Check paper reference discoverability in `docs/bibliography_audit.md`.
22. Check abstract-level evidence coverage in `docs/paper_abstract_audit.md`.
23. Check contribution-claim coverage in `docs/paper_contribution_audit.md`.
24. Check paper structure and RQ coverage in `docs/paper_structure_audit.md`.
25. Check metric coverage in `docs/metric_coverage_audit.md`.
26. Check reproduction command coverage in `docs/reproducibility_audit.md`.
27. Check claim-to-evidence mapping in `docs/reproducibility_checklist.md`.
28. Run the offline demo:

```bash
./scripts/demo.sh
```

29. Optionally open the visual replay UI:

```bash
cd web
npm install
npm run dev
```

## Main Evidence

| Question | Evidence |
| --- | --- |
| RQ1: What failure modes are observable? | `docs/failure_taxonomy.md`, `docs/paper_draft.md` |
| RQ2: Can trace rules detect failures? | `benchmark/hard/pilot/hard30-real/label-eval.md` |
| Is detector evaluation evidence consolidated? | `docs/detector_evaluation_audit.md` |
| Are diagnosis rules implemented for each taxonomy label? | `docs/rule_implementation_audit.md` |
| Is the no-verify ablation scaffold ready? | `docs/verification_ablation_plan_audit.md` |
| Is the normalized trace schema mapped to code? | `docs/schema_field_audit.md` |
| Do diagnosis findings trace to highlighted event nodes? | `docs/failure_node_traceability.md` |
| Is phase segmentation covered? | `docs/phase_coverage_audit.md` |
| Do benchmark tasks cover the planned task types? | `docs/task_category_coverage.md` |
| Do intervention prompts encode the harness protocol? | `docs/harness_protocol_audit.md` |
| Is the six-label taxonomy covered? | `docs/failure_taxonomy_audit.md` |
| Is the related-work positioning covered? | `docs/related_work.md`, `docs/related_work_audit.md` |
| Are paper references discoverable? | `docs/bibliography_audit.md` |
| Does the abstract match the evidence boundary? | `docs/paper_abstract_audit.md` |
| Are the contribution claims evidence-backed? | `docs/paper_contribution_audit.md` |
| Does the paper draft cover the required structure? | `docs/paper_draft.md`, `docs/paper_structure_audit.md` |
| RQ3: Do harness interventions help? | `docs/results_summary.md` RQ3 tables |
| What headline table should the paper use? | `docs/headline_results.md` |
| How should the original thesis be revised? | `docs/thesis_revision_decision.md` |
| What validity threats constrain the claims? | `docs/validity_threats.md` |
| RQ4: Which signals explain failure? | `docs/results_summary.md` RQ4 trace-signal table |
| Are all planned metrics reported? | `docs/metric_coverage_audit.md` |
| Are reproduction commands complete? | `docs/reproducibility_checklist.md`, `docs/reproducibility_audit.md` |
| Which tasks get lost? | `docs/hard30_task_diagnosis.md` |
| Which claims are safe to write? | `docs/submission_package.md`, `docs/paper_claim_audit.md` |
| Did paper text drift from evidence? | `docs/claim_text_guard.md`, `docs/paper_number_guard.md` |

The stored pilots currently include:

| Pilot | Tasks | Runs | Role |
| --- | ---: | ---: | --- |
| full30 | 30 | 60 | Measures process-waste reduction when outcomes are saturated. |
| hard10 | 10 | 20 | Early hard-tier pilot with a small success-rate lift. |
| hard30 | 30 | 60 | Paper-facing hard-tier artifact with hidden-grader failures and paired waste deltas. |
| process-stress | 12 | 24 | Observable-process stress slice with flat success and lower waste. |
| verification-lift | 8 | 16 | Weak-baseline verification-rate stress test; negative for verification lift. |
| verification-lift-v2 | 8 | 16 | Ordinary-baseline verification-rate retest; negative for verification lift. |
| verification-ablation | 4 | 8 | No-verify mechanism ablation; not ordinary-baseline evidence. |

## Reproduce Result Tables

The stored traces can be analyzed without a GPU and without re-running Codex:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research summary \
  --markdown-output /tmp/results-summary.md \
  --json-output /tmp/results-summary.json
```

Hard-tier detector evaluation:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research evaluate-labels \
  benchmark/hard/pilot/hard30-real/runs.jsonl \
  benchmark/hard/pilot/hard30-real/manual-labels.jsonl \
  --markdown-output /tmp/hard30-label-eval.md
```

Hard-tier paper report:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research paper-report \
  benchmark/hard/pilot/hard30-real/runs.jsonl \
  --labels benchmark/hard/pilot/hard30-real/manual-labels.jsonl \
  --markdown-output /tmp/hard30-paper-report.md
```

## Current Result Snapshot

| Result | Current evidence |
| --- | --- |
| full30 repeated tool calls | `10.43 -> 7.00` |
| full30 token usage | `218.7k -> 184.8k` |
| hard10 success rate | `70% -> 80%` |
| hard30 repeated tool calls | `12.93 -> 9.20` |
| hard30 token usage | `355.0k -> 256.3k` |
| hard30 double-failure tasks | `14` |
| hard30 repair/regression | `HARD-050` repaired, `HARD-007` regressed |
| process-stress repeated tool calls | `8.08 -> 7.17` |
| verification-lift-v2 verification | `100% -> 100%` |
| verification-lift-v2 repeated tool calls | `8.62 -> 5.50` |
| verification-lift-v2 token usage | `224.6k -> 185.5k` |
| no-verify ablation verification | `0% -> 100%`, mechanism check only |
| hidden semantic detector boundary | `TP=0`, `FP=0`, `FN=30` |
| repetitive exploration detection | `TP=4`, `FP=0`, `FN=0` |

The RQ4 signal table shows why the detector boundary matters:
`verification_rate` and `unresolved_error` do not separate hard30 success and
failure outcomes. The visible traces often look clean; hidden graders reveal
the missed edge cases.

## What To Cite In A CV Or Interview

- Built a GPU-free Codex trace diagnosis system that parses real
  `codex exec --json` runs into a normalized event schema.
- Designed a 204-run benchmark across seed, hard, process-stress,
  verification-lift, verification-lift-v2, and no-verify ablation tiers, including a 30-task
  hard-tier artifact with hidden graders.
- Measured harness intervention effects on real Codex runs: reduced repeated
  tool calls and token usage, with hard10 success improving from 70% to 80%
  and hard30 token usage improving in 26 of 30 paired tasks.
- Documented a negative boundary result: deterministic trace rules miss hidden
  semantic failures when visible process traces look clean.

## Known Limits

- The artifact studies Codex CLI traces, not all coding agents.
- The hard30 artifact has 30 selected tasks, but repeated trials are still
  needed before treating the measured deltas as population estimates.
- The detectors are deterministic and interpretable, but incomplete.
- Hidden semantic correctness still requires strong task-level oracles.

## Next Research Step

The strongest next step is repeated hard30 trials plus richer manual labels for
observable process failures. The current hard30 artifact is complete and
submission-ready as a pilot artifact, but its failures are dominated by hidden
semantic edge cases, so broader RQ1/RQ2 taxonomy claims need either more
process-failure-heavy tasks or a lightweight semantic analysis layer.

See `docs/submission_readiness_plan.md` for the concrete workstreams and
decision gate for moving from the current pilot artifact to a stronger paper
submission. See `docs/hard_tier_expansion_blueprint.md` for the implemented
`HARD-011` through `HARD-050` fixtures and hard30 pilot selection plan.
