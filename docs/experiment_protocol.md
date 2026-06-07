# Experiment Protocol

Paper title:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

## Research Questions

- RQ1: What observable failure modes appear in multi-turn coding-agent traces?
- RQ2: Can these failure modes be detected from trace signals alone?
- RQ3: Do simple harness interventions improve success or reduce waste?
- RQ4: Which trace signals best explain whether a run will fail?

## Dataset

Target size:

- 30-50 small coding tasks
- two prompt conditions per task: `baseline` and `intervention`
- one JSONL trace per run
- one outcome label per run

Current seed:

- `benchmark/tasks.jsonl` contains 30 tasks
- `benchmark/repos` contains runnable fixture repositories and external graders
- `benchmark/hard/tasks.jsonl` contains 47 runnable hard-tier tasks with
  hidden graders
- `benchmark/hard/repos` contains runnable hard-tier fixture repositories and
  hidden grader directories
- `benchmark/prompts/baseline.txt`
- `benchmark/prompts/intervention.txt`
- `benchmark/smoke/tasks.jsonl` contains 3 runnable fixtures for harness validation

## Prompt Conditions

Baseline:

- normal `codex exec` task prompt
- no explicit process constraints beyond the task and success check

Intervention:

- inspect first
- state minimal edit
- make focused change
- run post-edit verification
- diagnose before retrying failed commands
- finish only with evidence

## Run Collection

Validate the collection harness without spending model calls:

```bash
codex-trace research run \
  --tasks benchmark/smoke/tasks.jsonl \
  --output-dir runs/smoke-dry \
  --dry-run
```

For each task and prompt condition, use the collection runner:

```bash
codex-trace research run \
  --tasks benchmark/tasks.jsonl \
  --output-dir runs/full \
  --timeout-seconds 300
```

The runner copies the fixture repo into an isolated run directory, initializes a
fresh git repository, executes `codex exec --json`, then runs the task's external
grader from outside the agent worktree. For hidden-grader tasks, the prompt
contains only `public_success_check`; the hidden grader directory is copied into
the run directory only after the Codex process exits. It writes a run manifest:

```jsonl
{"task_id":"CT-001","prompt_type":"baseline","trace_path":"runs/CT-001/baseline.jsonl","outcome":"failure"}
{"task_id":"CT-001","prompt_type":"intervention","trace_path":"runs/CT-001/intervention.jsonl","outcome":"success"}
```

Outcome labels:

- `success`: final code passes the stated success check
- `failure`: final code fails the stated success check or does not implement the task
- `unknown`: run could not be judged

## Metrics

Run-level metrics:

- `success`
- `verification_rate`
- `unresolved_error`
- `repeated_tool_call_count`
- `retry_count`
- `command_failure_count`
- `token_usage`
- `failure_score`
- `turn_count`
- `time_to_first_edit`
- `time_to_first_test`
- `phase_inspect_events`
- `phase_edit_events`
- `phase_verify_events`
- `phase_recover_events`

Group-level metrics:

- `success_rate`
- `verification_rate`
- `unresolved_error_rate`
- `avg_repeated_tool_calls`
- `avg_retry_count`
- `avg_command_failures`
- `avg_recover_events`
- `avg_verify_events`
- `avg_token_usage`
- `avg_failure_score`

Detector evaluation metrics:

- per-label precision
- per-label recall
- per-label F1
- micro F1
- macro F1

## Aggregation

```bash
codex-trace research aggregate benchmark/runs.example.jsonl \
  --json-output reports/example-aggregate.json \
  --markdown-output reports/example-aggregate.md \
  --csv-output reports/example-runs.csv
```

Generate a manual annotation template:

```bash
codex-trace research label-template benchmark/runs.example.jsonl \
  --include-predictions \
  --output reports/example-label-template.jsonl
```

Evaluate detector labels against manual annotations:

```bash
codex-trace research evaluate-labels benchmark/runs.example.jsonl benchmark/labels.example.jsonl \
  --json-output reports/example-label-eval.json \
  --markdown-output reports/example-label-eval.md
```

Generate paper-ready RQ1-RQ4 tables:

```bash
codex-trace research paper-report benchmark/runs.example.jsonl \
  --labels benchmark/labels.example.jsonl \
  --json-output reports/example-paper-report.json \
  --markdown-output reports/example-paper-report.md
```

## Minimal Acceptance Bar For A Workshop-Style Draft

- 30 tasks x 2 prompt conditions
- at least 60 trace files
- manually verified outcome labels
- taxonomy distribution table
- baseline vs intervention table
- qualitative examples for 3-4 failure modes

Current pilot status:

- `benchmark/pilot/smoke-real`: 3 smoke tasks x 2 prompt conditions
- `benchmark/pilot/batch1-real`: 7 non-smoke tasks x 2 prompt conditions
- `benchmark/pilot/batch2-real`: 8 non-smoke tasks x 2 prompt conditions
- `benchmark/pilot/batch3-real`: 15 non-smoke tasks x 2 prompt conditions
- `benchmark/pilot/full30-real`: 30 non-smoke tasks x 2 prompt conditions
- `benchmark/hard/pilot/hard10-real`: 10 hard tasks x 2 prompt conditions
- The full 30-task pilot has 60/60 successful outcomes. It validates collection
  and process-metric analysis, but a harder tier is still needed for
  outcome-failure analysis.
- The hard 10-task pilot has 15/20 successful outcomes. Baseline success is
  `0.7`, intervention success is `0.8`, repeated tool calls drop from
  `9.2 -> 6.2`, and average token usage drops from about `248.9k -> 187.5k`.
  These traces supply the first outcome-failure examples, while also showing a
  limitation of trace-only rules: hidden semantic edge failures can receive
  `failure_score=0` when the visible process looks clean.
- `benchmark/hard/pilot/hard10-real/manual-labels.jsonl` labels the 5 hard-tier
  failures as `hidden_semantic_edge_case`. The current process-only detector has
  `TP=0`, `FP=0`, `FN=5` for that label, giving micro/macro F1 of `0`. This is
  an explicit RQ2 boundary result: trace rules can explain observable process
  failures, but hidden semantic edge cases require stronger oracles or separate
  semantic analysis.

Required next dataset extension:

- expand the hard tier beyond 10 tasks
- include at least several additional expected baseline failures
- keep hidden graders outside the agent worktree during Codex execution
- target tasks where success requires preserving multiple invariants, diagnosing
  misleading visible tests, or avoiding over-broad edits

## Threats To Validity

- single-agent/single-interface study
- small benchmark tasks may not represent large repositories
- rule-based labels are interpretable but incomplete
- final success labels can require manual judgment
- prompt intervention may change verbosity as well as behavior
