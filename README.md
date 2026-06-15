# CodexTrace

CodexTrace is a flight recorder and failure debugger for `codex exec --json` runs.
It turns Codex JSONL event streams into a normalized trace, detects agent failure
patterns, and produces a report plus a replay UI.

The practical problem is simple: after a coding agent fails, the transcript is
long and noisy. CodexTrace answers:

- Where did the run fail?
- Did Codex edit files without verifying them?
- Which commands or tool calls were repeated?
- Was the failure caused by sandbox/permission friction?
- Did the harness burn a large context window without useful progress?

## Why This Exists

This project is designed for Agent Harness work rather than model training. It
does not need a GPU and does not depend on Codex Web or private IDE-extension
interfaces. The first version focuses on the open Codex CLI/SDK surface and the
machine-readable events emitted by:

```bash
codex exec --json "your coding task" > traces/run.jsonl
```

## Features

- Normalize `codex exec --json` JSONL into a stable trace schema.
- Segment trace events into setup, inspect, edit, verify, recover, and complete phases.
- Detect concrete failure or inefficiency modes:
  - command failure not clearly handled
  - file edits without post-edit verification
  - premature completion without verification evidence
  - repeated search/read commands
  - sandbox or permission blocks
  - long context with weak progress
- Generate Markdown and JSON diagnosis reports.
- Replay a trace in a TypeScript Web UI with highlighted failure nodes.
- Run offline with demo traces; optional LLM judging can be added later.
- Includes `demo/real-codex-run.jsonl`, a real `codex exec --json` fixture captured from this repository.

## Research Snapshot

CodexTrace is also a paper-oriented artifact for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

Current stored pilots:

| Pilot | Tasks | Runs | Failure outcomes | Main result |
| --- | ---: | ---: | ---: | --- |
| full30 | 30 | 60 | 0 | Intervention reduces repeated tool calls `10.43 -> 7.00` and token usage `218.7k -> 184.8k`. |
| hard10 | 10 | 20 | 5 | Intervention improves success `70% -> 80%` and reduces token usage `248.9k -> 187.5k`. |
| hard30 | 30 | 60 | 30 | Intervention keeps success at `50% -> 50%` while reducing repeated tool calls `12.93 -> 9.20` and token usage `355.0k -> 256.3k`. |
| process-stress | 12 | 24 | 2 | Intervention keeps success at `91.67% -> 91.67%` while reducing repeated tool calls `8.08 -> 7.17` and token usage `209.0k -> 185.1k`. |
| verification-lift | 8 | 16 | 2 | Targeted stress test does not raise broad or exact success-check verification `100% -> 100%`, but reduces repeated tool calls `6.13 -> 5.38` and token usage `176.8k -> 172.2k`. |
| verification-lift-v2 | 8 | 16 | 2 | Ordinary-baseline retest also keeps broad and exact success-check verification at `100% -> 100%`, while reducing repeated tool calls `8.62 -> 5.50` and token usage `224.6k -> 185.5k`. |
| verification-ablation | 4 | 8 | 2 | Auxiliary no-verify baseline ablation lifts broad and exact success-check verification `0% -> 100%` and drops failure score `61.25 -> 0`, but is not an ordinary baseline. |

The hard tier also exposes a trace-only detector boundary: all hard30 hidden
semantic edge-case failures are missed by deterministic process rules
(`TP=0`, `FP=0`, `FN=30`), showing why trace diagnosis should be paired with
strong task-level oracles. At the same time, reviewed high-volume
`repetitive_exploration` process positives are detected from trace signals
(`TP=4`, `FP=0`, `FN=0`). Controlled detector fixtures cover all six
process labels with micro-F1 `1.00`; those fixtures are rule-level sanity
checks, not real-pilot outcome evidence.

See `docs/artifact_guide.md` for the reviewer-facing walkthrough,
`docs/results_summary.md` for the generated result summary and RQ4
trace-signal analysis, `docs/headline_results.md` for the compact actual
headline table, `docs/thesis_revision_decision.md` for the explicit
boundary-result thesis decision, `docs/validity_threats.md` for validity
threat mapping, `docs/limitations_traceability_audit.md` for paper-limitations
traceability, `docs/expected_results_reconciliation.md` for replacing the
original expected-results sketch with stored evidence,
`docs/verification_saturation_audit.md` for the generated
ordinary-baseline verification-saturation proof, `docs/rq4_signal_audit.md`
for the generated boundary-style signal audit, `docs/metric_coverage_audit.md` for experiment
metric coverage, `docs/benchmark_trace_artifact.md` for hard30 task/run/trace
pair completeness, `docs/label_provenance_audit.md` for hard30 label
template/manual-label/evaluation consistency, `docs/paired_effects_audit.md`
for paired RQ3 effect-size and uncertainty evidence, `docs/demo_audit.md` for the offline demo smoke path,
`docs/web_artifact_audit.md` for the static Web replay artifact,
`docs/cli_surface_audit.md` for offline CLI coverage,
`docs/ci_surface_audit.md` for CI/readiness/packaging coverage,
`docs/schema_field_audit.md` for Run/Step schema-field
mapping, `docs/parser_event_coverage.md` for JSONL parser event coverage,
`docs/failure_node_traceability.md` for diagnosis-node traceability,
`docs/failure_taxonomy_audit.md` for six-label taxonomy
coverage, `docs/related_work_audit.md` for related-work positioning coverage,
`docs/bibliography_audit.md` for paper reference discoverability,
`docs/paper_abstract_audit.md` for abstract-level claim coverage,
`docs/paper_contribution_audit.md` for contribution-claim coverage,
`docs/paper_conclusion_audit.md` for conclusion boundary alignment,
`docs/method_pipeline_audit.md` for method pipeline source/CLI coverage,
`docs/paper_structure_audit.md` for paper-section/RQ coverage,
`docs/rq_table_consistency_audit.md` for RQ result-table drift checks,
`docs/reproducibility_audit.md` for reproducibility-command coverage,
`docs/hard30_task_diagnosis.md` for task-level
hard30 repairs/regressions and double failures, `docs/thesis_readiness.md` for
the original-thesis gap audit, and `docs/reproducibility_checklist.md` for
claim-to-evidence mapping.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

codex-trace diagnose demo/failing-codex-trace.jsonl
codex-trace diagnose demo/failing-codex-trace.jsonl --format json -o demo/report.json
pytest
```

## Demo

Run the offline demo:

```bash
./scripts/demo.sh
```

It generates:

- `/tmp/codextrace-demo/demo-report.json`
- `/tmp/codextrace-demo/demo-report.md`

Then start the visual replay:

```bash
./scripts/demo.sh --update-ui
cd web
npm install
npm run dev
```

Open the printed Vite URL, usually `http://localhost:5173`. The
`--update-ui` flag refreshes `web/public/report.json`, which is the static
input used by the replay UI.

For the full walkthrough, see `demo/README.md`.

## Research Mode

CodexTrace now includes a benchmark scaffold for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

Key files:

- `benchmark/tasks.jsonl`: 30 seed coding tasks
- `benchmark/smoke/tasks.jsonl`: 3 runnable smoke tasks for validating the harness
- `benchmark/labels.example.jsonl`: example manual failure labels for detector evaluation
- `benchmark/prompts/baseline.txt`: baseline prompt template
- `benchmark/prompts/intervention.txt`: harness-intervention prompt template
- `benchmark/detector-fixtures/`: controlled JSONL traces covering the process-rule taxonomy
- `benchmark/process-stress/tasks.jsonl`: materialized process-stress slice for observable process-failure coverage
- `benchmark/verification-lift/tasks.jsonl`: targeted verification-lift stress tier under a weak-baseline prompt contrast
- `benchmark/verification-lift/prompts/`: verification-lift baseline/intervention prompt templates
- `benchmark/verification-lift-v2/tasks.jsonl`: ordinary-baseline verification-lift v2 tier for the completed claim-closure retest
- `benchmark/verification-lift-v2/prompts/`: ordinary baseline and evidence-gated v2 prompt templates
- `benchmark/verification-lift-v2/pilot/full-real`: 8-task / 16-run real ordinary-baseline verification-lift v2 pilot
- `benchmark/verification-ablation/tasks.jsonl`: auxiliary no-verify baseline ablation tasks for harness-control evidence
- `benchmark/verification-ablation/prompts/`: no-verify baseline and evidence-gated prompt templates
- `scripts/materialize_process_stress_fixtures.py`: rebuilds the process-stress fixture repositories
- `scripts/audit_process_stress_plan.py`: checks process-stress coverage and materialized fixture readiness
- `scripts/audit_verification_lift_plan.py`: checks verification-lift task, prompt, and fixture readiness
- `scripts/audit_verification_lift_v2_plan.py`: checks the ordinary-baseline verification-lift v2 scaffold
- `scripts/audit_verification_ablation_plan.py`: checks verification-ablation task, prompt, and fixture readiness
- `scripts/audit_verification_lift_next_experiment.py`: records whether ordinary-baseline verification-lift evidence closes the claim or requires thesis revision
- `scripts/audit_headline_results.py`: generates the compact actual headline table and verification-lift boundary note
- `scripts/run_benchmark_shards.py`: resumable per-task benchmark collection runner for tiers such as verification-lift v2
- `scripts/merge_benchmark_shards.py`: merges generic per-task shard manifests into one pilot `runs.jsonl`
- `scripts/finalize_benchmark_pilot.py`: preflights and finalizes non-hard30 pilot outputs such as verification-lift v2
- `scripts/audit_claim_text_guard.py`: checks paper-facing docs for unsupported verification-lift or hidden-semantic overclaims
- `scripts/audit_goal_completion.py`: checks original-goal completion status against current evidence
- `scripts/audit_thesis_revision_decision.py`: generates the explicit original-thesis revision decision memo
- `scripts/audit_validity_threats.py`: generates the validity-threat mapping for safe paper wording
- `scripts/audit_limitations_traceability.py`: checks paper limitations against validity-threat safe wording
- `scripts/audit_expected_results_reconciliation.py`: checks paper-facing files use stored headline evidence instead of the expected-results sketch
- `scripts/audit_verification_saturation.py`: checks stored non-ablation pilots for ordinary verification-rate saturation
- `scripts/audit_paper_numbers.py`: checks paper-draft numeric claims against stored aggregate artifacts
- `scripts/audit_reviewer_path.py`: checks required reviewer files are discoverable from paper-facing entry points
- `scripts/audit_benchmark_trace_artifact.py`: checks hard30 task/run/trace/outcome/manual-label completeness
- `scripts/audit_label_provenance.py`: checks hard30 label template, manual-label, and label-evaluation consistency
- `scripts/audit_metric_coverage.py`: checks planned experiment metrics across run rows, summaries, CSV, and aggregate Markdown
- `scripts/audit_paired_effects.py`: computes task-paired effect sizes, sign tests, and bootstrap CIs for RQ3 deltas
- `scripts/audit_demo.py`: runs the offline demo script and checks generated JSON/Markdown diagnosis artifacts
- `scripts/audit_web_artifact.py`: checks the committed Web replay fixture and event-ID highlight source path
- `scripts/audit_cli_surface.py`: smoke-tests offline CLI entry points for trace, diagnosis, and research artifact generation
- `scripts/audit_ci_surface.py`: checks CI, packaging, readiness-gate, and local task-runner coverage
- `scripts/audit_schema_fields.py`: checks paper-facing Run/Step schema fields against parser, schema, and research outputs
- `scripts/audit_parser_event_coverage.py`: checks synthetic JSONL event-kind and phase coverage for the parser
- `scripts/audit_failure_node_traceability.py`: checks diagnosis finding event IDs through JSON, Markdown, and Web UI highlights
- `scripts/audit_detector_evaluation.py`: consolidates detector precision/recall evidence for RQ2 boundary claims
- `scripts/audit_rule_implementation.py`: checks taxonomy labels against implemented diagnosis rules and label aliases
- `scripts/audit_phase_coverage.py`: checks phase segmentation coverage across schema, paper text, run rows, and RQ4 signals
- `scripts/audit_task_category_coverage.py`: checks benchmark task-category coverage across seed, hard, and hard30 manifests
- `scripts/audit_harness_protocol.py`: checks intervention prompt templates and protocol coverage for the harness constraints
- `scripts/audit_failure_taxonomy.py`: checks six-label taxonomy coverage across docs, paper mapping, and detector fixtures
- `scripts/audit_related_work.py`: checks related-work coverage across bibliography notes and the paper draft
- `scripts/audit_bibliography.py`: checks paper reference discoverability across the draft and related-work notes
- `scripts/audit_paper_abstract.py`: checks abstract-level evidence coverage and overclaim boundaries
- `scripts/audit_paper_contributions.py`: checks contribution claims against current evidence boundaries
- `scripts/audit_paper_conclusion.py`: checks conclusion claims against current evidence boundaries
- `scripts/audit_method_pipeline.py`: checks method pipeline mapping to source and offline CLI smoke outputs
- `scripts/audit_paper_structure.py`: checks paper draft section, RQ, and boundary-result coverage
- `scripts/audit_rq_table_consistency.py`: checks paper RQ result tables against generated hard30 report artifacts
- `scripts/audit_reproducibility.py`: checks reproducibility checklist command coverage and Markdown fence balance
- `scripts/audit_submission_package.py`: generates the RQ-to-evidence submission package map
- `docs/artifact_guide.md`: 15-minute reviewer/interviewer walkthrough
- `docs/experiment_protocol.md`: collection and labeling protocol
- `docs/failure_taxonomy.md`: process-level failure labels
- `docs/hard_tier_expansion_blueprint.md`: HARD-011 to HARD-050 fixtures and hard30 pilot selection plan
- `docs/paper_claim_audit.md`: generated support/partial/unsupported audit for thesis-level claims
- `docs/claim_text_guard.md`: generated guard that checks paper-facing text for unsupported-claim drift
- `docs/goal_completion_audit.md`: generated audit showing original-goal completion status and blocking evidence gaps
- `docs/thesis_revision_decision.md`: generated decision memo for revising the original thesis into a boundary-result paper
- `docs/validity_threats.md`: generated validity-threat map with evidence, mitigations, and safe wording
- `docs/limitations_traceability_audit.md`: generated audit linking paper limitations to validity-threat safe wording
- `docs/expected_results_reconciliation.md`: generated audit proving paper-facing files use actual headline evidence instead of expected-results numbers
- `docs/verification_saturation_audit.md`: generated audit for ordinary-baseline verification saturation and ablation boundary
- `docs/verification_lift_next_experiment.md`: generated audit for ordinary-baseline verification-lift claim closure and thesis-revision status
- `docs/headline_results.md`: generated compact actual headline table replacing the expected-results sketch
- `docs/paper_number_guard.md`: generated guard that checks paper-draft numeric claims against stored artifacts
- `docs/reviewer_path_audit.md`: generated guard that checks reviewer-path coverage for required paper artifacts
- `docs/benchmark_trace_artifact.md`: generated audit for hard30 task/run/trace/outcome/manual-label completeness
- `docs/label_provenance_audit.md`: generated audit for hard30 label-file provenance and evaluation consistency
- `docs/paper_draft.md`: result-driven workshop-style paper draft
- `docs/paper_outline.md`: paper outline and experiment plan
- `docs/paired_effects_audit.md`: generated paired effect-size and uncertainty audit for RQ3 waste-reduction claims
- `docs/demo_audit.md`: generated audit for the reviewer-facing offline demo script
- `docs/web_artifact_audit.md`: generated audit for the committed static Web replay artifact
- `docs/ci_surface_audit.md`: generated audit for CI, packaging, readiness-gate, and local task-runner coverage
- `docs/reproducibility_checklist.md`: claim-evidence map and reproduction commands
- `docs/submission_package.md`: generated RQ-to-evidence map for safe paper submission claims
- `docs/results_summary.md`: generated full30 + hard10 + hard30 + process-stress + verification-lift + verification-lift-v2 + verification-ablation result summary, including RQ4 trace-signal analysis
- `docs/rq4_signal_audit.md`: generated signal audit for observable process failures and hidden semantic boundaries
- `docs/benchmark_trace_artifact.md`: generated audit for hard30 task/run/trace/outcome/manual-label completeness
- `docs/metric_coverage_audit.md`: generated coverage audit for the experiment-design metrics
- `docs/cli_surface_audit.md`: generated audit for offline CLI command surface coverage
- `docs/ci_surface_audit.md`: generated audit for CI, packaging, readiness-gate, and local task-runner coverage
- `docs/schema_field_audit.md`: generated audit for paper-facing Run/Step schema-field mapping
- `docs/parser_event_coverage.md`: generated audit for JSONL parser event-kind and phase coverage
- `docs/failure_node_traceability.md`: generated audit for diagnosis finding event-ID traceability
- `docs/detector_evaluation_audit.md`: generated audit for detector precision/recall evidence
- `docs/rule_implementation_audit.md`: generated audit for implemented diagnosis-rule coverage
- `docs/phase_coverage_audit.md`: generated audit for phase segmentation coverage
- `docs/task_category_coverage.md`: generated audit for benchmark task-category coverage
- `docs/harness_protocol_audit.md`: generated audit for intervention prompt/protocol coverage
- `docs/failure_taxonomy_audit.md`: generated coverage audit for the six process-failure taxonomy labels
- `docs/related_work_audit.md`: generated coverage audit for related-work positioning axes
- `docs/bibliography_audit.md`: generated audit for reference discoverability across paper and notes
- `docs/paper_abstract_audit.md`: generated audit for abstract-level evidence coverage and overclaim boundaries
- `docs/paper_contribution_audit.md`: generated audit for evidence-backed contribution claims
- `docs/paper_conclusion_audit.md`: generated audit for conclusion boundary alignment and overclaim prevention
- `docs/method_pipeline_audit.md`: generated audit for method pipeline source/CLI smoke coverage
- `docs/paper_structure_audit.md`: generated coverage audit for paper sections, RQ result blocks, and boundary framing
- `docs/rq_table_consistency_audit.md`: generated audit for paper RQ result-table consistency with hard30 report artifacts
- `docs/label_provenance_audit.md`: generated audit for hard30 label-file provenance and evaluation consistency
- `docs/verification_saturation_audit.md`: generated audit for ordinary-baseline verification saturation and ablation boundary
- `docs/reproducibility_audit.md`: generated coverage audit for reproduction commands and checklist Markdown structure
- `docs/hard30_task_diagnosis.md`: generated task-level hard30 diagnosis for double failures, repairs, regressions, and waste deltas
- `docs/process_stress_plan_audit.md`: generated coverage audit for the materialized process-stress tier
- `docs/verification_lift_plan_audit.md`: generated coverage audit for the targeted verification-lift tier
- `docs/verification_lift_v2_plan_audit.md`: generated coverage audit for the ordinary-baseline verification-lift v2 tier
- `docs/verification_ablation_plan_audit.md`: generated coverage audit for the no-verify ablation tier
- `docs/related_work.md`: compact bibliography and positioning notes
- `docs/submission_readiness_plan.md`: concrete path from pilot artifact to stronger paper submission
- `docs/thesis_readiness.md`: generated audit of which original-thesis requirements are satisfied, partial, or missing
- `benchmark/pilot/full30-real`: 30-task / 60-run real pilot
- `benchmark/process-stress/pilot/full-real`: 12-task / 24-run real pilot for the process-stress tier
- `benchmark/verification-lift/pilot/full-real`: 8-task / 16-run real pilot for the verification-lift tier
- `benchmark/verification-lift-v2/pilot/full-real`: 8-task / 16-run real ordinary-baseline verification-lift v2 pilot
- `benchmark/verification-ablation/pilot/full-real`: 4-task / 8-run real no-verify ablation pilot
- `benchmark/hard/pilot/hard10-real`: 10-task / 20-run hard-tier pilot with outcome failures
- `benchmark/hard/pilot/hard30-real`: 30-task / 60-run hard-tier pilot with hidden-grader failures and paper tables
- `benchmark/hard/pilot/hard30-selection`: selected 30-task hard-tier pilot used for the hard30 collection

Render prompts:

```bash
codex-trace research prompt --tasks benchmark/tasks.jsonl CT-001 baseline
codex-trace research prompt --tasks benchmark/tasks.jsonl CT-001 intervention
```

Aggregate traces:

```bash
codex-trace research aggregate benchmark/runs.example.jsonl \
  --json-output reports/example-aggregate.json \
  --markdown-output reports/example-aggregate.md \
  --csv-output reports/example-runs.csv
```

Dry-run the runnable smoke harness:

```bash
codex-trace research run \
  --tasks benchmark/smoke/tasks.jsonl \
  --output-dir runs/smoke-dry \
  --dry-run
```

Generate a manual-label template from collected runs:

```bash
codex-trace research label-template benchmark/runs.example.jsonl \
  --include-predictions \
  --output reports/example-label-template.jsonl
```

Evaluate detector labels against manual labels:

```bash
codex-trace research evaluate-labels benchmark/runs.example.jsonl benchmark/labels.example.jsonl \
  --json-output reports/example-label-eval.json \
  --markdown-output reports/example-label-eval.md
```

Generate paper-ready RQ tables:

```bash
codex-trace research paper-report benchmark/runs.example.jsonl \
  --labels benchmark/labels.example.jsonl \
  --json-output reports/example-paper-report.json \
  --markdown-output reports/example-paper-report.md
```

Current paper artifacts:

```bash
codex-trace research aggregate benchmark/pilot/full30-real/runs.jsonl
codex-trace research aggregate benchmark/hard/pilot/hard10-real/runs.jsonl
codex-trace research aggregate benchmark/hard/pilot/hard30-real/runs.jsonl
codex-trace research paper-report benchmark/hard/pilot/hard10-real/runs.jsonl \
  --labels benchmark/hard/pilot/hard10-real/manual-labels.jsonl
codex-trace research paper-report benchmark/hard/pilot/hard30-real/runs.jsonl \
  --labels benchmark/hard/pilot/hard30-real/manual-labels.jsonl
codex-trace research summary --markdown-output docs/results_summary.md
PYTHONPATH=. python3 scripts/audit_hard30_task_diagnosis.py \
  --json-output docs/hard30_task_diagnosis.json \
  --markdown-output docs/hard30_task_diagnosis.md
PYTHONPATH=. python3 scripts/audit_paper_claims.py --markdown-output docs/paper_claim_audit.md
PYTHONPATH=. python3 scripts/audit_thesis_readiness.py --markdown-output docs/thesis_readiness.md
PYTHONPATH=. python3 scripts/audit_claim_text_guard.py --markdown-output docs/claim_text_guard.md
PYTHONPATH=. python3 scripts/audit_goal_completion.py --markdown-output docs/goal_completion_audit.md
PYTHONPATH=. python3 scripts/audit_thesis_revision_decision.py --markdown-output docs/thesis_revision_decision.md
PYTHONPATH=. python3 scripts/audit_validity_threats.py --markdown-output docs/validity_threats.md
PYTHONPATH=. python3 scripts/audit_limitations_traceability.py --markdown-output docs/limitations_traceability_audit.md
PYTHONPATH=. python3 scripts/audit_expected_results_reconciliation.py --markdown-output docs/expected_results_reconciliation.md
PYTHONPATH=. python3 scripts/audit_verification_lift_next_experiment.py --markdown-output docs/verification_lift_next_experiment.md
PYTHONPATH=. python3 scripts/audit_verification_lift_v2_plan.py --markdown-output docs/verification_lift_v2_plan_audit.md
PYTHONPATH=. python3 scripts/audit_verification_ablation_plan.py --markdown-output docs/verification_ablation_plan_audit.md
PYTHONPATH=. python3 scripts/audit_headline_results.py --markdown-output docs/headline_results.md
PYTHONPATH=. python3 scripts/audit_paper_numbers.py --markdown-output docs/paper_number_guard.md
PYTHONPATH=. python3 scripts/audit_reviewer_path.py --markdown-output docs/reviewer_path_audit.md
PYTHONPATH=. python3 scripts/audit_benchmark_trace_artifact.py --markdown-output docs/benchmark_trace_artifact.md
PYTHONPATH=. python3 scripts/audit_submission_package.py --markdown-output docs/submission_package.md
PYTHONPATH=. python3 scripts/audit_detector_evaluation.py --markdown-output docs/detector_evaluation_audit.md
PYTHONPATH=. python3 scripts/audit_rule_implementation.py --markdown-output docs/rule_implementation_audit.md
PYTHONPATH=. python3 scripts/audit_paired_effects.py --markdown-output docs/paired_effects_audit.md
PYTHONPATH=. python3 scripts/audit_demo.py --markdown-output docs/demo_audit.md
PYTHONPATH=. python3 scripts/audit_web_artifact.py --markdown-output docs/web_artifact_audit.md
PYTHONPATH=. python3 scripts/audit_cli_surface.py --markdown-output docs/cli_surface_audit.md
PYTHONPATH=. python3 scripts/audit_ci_surface.py --markdown-output docs/ci_surface_audit.md
PYTHONPATH=. python3 scripts/audit_schema_fields.py --markdown-output docs/schema_field_audit.md
PYTHONPATH=. python3 scripts/audit_parser_event_coverage.py --markdown-output docs/parser_event_coverage.md
PYTHONPATH=. python3 scripts/audit_failure_node_traceability.py --markdown-output docs/failure_node_traceability.md
PYTHONPATH=. python3 scripts/audit_phase_coverage.py --markdown-output docs/phase_coverage_audit.md
PYTHONPATH=. python3 scripts/audit_task_category_coverage.py --markdown-output docs/task_category_coverage.md
PYTHONPATH=. python3 scripts/audit_harness_protocol.py --markdown-output docs/harness_protocol_audit.md
PYTHONPATH=. python3 scripts/audit_failure_taxonomy.py --markdown-output docs/failure_taxonomy_audit.md
PYTHONPATH=. python3 scripts/audit_related_work.py --markdown-output docs/related_work_audit.md
PYTHONPATH=. python3 scripts/audit_bibliography.py --markdown-output docs/bibliography_audit.md
PYTHONPATH=. python3 scripts/audit_paper_abstract.py --markdown-output docs/paper_abstract_audit.md
PYTHONPATH=. python3 scripts/audit_paper_contributions.py --markdown-output docs/paper_contribution_audit.md
PYTHONPATH=. python3 scripts/audit_paper_conclusion.py --markdown-output docs/paper_conclusion_audit.md
PYTHONPATH=. python3 scripts/audit_method_pipeline.py --markdown-output docs/method_pipeline_audit.md
PYTHONPATH=. python3 scripts/audit_paper_structure.py --markdown-output docs/paper_structure_audit.md
PYTHONPATH=. python3 scripts/audit_rq_table_consistency.py --markdown-output docs/rq_table_consistency_audit.md
PYTHONPATH=. python3 scripts/audit_label_provenance.py --markdown-output docs/label_provenance_audit.md
PYTHONPATH=. python3 scripts/audit_verification_saturation.py --markdown-output docs/verification_saturation_audit.md
PYTHONPATH=. python3 scripts/audit_reproducibility.py --markdown-output docs/reproducibility_audit.md
```

The current draft in `docs/paper_draft.md` reports the seed, hard10, hard30,
process-stress, verification-lift, and verification-ablation pilots. The
ordinary and weak-baseline pilots support waste reduction but not
verification-rate lift, even under exact visible success-check matching; the
no-verify ablation is reported only as a mechanism check that the harness can
control verification behavior under an artificial baseline condition.

To run the Web UI:

```bash
cd web
npm install
npm run dev
```

## Capturing a Real Codex Trace

From any Git repository:

```bash
codex exec --json "inspect this repo and identify one risky area" > run.jsonl
codex-trace diagnose run.jsonl -o report.md
codex-trace diagnose run.jsonl --format json -o report.json
```

## CLI

```bash
codex-trace collect TRACE.jsonl -o trace.json
codex-trace diagnose TRACE.jsonl --format markdown -o report.md
codex-trace diagnose TRACE.jsonl --format json -o report.json
```

## Trace Schema

CodexTrace maps raw Codex events into:

- `thread`
- `turn`
- `agent_message`
- `reasoning`
- `command`
- `file_change`
- `mcp_tool`
- `web_search`
- `plan`
- `error`
- `unknown`

Each event also carries an inferred `phase`:

- `setup`
- `inspect`
- `edit`
- `verify`
- `recover`
- `complete`
- `other`

This keeps the first version Codex-first while leaving room for future adapters
for Claude Code, SWE-agent, OpenHands, or custom MCP agents.

## Example Diagnosis

```text
Failed trace: Command failures were not clearly handled.
10 events, 4 commands, 2 failed commands.

Findings:
- Command failures were not clearly handled
- Files changed without a verification command
- Repeated search/read commands suggest inefficient exploration
- Sandbox or permission friction blocked progress
```

## CV Bullets

- Built `CodexTrace`, a GPU-free Agent Harness research tool that parses `codex exec --json` event streams into normalized traces and detects process failures such as missing verification, unrecovered command errors, repeated tool use, and sandbox blocks.
- Designed and collected a 204-run Codex trace benchmark across seed, hard, process-stress, verification-lift, verification-lift-v2, and no-verify ablation tiers, comparing baseline prompts with verification-focused harness interventions.
- Measured intervention effects on real Codex runs: hard30 repeated tool calls dropped `12.93 -> 9.20`, hard30 token usage dropped `355.0k -> 256.3k`, and paired tasks improved on token usage in `26/30` cases.
- Shipped a reproducible research artifact with hidden-grader fixtures, manual-label evaluation, generated paper tables, a TypeScript replay UI, Python CLI, and GitHub Actions CI.

## Non-goals

- No model training.
- No GPU dependency.
- No private Codex Web or IDE-extension interfaces.
- No attempt to clone Codex.
- No multi-agent platform in v1.

## Roadmap

- Load generated report JSON directly in the Web UI.
- Add Codex SDK capture helpers.
- Add optional LLM-as-judge scoring.
- Add run-to-run diff for prompt and harness interventions.
- Extend adapters to other coding-agent traces.
- Expand the hard tier and manual labels following `docs/submission_readiness_plan.md` and `docs/hard_tier_expansion_blueprint.md`.
