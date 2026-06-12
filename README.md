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
trace-signal analysis, `docs/rq4_signal_audit.md` for the generated
boundary-style signal audit, `docs/hard30_task_diagnosis.md` for task-level
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
- `benchmark/process-stress/tasks.jsonl`: materialized process-stress slice for closing original-thesis evidence gaps
- `benchmark/verification-lift/tasks.jsonl`: targeted verification-lift stress tier under a weak-baseline prompt contrast
- `benchmark/verification-lift/prompts/`: verification-lift baseline/intervention prompt templates
- `benchmark/verification-ablation/tasks.jsonl`: auxiliary no-verify baseline ablation tasks for harness-control evidence
- `benchmark/verification-ablation/prompts/`: no-verify baseline and evidence-gated prompt templates
- `scripts/materialize_process_stress_fixtures.py`: rebuilds the process-stress fixture repositories
- `scripts/audit_process_stress_plan.py`: checks process-stress coverage and materialized fixture readiness
- `scripts/audit_verification_lift_plan.py`: checks verification-lift task, prompt, and fixture readiness
- `scripts/audit_verification_ablation_plan.py`: checks verification-ablation task, prompt, and fixture readiness
- `scripts/audit_claim_text_guard.py`: checks paper-facing docs for unsupported verification-lift or hidden-semantic overclaims
- `scripts/audit_submission_package.py`: generates the RQ-to-evidence submission package map
- `docs/artifact_guide.md`: 15-minute reviewer/interviewer walkthrough
- `docs/experiment_protocol.md`: collection and labeling protocol
- `docs/failure_taxonomy.md`: process-level failure labels
- `docs/hard_tier_expansion_blueprint.md`: HARD-011 to HARD-050 fixtures and hard30 pilot selection plan
- `docs/paper_claim_audit.md`: generated support/partial/unsupported audit for thesis-level claims
- `docs/claim_text_guard.md`: generated guard that checks paper-facing text for unsupported-claim drift
- `docs/paper_draft.md`: result-driven workshop-style paper draft
- `docs/paper_outline.md`: paper outline and experiment plan
- `docs/reproducibility_checklist.md`: claim-evidence map and reproduction commands
- `docs/submission_package.md`: generated RQ-to-evidence map for safe paper submission claims
- `docs/results_summary.md`: generated full30 + hard10 + hard30 + process-stress + verification-lift + verification-ablation result summary, including RQ4 trace-signal analysis
- `docs/rq4_signal_audit.md`: generated signal audit for observable process failures and hidden semantic boundaries
- `docs/hard30_task_diagnosis.md`: generated task-level hard30 diagnosis for double failures, repairs, regressions, and waste deltas
- `docs/process_stress_plan_audit.md`: generated coverage audit for the materialized process-stress tier
- `docs/verification_lift_plan_audit.md`: generated coverage audit for the targeted verification-lift tier
- `docs/verification_ablation_plan_audit.md`: generated coverage audit for the no-verify ablation tier
- `docs/related_work.md`: compact bibliography and positioning notes
- `docs/submission_readiness_plan.md`: concrete path from pilot artifact to stronger paper submission
- `docs/thesis_readiness.md`: generated audit of which original-thesis requirements are satisfied, partial, or missing
- `benchmark/pilot/full30-real`: 30-task / 60-run real pilot
- `benchmark/process-stress/pilot/full-real`: 12-task / 24-run real pilot for the process-stress tier
- `benchmark/verification-lift/pilot/full-real`: 8-task / 16-run real pilot for the verification-lift tier
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
PYTHONPATH=. python3 scripts/audit_submission_package.py --markdown-output docs/submission_package.md
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
- Designed and collected a 188-run Codex trace benchmark across seed, hard, process-stress, verification-lift, and no-verify ablation tiers, comparing baseline prompts with verification-focused harness interventions.
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
