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
| `docs/results_summary.md` | Generated full30 + hard10 result summary, including RQ4 trace-signal analysis. |
| `docs/failure_taxonomy.md` | Definitions for process-level failure labels. |
| `docs/hard_tier_expansion_blueprint.md` | Implemented HARD-011 to HARD-033 fixtures and next hard-tier expansion candidates. |
| `docs/experiment_protocol.md` | Collection, labeling, and evaluation protocol. |
| `docs/related_work.md` | Compact bibliography and positioning notes. |
| `docs/submission_readiness_plan.md` | Workstreams and decision gate for a stronger paper submission. |
| `benchmark/pilot/full30-real` | 30-task / 60-run real seed pilot. |
| `benchmark/hard/pilot/hard10-real` | 10-task / 20-run hard-tier pilot with outcome failures. |
| `benchmark/hard/pilot/hard10-real/manual-labels.jsonl` | Manual hidden-failure labels for hard-tier RQ2 analysis. |

## Reproduce Tables From Stored Traces

Full 30-task aggregate:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research aggregate \
  benchmark/pilot/full30-real/runs.jsonl \
  --json-output /tmp/full30-aggregate.json \
  --markdown-output /tmp/full30-aggregate.md \
  --csv-output /tmp/full30-runs.csv
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
  benchmark/hard/pilot/hard10-real/runs.jsonl \
  --labels benchmark/hard/pilot/hard10-real/manual-labels.jsonl \
  --json-output /tmp/hard10-paper-report.json \
  --markdown-output /tmp/hard10-paper-report.md
```

Combined paper-facing summary:

```bash
PYTHONPATH=. python3 -m codex_trace.cli research summary \
  --markdown-output /tmp/results-summary.md \
  --json-output /tmp/results-summary.json
```

## Claim-Evidence Map

| Claim | Evidence | Current status |
| --- | --- | --- |
| CodexTrace parses Codex JSONL traces and emits reports. | `codex_trace/parser.py`, `codex_trace/diagnose.py`, `demo/`, `tests/` | Implemented and CI-tested. |
| The benchmark has a 30-task seed tier and two prompt conditions. | `benchmark/tasks.jsonl`, `benchmark/prompts/`, `benchmark/pilot/full30-real/runs.jsonl` | Implemented; 60 real stored runs. |
| The benchmark has a hard tier with hidden graders. | `benchmark/hard/tasks.jsonl`, `benchmark/hard/repos/`, `benchmark/hard/pilot/hard10-real` | Implemented; 33 runnable hard tasks and 20 real stored hard10 runs. |
| Hidden graders are not exposed during Codex execution. | `codex_trace/research.py`, `public_success_check` fields, hard-tier prompts | Implemented; hidden grader copied after Codex exits. |
| Full30 intervention reduces process waste. | `benchmark/pilot/full30-real/aggregate.md` | Supported: repeated tool calls `10.43 -> 7.00`, token usage `218.7k -> 184.8k`. |
| Hard10 intervention improves success and reduces waste. | `benchmark/hard/pilot/hard10-real/aggregate.md` | Supported: success `0.70 -> 0.80`, repeated tool calls `9.20 -> 6.20`, token usage `248.9k -> 187.5k`. |
| Trace-only process rules miss hidden semantic edge failures. | `benchmark/hard/pilot/hard10-real/label-eval.md` | Supported as a boundary result: `TP=0`, `FP=0`, `FN=5` for `hidden_semantic_edge_case`. |
| Hard10 process signals explain the detector boundary. | `docs/results_summary.md` RQ4 table | Supported: `verification_rate`, `unresolved_error`, `command_failure_count`, and `failure_score` are equal for success and failure outcomes. |
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
failed_initial_count 33
failed_initial ['HARD-001', 'HARD-002', 'HARD-003', 'HARD-004', 'HARD-005', 'HARD-006', 'HARD-007', 'HARD-008', 'HARD-009', 'HARD-010', 'HARD-011', 'HARD-012', 'HARD-013', 'HARD-014', 'HARD-015', 'HARD-016', 'HARD-017', 'HARD-018', 'HARD-019', 'HARD-020', 'HARD-021', 'HARD-022', 'HARD-023', 'HARD-024', 'HARD-025', 'HARD-026', 'HARD-027', 'HARD-028', 'HARD-029', 'HARD-030', 'HARD-031', 'HARD-032', 'HARD-033']
```

## Current Gaps Before A Stronger Submission

- Expand the hard tier from 10 tasks toward 30-50 tasks.
- Add more observable process failures, not only hidden semantic failures.
- Add repeated trials or randomization to reduce prompt/order effects.
- Consider a lightweight semantic analysis layer for hidden edge-case failures.
- Improve detector evaluation with richer manual labels beyond the current
  hard-tier boundary label.

For a concrete expansion backlog and submission decision gate, see
`docs/submission_readiness_plan.md`. For the implemented HARD-011 to HARD-033
fixtures and next candidates, see
`docs/hard_tier_expansion_blueprint.md`.
