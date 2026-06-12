# Process-Stress Tier

This is a runnable benchmark slice for closing the original-thesis evidence gaps
tracked in `docs/thesis_readiness.md`.

The stored hard30 artifact is submission-ready for a boundary-result paper, but
it does not support two stronger original-thesis claims:

- intervention improves verification rate
- trace rules detect a broad set of observable process failures

The process-stress tier targets those claims directly. Its tasks are designed
to make process failures observable in the trace rather than only in hidden
semantic graders.

## Design

- 12 materialized tasks, `PST-001` to `PST-012`
- 2 tasks per target process label where possible
- baseline and intervention prompt conditions
- public success checks stay visible to the agent
- hidden graders still run outside the agent worktree after execution
- initial fixture repositories fail their public success checks before agent
  edits, so each run requires concrete repair work

Target labels:

- `verification_gap`
- `unrecovered_tool_error`
- `repetitive_exploration`
- `context_drift`
- `premature_completion`
- `sandbox_permission_deadlock`

## Acceptance Gate

Use this tier to update the original thesis only if the collected runs show:

- process-label recall at least `0.70` on observable manual labels
- no detector label with precision below `0.60`
- verification rate or verification-depth improvement under intervention
- reduced repeated tool calls or token usage under intervention

If verification remains saturated, keep the paper framed around waste reduction
and detector-boundary results rather than claiming verification-rate lift.

## Current Full Pilot

`benchmark/process-stress/pilot/full-real` contains the current real collection:

- tasks: `PST-001` to `PST-012`
- runs: 24 baseline/intervention Codex JSONL traces
- success rate: `0.9167 -> 0.9167`
- verification rate: `1.00 -> 1.00`
- repeated tool calls: `8.08 -> 7.17`
- recover events: `1.25 -> 0.83`
- token usage: `209.0k -> 185.1k`

This pilot validates the collection path and shows process-waste reduction, but
it still does not close the original-thesis verification-rate lift claim.
