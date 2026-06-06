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
4. Check claim-to-evidence mapping in `docs/reproducibility_checklist.md`.
5. Run the offline demo:

```bash
./scripts/demo.sh
```

6. Optionally open the visual replay UI:

```bash
cd web
npm install
npm run dev
```

## Main Evidence

| Question | Evidence |
| --- | --- |
| RQ1: What failure modes are observable? | `docs/failure_taxonomy.md`, `docs/paper_draft.md` |
| RQ2: Can trace rules detect failures? | `benchmark/hard/pilot/hard10-real/label-eval.md` |
| RQ3: Do harness interventions help? | `docs/results_summary.md` RQ3 tables |
| RQ4: Which signals explain failure? | `docs/results_summary.md` RQ4 trace-signal table |

The stored pilots currently include:

| Pilot | Tasks | Runs | Role |
| --- | ---: | ---: | --- |
| full30 | 30 | 60 | Measures process-waste reduction when outcomes are saturated. |
| hard10 | 10 | 20 | Measures outcome failures and hidden-grader boundary behavior. |

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
  benchmark/hard/pilot/hard10-real/runs.jsonl \
  benchmark/hard/pilot/hard10-real/manual-labels.jsonl \
  --markdown-output /tmp/hard10-label-eval.md
```

Hard-tier paper report:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research paper-report \
  benchmark/hard/pilot/hard10-real/runs.jsonl \
  --labels benchmark/hard/pilot/hard10-real/manual-labels.jsonl \
  --markdown-output /tmp/hard10-paper-report.md
```

## Current Result Snapshot

| Result | Current evidence |
| --- | --- |
| full30 repeated tool calls | `10.43 -> 7.00` |
| full30 token usage | `218.7k -> 184.8k` |
| hard10 success rate | `70% -> 80%` |
| hard10 repeated tool calls | `9.20 -> 6.20` |
| hard10 token usage | `248.9k -> 187.5k` |
| hidden semantic detector boundary | `TP=0`, `FP=0`, `FN=5` |

The RQ4 signal table shows why the detector boundary matters:
`verification_rate`, `unresolved_error`, `command_failure_count`, and
`failure_score` are identical for hard10 success and failure outcomes. The
visible traces look clean; hidden graders reveal the missed edge cases.

## What To Cite In A CV Or Interview

- Built a GPU-free Codex trace diagnosis system that parses real
  `codex exec --json` runs into a normalized event schema.
- Designed an 80-run benchmark across a 30-task seed tier and a 10-task hard
  tier with hidden graders.
- Measured harness intervention effects on real Codex runs: reduced repeated
  tool calls and token usage, with hard-tier success improving from 70% to 80%.
- Documented a negative boundary result: deterministic trace rules miss hidden
  semantic failures when visible process traces look clean.

## Known Limits

- The artifact studies Codex CLI traces, not all coding agents.
- The evaluated hard10 pilot has 10 tasks, so success-rate changes are pilot
  evidence rather than broad population estimates. The hard task suite now has
  11 runnable tasks after adding `HARD-011`.
- The detectors are deterministic and interpretable, but incomplete.
- Hidden semantic correctness still requires strong task-level oracles.

## Next Research Step

The strongest next step is to expand the hard tier from 10 tasks toward 30-50
tasks while adding more observable process failures, not only hidden semantic
edge cases. That would strengthen RQ1/RQ2 distribution claims and make the RQ3
success-rate estimate less fragile.

See `docs/submission_readiness_plan.md` for the concrete workstreams and
decision gate for moving from the current pilot artifact to a stronger paper
submission. See `docs/hard_tier_expansion_blueprint.md` for the implemented
`HARD-011` fixture and HARD-012 to HARD-030 task designs.
