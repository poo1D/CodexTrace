# Reproducibility And Claim-Evidence Checklist

This checklist maps the current CodexTrace paper claims to concrete repository
artifacts and commands. It is intended for paper writing, artifact review, and
CV/interview defense.

## Environment

CodexTrace is designed to run without GPU resources.

Minimum local requirements:

- Python 3.10+
- Node.js and npm for JavaScript fixture tests and the Web UI
- Codex CLI only when collecting new real traces

The stored pilots can be inspected and aggregated without re-running Codex.

## Main Artifacts

| Artifact | Purpose |
| --- | --- |
| `docs/artifact_guide.md` | Fifteen-minute reviewer/interviewer walkthrough. |
| `docs/paper_draft.md` | Result-driven workshop-style draft. |
| `docs/paper_outline.md` | Current outline and boundary-result writing plan. |
| `docs/results_summary.md` | Generated full30 + hard10 + hard30 + process-stress + verification-lift + verification-lift-v2 + verification-ablation result summary, including RQ4 trace-signal analysis. |
| `docs/rq4_signal_audit.md` | Generated signal audit for observable process positives and hidden semantic boundaries. |
| `docs/metric_coverage_audit.md` | Generated coverage audit for the metrics named in the experiment design. |
| `docs/failure_taxonomy_audit.md` | Generated coverage audit for the six process-failure taxonomy labels. |
| `docs/hard30_task_diagnosis.md` | Generated task-level hard30 diagnosis for double failures, intervention repairs/regressions, and largest waste deltas. |
| `docs/paper_claim_audit.md` | Generated support/partial/unsupported audit for thesis-level paper claims. |
| `docs/claim_text_guard.md` | Generated guard that checks paper-facing text for unsupported-claim drift. |
| `docs/goal_completion_audit.md` | Generated audit of whether the active original objective is complete or still blocked by evidence gaps. |
| `docs/verification_lift_next_experiment.md` | Generated audit of ordinary-baseline verification-lift claim closure and thesis-revision status. |
| `docs/paper_number_guard.md` | Generated guard that checks paper-draft numeric claims against stored aggregate artifacts. |
| `docs/reviewer_path_audit.md` | Generated guard that checks required reviewer files are discoverable from paper-facing entry points. |
| `docs/thesis_readiness.md` | Generated audit of which original-thesis requirements are satisfied, partial, or missing. |
| `docs/submission_package.md` | Generated RQ-to-evidence map for safe boundary-result paper claims. |
| `docs/process_stress_plan_audit.md` | Generated coverage audit for the planned process-stress tier. |
| `docs/verification_lift_plan_audit.md` | Generated task/prompt readiness audit for the verification-lift tier. |
| `docs/verification_lift_v2_plan_audit.md` | Generated task/prompt readiness audit for the ordinary-baseline verification-lift v2 tier. |
| `docs/verification_ablation_plan_audit.md` | Generated task/prompt readiness audit for the no-verify ablation tier. |
| `docs/failure_taxonomy.md` | Definitions for process-level failure labels. |
| `docs/hard_tier_expansion_blueprint.md` | Implemented HARD-011 to HARD-050 fixtures and hard30 pilot selection plan. |
| `docs/experiment_protocol.md` | Collection, labeling, and evaluation protocol. |
| `docs/related_work.md` | Compact bibliography and positioning notes. |
| `docs/submission_readiness_plan.md` | Workstreams and decision gate for a stronger paper submission. |
| `benchmark/hard/pilot/hard30-selection/` | Fixed 30-task hard-tier selection used for the 60-run hard30 collection. |
| `benchmark/hard/pilot/hard30-real/` | Submission-ready 30-task / 60-run hard-tier artifact with reports, labels, and shard metadata. |
| `benchmark/process-stress/tasks.jsonl` | Materialized 12-task process-stress tier for observable process failures. |
| `benchmark/detector-fixtures/` | Controlled JSONL detector fixtures covering the process-rule taxonomy. |
| `benchmark/verification-lift/tasks.jsonl` | Targeted 8-task verification-lift tier for the missing verification-rate claim. |
| `benchmark/verification-lift/prompts/` | Weak-baseline and evidence-gated prompt templates for the verification-lift tier. |
| `benchmark/verification-lift/pilot/full-real/` | 8-task / 16-run real verification-lift pilot with aggregate and manual labels. |
| `benchmark/verification-lift-v2/tasks.jsonl` | Ordinary-baseline 8-task verification-lift v2 tier for the completed claim-closure retest. |
| `benchmark/verification-lift-v2/prompts/` | Ordinary baseline and evidence-gated prompt templates for verification-lift v2. |
| `benchmark/verification-lift-v2/pilot/full-real/` | 8-task / 16-run real ordinary-baseline verification-lift v2 pilot with aggregate and shard status. |
| `benchmark/verification-ablation/tasks.jsonl` | Auxiliary 4-task no-verify ablation tier for harness-control evidence. |
| `benchmark/verification-ablation/prompts/` | No-verify baseline and evidence-gated prompt templates for the ablation tier. |
| `benchmark/verification-ablation/pilot/full-real/` | 4-task / 8-run real verification-ablation pilot with aggregate and manual labels. |
| `scripts/run_hard30_shards.py` | Resumable hard30 collection runner with configurable per-task concurrency. |
| `scripts/merge_hard30_shards.py` | Merge per-task hard30 shard manifests into the reporting `runs.jsonl`. |
| `scripts/run_benchmark_shards.py` | Resumable generic per-task collection runner for tiers such as verification-lift v2. |
| `scripts/merge_benchmark_shards.py` | Merge generic per-task shard manifests into the reporting `runs.jsonl`. |
| `scripts/finalize_hard30_pilot.py` | Post-processing entrypoint for hard30 aggregate tables, labels, CSV, and paper-report artifacts. |
| `scripts/finalize_benchmark_pilot.py` | Generic preflight/finalize entrypoint for non-hard30 pilots such as verification-lift v2. |
| `scripts/audit_manual_labels.py` | Standalone progress and quality audit for hard30 manual failure labels. |
| `scripts/audit_paper_claims.py` | Machine-readable guard against overclaiming unsupported paper findings. |
| `scripts/audit_claim_text_guard.py` | Text-level guard against reintroducing unsupported verification-lift or hidden-semantic claims. |
| `scripts/audit_goal_completion.py` | Goal-level completion audit for the original objective and boundary-result paper state. |
| `scripts/audit_verification_lift_next_experiment.py` | Claim-closure audit for the unresolved ordinary-baseline verification-lift claim. |
| `scripts/audit_verification_lift_v2_plan.py` | Plan audit for the ordinary-baseline verification-lift v2 scaffold. |
| `scripts/audit_paper_numbers.py` | Numeric guard for paper-draft values copied from generated result artifacts. |
| `scripts/audit_reviewer_path.py` | Reviewer-path coverage guard for required paper artifacts. |
| `scripts/audit_metric_coverage.py` | Checks that experiment-design metrics are collected, summarized, exported to CSV, and visible in aggregate Markdown. |
| `scripts/audit_failure_taxonomy.py` | Checks that taxonomy labels are defined, mapped in the paper draft, and covered by detector fixtures. |
| `scripts/audit_hard30_task_diagnosis.py` | Generates task-level hard30 failure-pattern and waste-delta diagnosis. |
| `scripts/audit_submission_package.py` | Generates the reviewer-facing RQ-to-evidence submission package map. |
| `scripts/check_submission_readiness.py` | Machine-readable gate for hard30 collection, finalization, labeling, and paper artifact readiness. |
| `benchmark/pilot/full30-real` | 30-task / 60-run real seed pilot. |
| `benchmark/pilot/full30-real/process-labels.jsonl` | Manual process-positive labels for full30 sandbox/permission detector coverage. |
| `benchmark/hard/pilot/hard10-real` | 10-task / 20-run hard-tier pilot with outcome failures. |
| `benchmark/hard/pilot/hard10-real/manual-labels.jsonl` | Manual hidden-failure labels for hard-tier RQ2 analysis. |
| `benchmark/hard/pilot/hard30-real/manual-labels.jsonl` | Hard30 hidden-failure labels for RQ1/RQ2 analysis. |

## Reproduce Tables From Stored Traces

Full 30-task aggregate:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/pilot/full30-real/runs.jsonl \
  --json-output /tmp/full30-aggregate.json \
  --markdown-output /tmp/full30-aggregate.md \
  --csv-output /tmp/full30-runs.csv
```

Full30 process-positive detector evaluation:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research evaluate-labels \
  benchmark/pilot/full30-real/runs.jsonl \
  benchmark/pilot/full30-real/process-labels.jsonl \
  --json-output /tmp/full30-process-label-eval.json \
  --markdown-output /tmp/full30-process-label-eval.md
```

Controlled detector-fixture evaluation:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research evaluate-labels \
  benchmark/detector-fixtures/runs.jsonl \
  benchmark/detector-fixtures/labels.jsonl \
  --json-output /tmp/detector-fixture-label-eval.json \
  --markdown-output /tmp/detector-fixture-label-eval.md
```

RQ4 signal audit:

```bash
PYTHONPATH=. python3 scripts/audit_rq4_signals.py \
  --json-output /tmp/rq4-signal-audit.json \
  --markdown-output /tmp/rq4-signal-audit.md
```

Metric coverage audit:

```bash
PYTHONPATH=. python3 scripts/audit_metric_coverage.py \
  --json-output /tmp/metric-coverage-audit.json \
  --markdown-output /tmp/metric-coverage-audit.md
```

Failure taxonomy coverage audit:

```bash
PYTHONPATH=. python3 scripts/audit_failure_taxonomy.py \
  --json-output /tmp/failure-taxonomy-audit.json \
  --markdown-output /tmp/failure-taxonomy-audit.md
```

Hard 10-task aggregate:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/hard/pilot/hard10-real/runs.jsonl \
  --json-output /tmp/hard10-aggregate.json \
  --markdown-output /tmp/hard10-aggregate.md \
  --csv-output /tmp/hard10-runs.csv
```

Hard-tier detector-vs-manual-label evaluation:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research evaluate-labels \
  benchmark/hard/pilot/hard10-real/runs.jsonl \
  benchmark/hard/pilot/hard10-real/manual-labels.jsonl \
  --json-output /tmp/hard10-label-eval.json \
  --markdown-output /tmp/hard10-label-eval.md
```

Hard-tier paper report with manual labels:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research paper-report \
  benchmark/hard/pilot/hard30-real/runs.jsonl \
  --labels benchmark/hard/pilot/hard30-real/manual-labels.jsonl \
  --json-output /tmp/hard30-paper-report.json \
  --markdown-output /tmp/hard30-paper-report.md
```

Hard30 task-level diagnosis:

```bash
PYTHONPATH=. python3 scripts/audit_hard30_task_diagnosis.py \
  --json-output /tmp/hard30-task-diagnosis.json \
  --markdown-output /tmp/hard30-task-diagnosis.md
```

When labels are provided, the paper report includes both outcome-level RQ4
trace signals and per-manual-label signal means. The latter is the table to use
when explaining which trace features characterize each failure class.
The same report also includes paired per-task baseline/intervention deltas for
RQ3, and `scripts/audit_hard30_task_diagnosis.py` turns those deltas into the
task-level answer for which hard30 tasks get lost, repair, regress, or waste
the most tool calls and tokens.
The paired summary counts improved/regressed/unchanged tasks for success,
verification, repeated calls, token usage, and failure score. `finalize`
also writes `paired-task-deltas.csv` and `paired-task-summary.csv` for
spreadsheet checks and plotting.

Combined paper-facing summary:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research summary \
  --markdown-output /tmp/results-summary.md \
  --json-output /tmp/results-summary.json
```

Original-thesis readiness audit:

```bash
PYTHONPATH=. python3 scripts/materialize_process_stress_fixtures.py

PYTHONPATH=. python3 scripts/audit_process_stress_plan.py \
  --markdown-output /tmp/process-stress-plan-audit.md \
  --json-output /tmp/process-stress-plan-audit.json

PYTHONPATH=. python3 scripts/audit_verification_lift_plan.py \
  --markdown-output /tmp/verification-lift-plan-audit.md \
  --json-output /tmp/verification-lift-plan-audit.json

PYTHONPATH=. python3 scripts/audit_verification_lift_v2_plan.py \
  --markdown-output /tmp/verification-lift-v2-plan-audit.md \
  --json-output /tmp/verification-lift-v2-plan-audit.json

PYTHONPATH=. python3 scripts/audit_verification_ablation_plan.py \
  --markdown-output /tmp/verification-ablation-plan-audit.md \
  --json-output /tmp/verification-ablation-plan-audit.json

PYTHONPATH=. python3 scripts/audit_thesis_readiness.py \
  --markdown-output /tmp/thesis-readiness.md \
  --json-output /tmp/thesis-readiness.json

PYTHONPATH=. python3 scripts/audit_goal_completion.py \
  --markdown-output /tmp/goal-completion-audit.md \
  --json-output /tmp/goal-completion-audit.json

PYTHONPATH=. python3 scripts/audit_verification_lift_next_experiment.py \
  --markdown-output /tmp/verification-lift-next-experiment.md \
  --json-output /tmp/verification-lift-next-experiment.json

PYTHONPATH=. python3 scripts/audit_paper_numbers.py \
  --markdown-output /tmp/paper-number-guard.md \
  --json-output /tmp/paper-number-guard.json

PYTHONPATH=. python3 scripts/audit_reviewer_path.py \
  --markdown-output /tmp/reviewer-path-audit.md \
  --json-output /tmp/reviewer-path-audit.json

PYTHONPATH=. python3 scripts/audit_submission_package.py \
  --markdown-output /tmp/submission-package.md \
  --json-output /tmp/submission-package.json
```

Dry-run the process-stress tier without model calls:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/process-stress/tasks.jsonl \
  --output-dir /tmp/codextrace-process-stress-dry \
  --dry-run
```

Dry-run the verification-lift tier without model calls:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/verification-lift/tasks.jsonl \
  --prompt-dir benchmark/verification-lift/prompts \
  --output-dir /tmp/codextrace-verification-lift-dry \
  --dry-run
```

Dry-run the ordinary-baseline verification-lift v2 tier without model calls:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/verification-lift-v2/tasks.jsonl \
  --prompt-dir benchmark/verification-lift-v2/prompts \
  --output-dir /tmp/codextrace-verification-lift-v2-dry \
  --dry-run
```

Resumable real collection for verification-lift v2:

```bash
PYTHONPATH=. python3 scripts/run_benchmark_shards.py \
  --tasks benchmark/verification-lift-v2/tasks.jsonl \
  --prompt-dir benchmark/verification-lift-v2/prompts \
  --run-dir benchmark/verification-lift-v2/pilot/full-real \
  --max-parallel 4 \
  --timeout-seconds 600 \
  --skip-complete

PYTHONPATH=. python3 scripts/run_benchmark_shards.py \
  --tasks benchmark/verification-lift-v2/tasks.jsonl \
  --prompt-dir benchmark/verification-lift-v2/prompts \
  --run-dir benchmark/verification-lift-v2/pilot/full-real \
  --status \
  --status-json /tmp/verification-lift-v2-shard-status.json

PYTHONPATH=. python3 scripts/merge_benchmark_shards.py \
  --run-dir benchmark/verification-lift-v2/pilot/full-real \
  --tasks benchmark/verification-lift-v2/tasks.jsonl
```

After collecting real verification-lift v2 traces, preflight and finalize the pilot:

```bash
PYTHONPATH=. python3 scripts/finalize_benchmark_pilot.py \
  --run-dir benchmark/verification-lift-v2/pilot/full-real \
  --tasks benchmark/verification-lift-v2/tasks.jsonl \
  --preflight-only \
  --preflight-json /tmp/verification-lift-v2-preflight.json

PYTHONPATH=. python3 scripts/finalize_benchmark_pilot.py \
  --run-dir benchmark/verification-lift-v2/pilot/full-real \
  --tasks benchmark/verification-lift-v2/tasks.jsonl
```

Current verification-lift v2 pilot outputs:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/verification-lift-v2/pilot/full-real/runs.jsonl \
  --markdown-output /tmp/verification-lift-v2-aggregate.md \
  --json-output /tmp/verification-lift-v2-aggregate.json

PYTHONPATH=. python3 -m codex_trace.cli research paper-report \
  benchmark/verification-lift-v2/pilot/full-real/runs.jsonl \
  --markdown-output /tmp/verification-lift-v2-paper-report.md \
  --json-output /tmp/verification-lift-v2-paper-report.json
```

Current verification-lift pilot outputs:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/verification-lift/pilot/full-real/runs.jsonl \
  --markdown-output /tmp/verification-lift-full-aggregate.md \
  --json-output /tmp/verification-lift-full-aggregate.json

PYTHONPATH=. python3 -m codex_trace.cli research paper-report \
  benchmark/verification-lift/pilot/full-real/runs.jsonl \
  --labels benchmark/verification-lift/pilot/full-real/manual-labels.jsonl \
  --markdown-output /tmp/verification-lift-paper-report.md \
  --json-output /tmp/verification-lift-paper-report.json
```

Current process-stress pilot outputs:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/process-stress/pilot/full-real/runs.jsonl \
  --markdown-output /tmp/process-stress-full-aggregate.md \
  --json-output /tmp/process-stress-full-aggregate.json
```

Dry-run the verification-ablation tier without model calls:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/verification-ablation/tasks.jsonl \
  --prompt-dir benchmark/verification-ablation/prompts \
  --output-dir /tmp/codextrace-verification-ablation-dry \
  --dry-run
```

Current verification-ablation pilot outputs:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/verification-ablation/pilot/full-real/runs.jsonl \
  --markdown-output /tmp/verification-ablation-aggregate.md \
  --json-output /tmp/verification-ablation-aggregate.json

PYTHONPATH=. python3 -m codex_trace.cli research paper-report \
  benchmark/verification-ablation/pilot/full-real/runs.jsonl \
  --labels benchmark/verification-ablation/pilot/full-real/manual-labels.jsonl \
  --markdown-output /tmp/verification-ablation-paper-report.md \
  --json-output /tmp/verification-ablation-paper-report.json
```

## Claim-Evidence Map

| Claim | Evidence | Current status |
| --- | --- | --- |
| CodexTrace parses Codex JSONL traces and emits reports. | `codex_trace/parser.py`, `codex_trace/diagnose.py`, `demo/`, `tests/` | Implemented and CI-tested. |
| The benchmark has a 30-task seed tier and two prompt conditions. | `benchmark/tasks.jsonl`, `benchmark/prompts/`, `benchmark/pilot/full30-real/runs.jsonl` | Implemented; 60 real stored runs. |
| The benchmark has a hard tier with hidden graders. | `benchmark/hard/tasks.jsonl`, `benchmark/hard/repos/`, `benchmark/hard/pilot/hard10-real` | Implemented; 50 runnable hard tasks and 20 real stored hard10 runs. |
| A balanced hard30 pilot has been collected. | `benchmark/hard/pilot/hard30-real/runs.jsonl`, `benchmark/hard/pilot/hard30-real/readiness.md` | Implemented; 30 selected tasks, 60 complete baseline/intervention runs, readiness passes. |
| Hard30 collection can run resumably with bounded concurrency. | `scripts/run_hard30_shards.py`, `scripts/merge_hard30_shards.py` | Implemented; one shard per hard30 task, configurable with `--max-parallel`. |
| Hard30 shard failures are machine-auditable. | `scripts/run_hard30_shards.py --status-json ...` | Implemented; each shard writes `shard-run.json` with return code, command, and log paths. |
| Hidden graders are not exposed during Codex execution. | `codex_trace/research.py`, `public_success_check` fields, hard-tier prompts | Implemented; hidden grader copied after Codex exits. |
| Full30 intervention reduces process waste. | `benchmark/pilot/full30-real/aggregate.md` | Supported: repeated tool calls `10.43 -> 7.00`, token usage `218.7k -> 184.8k`. |
| Hard10 intervention improves success and reduces waste. | `benchmark/hard/pilot/hard10-real/aggregate.md` | Supported: success `0.70 -> 0.80`, repeated tool calls `9.20 -> 6.20`, token usage `248.9k -> 187.5k`. |
| Hard30 intervention reduces process waste. | `benchmark/hard/pilot/hard30-real/aggregate.md`, `benchmark/hard/pilot/hard30-real/paired-task-summary.csv` | Supported: repeated tool calls `12.93 -> 9.20`, token usage `355.0k -> 256.3k`, token usage improves in 26/30 paired tasks. |
| Trace-only process rules miss hidden semantic edge failures. | `benchmark/hard/pilot/hard30-real/label-eval.md` | Supported as a boundary result: `TP=0`, `FP=0`, `FN=30` for `hidden_semantic_edge_case`. |
| Trace rules detect observed repetitive exploration positives. | `benchmark/hard/pilot/hard30-real/label-eval.md` | Supported for the reviewed process-positive subset: `TP=4`, `FP=0`, `FN=0` for `repetitive_exploration`. |
| Trace rules detect an observed sandbox/permission positive. | `benchmark/pilot/full30-real/process-label-eval.md` | Supported for the reviewed full30 process-positive subset: `TP=1`, `FP=0`, `FN=0` for `sandbox_permission_deadlock`; the same slice exposes `repetitive_exploration` false positives. |
| Trace rules cover the process taxonomy on controlled fixtures. | `benchmark/detector-fixtures/label-eval.md` | Supported as a rule-level sanity check: 6 labels, micro-F1 `1.00`. |
| RQ-to-evidence mapping is explicit. | `docs/experiment_protocol.md` | Each RQ is tied to a primary artifact, reproduction command, and acceptance evidence. |
| Process signals explain observable process failures and detector boundaries. | `docs/rq4_signal_audit.md`, `benchmark/hard/pilot/hard30-real/paper-report-labeled.md` RQ4 tables | Supported as a boundary-style RQ4 result: hidden failures have broad and exact success-check verification rate 1.0 and unresolved error 0, while repetitive exploration and sandbox/permission positives have large token, repeated-call, failure-score, or recover-phase deltas. |
| Original-thesis verification-rate lift is not yet supported. | `docs/thesis_readiness.md`, `docs/paper_claim_audit.md`, `benchmark/verification-lift/pilot/full-real/aggregate.md`, `benchmark/verification-lift-v2/pilot/full-real/aggregate.md` | Missing: stored ordinary and weak-baseline pilots, including the targeted verification-lift and verification-lift-v2 pilots, have saturated broad and exact success-check verification rates `1.00 -> 1.00`. |
| Original-thesis process-rule recall is supported at rule level, with real-pilot limits. | `docs/thesis_readiness.md`, `benchmark/detector-fixtures/label-eval.md`, `benchmark/pilot/full30-real/process-label-eval.md` | Controlled fixtures cover all process labels; real pilots naturally expose only some observable process positives and hidden semantic boundaries. |
| A process-stress tier is materialized for the missing evidence. | `benchmark/process-stress/tasks.jsonl`, `docs/process_stress_plan_audit.md` | Materialized: 12 tasks, at least two per target observable process label. |
| A process-stress real pilot validates collection. | `benchmark/process-stress/pilot/full-real/aggregate.md` | 12 tasks, 24 runs; success `0.9167 -> 0.9167`, repeated calls `8.08 -> 7.17`, token usage `209.0k -> 185.1k`. |
| A verification-lift tier tests the missing verification-rate claim. | `benchmark/verification-lift/pilot/full-real/aggregate.md`, `docs/thesis_readiness.md` | Negative result: 8 tasks, 16 runs; broad and exact success-check verification remain `1.00 -> 1.00`, repeated calls improve `6.13 -> 5.38`, token usage improves `176.8k -> 172.2k`. |
| An ordinary-baseline verification-lift v2 tier retests the missing verification-rate claim. | `benchmark/verification-lift-v2/pilot/full-real/aggregate.md`, `docs/thesis_readiness.md` | Negative result for verification lift: 8 tasks, 16 runs; broad and exact success-check verification remain `1.00 -> 1.00`, repeated calls improve `8.62 -> 5.50`, token usage improves `224.6k -> 185.5k`. |
| A no-verify ablation tests whether harness constraints can control verification behavior. | `benchmark/verification-ablation/pilot/full-real/aggregate.md`, `benchmark/verification-ablation/pilot/full-real/label-eval.md`, `docs/paper_claim_audit.md` | Supported only as a mechanism ablation: 4 tasks, 8 runs; broad and exact success-check verification rise `0.00 -> 1.00`, failure score drops `61.25 -> 0.00`, and detector labels recover `verification_gap` TP=4 and `premature_completion` TP=3. |
| Current claims are pilot-scale, not broad SWE-bench-scale claims. | `docs/paper_draft.md`, `docs/experiment_protocol.md` | Stated explicitly in limitations. |

## Validation Commands

Run syntax and import checks:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 -m compileall codex_trace tests \
  scripts/materialize_benchmark_fixtures.py \
  scripts/materialize_hard_fixtures.py
```

Run the hard-tier dry-run harness without model calls:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \
  --tasks benchmark/hard/tasks.jsonl \
  --output-dir /tmp/codextrace-hard-dry \
  --dry-run
```

Run the selected hard30 pilot as 30 resumable task shards without model calls,
using the same 15-way concurrency intended for a larger machine:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/run_hard30_shards.py \
  --run-dir /tmp/codextrace-hard30-sharded-dry \
  --max-parallel 15 \
  --dry-run
```

Merge the dry-run shard manifests into the single reporting manifest:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/merge_hard30_shards.py \
  --run-dir /tmp/codextrace-hard30-sharded-dry
```

Expected current output:

```text
Wrote 60 run record(s) to /tmp/codextrace-hard30-sharded-dry/runs.jsonl
```

Audit shard readiness without launching Codex:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/run_hard30_shards.py \
  --run-dir /tmp/codextrace-hard30-sharded-dry \
  --status \
  --status-json /tmp/codextrace-hard30-sharded-dry/shard-status.json
```

Expected completed dry-run output includes:

```text
Completed shards: 30
Failed shards: 0
Run records: 60 / 60
Ready to merge: yes
```

Run the hard30 finalization preflight after merging real traces:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/finalize_hard30_pilot.py \
  --run-dir benchmark/hard/pilot/hard30-real \
  --preflight-only \
  --preflight-json benchmark/hard/pilot/hard30-real/preflight.json
```

Run the submission readiness gate:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/check_submission_readiness.py \
  --json-output /tmp/codextrace-readiness.json \
  --markdown-output /tmp/codextrace-readiness.md
```

Run the paper-claim audit:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/audit_paper_claims.py \
  --json-output /tmp/codextrace-claim-audit.json \
  --markdown-output /tmp/codextrace-claim-audit.md
```

Run the paper-facing claim text guard:

```bash
PYTHONPATH=. PYTHONPYCACHEPREFIX=/tmp/codextrace-pycache \
  python3 scripts/audit_claim_text_guard.py \
  --json-output /tmp/codextrace-claim-text-guard.json \
  --markdown-output /tmp/codextrace-claim-text-guard.md
```

Check Git credential hygiene before pushing generated artifacts:

```bash
git config --show-origin --get-all credential.helper
test ! -e ./-
rg -n "gh[o]_|github[_]pat_|gh[p]_" .
```

Expected: credential helpers should not include `store --file=-`, the file
`./-` should not exist, and the token-pattern scan should return no matches.

When the gate is not ready, the Markdown/JSON report includes ordered next
actions for collection, merge, finalization, and labeling.

Manual label rows for failed runs must include at least one known failure tag
and a non-empty `notes` rationale. Known tags are the taxonomy labels in
`docs/failure_taxonomy.md` plus the hard-tier boundary label
`hidden_semantic_edge_case`.

Check that all hard-tier initial fixtures fail their hidden graders before an
agent edits them:

```bash
python3 -c 'import json, pathlib, subprocess
root=pathlib.Path("benchmark/hard")
passed=[]
failed=[]
for line in (root/"tasks.jsonl").read_text().splitlines():
    task=json.loads(line)
    result=subprocess.run(task["success_check"], cwd=root/task["fixture_path"], shell=True)
    (passed if result.returncode == 0 else failed).append(task["task_id"])
print("passed_initial", passed)
print("failed_initial_count", len(failed))
print("failed_initial", failed)'
```

Expected current output:

```text
passed_initial []
failed_initial_count 50
failed_initial ['HARD-001', 'HARD-002', 'HARD-003', 'HARD-004', 'HARD-005', 'HARD-006', 'HARD-007', 'HARD-008', 'HARD-009', 'HARD-010', 'HARD-011', 'HARD-012', 'HARD-013', 'HARD-014', 'HARD-015', 'HARD-016', 'HARD-017', 'HARD-018', 'HARD-019', 'HARD-020', 'HARD-021', 'HARD-022', 'HARD-023', 'HARD-024', 'HARD-025', 'HARD-026', 'HARD-027', 'HARD-028', 'HARD-029', 'HARD-030', 'HARD-031', 'HARD-032', 'HARD-033', 'HARD-034', 'HARD-035', 'HARD-036', 'HARD-037', 'HARD-038', 'HARD-039', 'HARD-040', 'HARD-041', 'HARD-042', 'HARD-043', 'HARD-044', 'HARD-045', 'HARD-046', 'HARD-047', 'HARD-048', 'HARD-049', 'HARD-050']
```

## Current Gaps Before A Stronger Submission

- Repeat the hard30 collection or add randomized trials to reduce prompt/order effects.
- Add more observable process failures, not only hidden semantic failures.
- Consider a lightweight semantic analysis layer for hidden edge-case failures.
- Improve detector evaluation with richer manual labels beyond the current
  hard-tier boundary label.

For a concrete expansion backlog and submission decision gate, see
`docs/submission_readiness_plan.md`. For the implemented HARD-011 to HARD-050
fixtures and completed hard30 pilot selection plan, see
`docs/hard_tier_expansion_blueprint.md`.
