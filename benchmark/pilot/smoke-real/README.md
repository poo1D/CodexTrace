# Smoke Pilot: Real Codex Runs

This directory contains a small real-run pilot collected with:

```bash
codex-trace research run \
  --tasks benchmark/smoke/tasks.jsonl \
  --prompt-types baseline intervention \
  --output-dir /tmp/codextrace-smoke-real-runs \
  --timeout-seconds 300
```

It is a pipeline sanity check, not the paper's final benchmark. All 3 smoke
tasks succeeded under both prompt conditions, so the pilot validates trace
collection, parsing, aggregation, and paper-table generation, but it does not
support conclusions about failure-taxonomy prevalence.

Included artifacts:

- `runs.jsonl`: run manifest with task outcomes.
- `*/trace.jsonl`: raw `codex exec --json` traces.
- `*/prompt.md`: rendered prompt used for each run.
- `*/success_check.txt`: final success-check output.
- `labels.jsonl`: manual-label skeleton; all failure tags are empty for this pilot.
- `aggregate.*`: baseline vs intervention aggregate outputs.
- `paper-report.*`: RQ1-RQ4 paper-table outputs for the pilot.
