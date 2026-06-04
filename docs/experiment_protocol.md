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
- `benchmark/prompts/baseline.txt`
- `benchmark/prompts/intervention.txt`

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

For each task and prompt condition:

```bash
codex-trace research prompt CT-001 baseline > /tmp/prompt.txt
codex exec --json "$(cat /tmp/prompt.txt)" > runs/CT-001/baseline.jsonl

codex-trace research prompt CT-001 intervention > /tmp/prompt.txt
codex exec --json "$(cat /tmp/prompt.txt)" > runs/CT-001/intervention.jsonl
```

Then label the outcome:

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
- `command_failure_count`
- `token_usage`
- `failure_score`
- `turn_count`
- `time_to_first_edit`
- `time_to_first_test`

Group-level metrics:

- `success_rate`
- `verification_rate`
- `unresolved_error_rate`
- `avg_repeated_tool_calls`
- `avg_command_failures`
- `avg_token_usage`
- `avg_failure_score`

## Aggregation

```bash
codex-trace research aggregate benchmark/runs.example.jsonl \
  --json-output reports/example-aggregate.json \
  --markdown-output reports/example-aggregate.md \
  --csv-output reports/example-runs.csv
```

## Minimal Acceptance Bar For A Workshop-Style Draft

- 30 tasks x 2 prompt conditions
- at least 60 trace files
- manually verified outcome labels
- taxonomy distribution table
- baseline vs intervention table
- qualitative examples for 3-4 failure modes

## Threats To Validity

- single-agent/single-interface study
- small benchmark tasks may not represent large repositories
- rule-based labels are interpretable but incomplete
- final success labels can require manual judgment
- prompt intervention may change verbosity as well as behavior
