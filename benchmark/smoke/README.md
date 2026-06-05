# Smoke Benchmark

This suite contains three tiny runnable tasks used to validate the full
research harness before collecting the 30-50 task paper benchmark.

Run a dry collection:

```bash
codex-trace research run \
  --tasks benchmark/smoke/tasks.jsonl \
  --output-dir runs/smoke-dry \
  --dry-run
```

Run one real baseline/intervention pair:

```bash
codex-trace research run \
  --tasks benchmark/smoke/tasks.jsonl \
  --task-id SM-001 \
  --output-dir runs/smoke-real
```

The runner copies each fixture repository into an isolated workdir, writes the
rendered prompt, captures `codex exec --json` to `trace.jsonl`, runs the task's
success check, and writes `runs.jsonl`.
