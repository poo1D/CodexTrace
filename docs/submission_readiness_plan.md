# Submission Readiness Plan

This plan tracks the gap between the current CodexTrace artifact and a stronger
paper submission for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

The current repository is already useful as a GPU-free research artifact and CV
project. A stronger submission needs more evidence around scale, observable
process failures, and repeatability.

## Current Evidence Level

| Area | Current state | Submission risk |
| --- | --- | --- |
| System artifact | Parser, diagnosis engine, CLI, Web UI, benchmark runner, hidden-grader support. | Low. The system is implemented and CI-tested. |
| Seed benchmark | 30 tasks, 60 real Codex runs, all outcomes pass. | Medium. Good for waste analysis, weak for failure-distribution claims. |
| Hard benchmark | 41 runnable tasks; the evaluated hard10 pilot has 10 tasks, 20 real Codex runs, and 5 outcome failures. | Medium. Good pilot, small sample for success-rate claims. |
| Detector evaluation | Manual labels expose `TP=0`, `FP=0`, `FN=5` for hidden semantic edge cases. | Medium. Strong boundary result, but not enough positive process-failure labels. |
| RQ4 signal analysis | Hard10 signal table explains why clean traces can still fail hidden graders. | Medium. Needs more observable failures to identify predictive process signals. |

## Target For A Stronger Submission

The next submission-ready target should be:

- 30-50 hard-tier tasks.
- 60-100 hard-tier runs across baseline and intervention.
- At least 15-25 manually labeled outcome failures.
- A mix of hidden semantic failures and observable process failures.
- Repeated trials for at least a subset of tasks to reduce prompt-order noise.
- A paper draft whose main claims are supported by generated tables.

## Workstream 1: Expand Hard-Tier Tasks

Goal: move from the evaluated `hard10` pilot to a harder 30-50 task suite
while preserving hidden grader isolation. `HARD-011` through `HARD-041` are now
implemented; the next candidates are tracked in
`docs/hard_tier_expansion_blueprint.md`.

Tasks to add:

| Category | Target count | Desired failure pressure |
| --- | ---: | --- |
| hidden semantic edge cases | 10-15 | Visible tests pass but hidden grader catches edge behavior. |
| multi-step feature changes | 5-10 | Agent must preserve earlier requirements while adding later ones. |
| error-recovery tasks | 5-8 | Initial verification fails and requires a targeted repair. |
| dependency/sandbox-friction tasks | 3-5 | Agent must adapt command strategy without deadlocking. |
| refactor-with-invariants tasks | 5-8 | Agent can over-edit or miss behavioral invariants. |

Acceptance criteria:

- Every new task has `public_success_check` and hidden `success_check` when
  hidden behavior is required.
- Initial fixture fails the hidden grader before agent edits.
- The prompt never exposes hidden grader details.
- Each task has a short category and expected failure-pressure note.

## Workstream 2: Improve Manual Labeling

Goal: make RQ1 and RQ2 stronger by labeling both outcome failures and
observable process failures.

Add labels for:

- `verification_gap`
- `unrecovered_tool_error`
- `repetitive_exploration`
- `context_drift`
- `premature_completion`
- `sandbox_permission_deadlock`
- `hidden_semantic_edge_case`

Acceptance criteria:

- Each failed run has at least one manual label.
- Each label includes a one-line rationale or evidence pointer.
- The label file can be evaluated by `codex-trace research evaluate-labels`.
- Positive examples exist for at least four process-level labels.

## Workstream 3: Repeatability And Variance

Goal: reduce the risk that observed improvements are one-off prompt or sampling
effects.

Recommended design:

- Run all hard tasks once under baseline and intervention.
- Re-run a stratified subset of 10-15 tasks with a second seed or fresh Codex
  session.
- Report aggregate means plus per-task paired deltas.

Acceptance criteria:

- Repeated subset has a separate manifest.
- Results summary reports whether intervention gains persist under repeats.
- Paper distinguishes pilot-scale evidence from stable estimates.

## Workstream 4: Better RQ4 Analysis

Goal: identify trace signals that explain observable failures, not only show
the hidden-semantic boundary.

Candidate additions:

- Per-signal effect sizes between success and failure outcomes.
- Per-label signal means for process-failure labels.
- A simple threshold table for high-confidence warning signals.
- Optional logistic-regression or decision-stump analysis, only if sample size
  becomes large enough.

Acceptance criteria:

- RQ4 table separates at least one observable failure class.
- Hidden semantic failures remain reported as a boundary case.
- The paper does not overclaim trace-only prediction for semantic correctness.

## Workstream 5: Paper Polish

Goal: make the paper read like an honest systems/evaluation artifact, not a
demo writeup.

Required edits:

- Add an artifact availability paragraph.
- Add a clearer dataset construction table.
- Add a limitations paragraph that distinguishes process diagnosis from
  semantic correctness.
- Add a short "why no GPU is needed" method note.
- Keep all numeric claims tied to generated artifacts.

Acceptance criteria:

- `docs/paper_draft.md` can be read independently of the README.
- `docs/artifact_guide.md` gives a fast review path.
- `docs/reproducibility_checklist.md` maps every headline claim to evidence.

## Decision Gate

Treat the project as submission-ready only when:

- Hard tier has at least 30 tasks and 60 hard-tier runs.
- Detector evaluation includes both positive and negative examples for
  observable process failures.
- RQ3 improvement is visible in either success rate, waste metrics, or both.
- RQ4 has at least one signal analysis result beyond the hidden-semantic
  boundary.
- CI passes and all generated result tables can be reproduced from stored
  manifests.

Until then, the honest positioning is:

> A reproducible pilot artifact showing that trace diagnosis can measure
> process failures and harness-level waste reductions, with an explicit boundary
> result for hidden semantic failures.
