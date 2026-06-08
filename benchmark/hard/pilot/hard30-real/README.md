# Hard30 Real Pilot

This directory stores the 30-task / 60-run hard-tier CodexTrace artifact.

Key files:

- `runs.jsonl`: merged baseline/intervention manifest.
- `aggregate.md`: aggregate baseline vs intervention metrics.
- `paper-report-labeled.md`: paper-facing RQ1-RQ4 tables with manual labels.
- `paired-task-summary.csv`: paired task improvement/regression counts.
- `label-eval.md`: detector-vs-manual-label evaluation.
- `manual-label-audit.md`: manual-label completeness and coverage audit.
- `readiness.md`: submission-readiness gate output.
- `shards/*/*/*/trace.jsonl`: raw `codex exec --json` traces.

The collected shard directories keep traces, prompts, success-check text, stderr,
and per-shard metadata. Temporary materialized workdirs and copied hidden
graders are pruned from this artifact; they can be regenerated from
`benchmark/hard/repos/` and `benchmark/hard/pilot/hard30-selection/tasks.jsonl`.
