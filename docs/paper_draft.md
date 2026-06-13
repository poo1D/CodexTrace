# When Coding Agents Get Lost

Trace-Based Diagnosis of Multi-Turn Tool-Use Failures

## Abstract

Coding agents increasingly solve software tasks by inspecting repositories,
calling tools, editing files, running commands, and producing final summaries.
However, most evaluations reduce this process to a final success or failure
label. This hides a useful class of failures that happen inside the tool-use
loop: missing verification, unrecovered tool errors, repetitive exploration,
context drift, premature completion, and sandbox or permission deadlocks.

We introduce CodexTrace, an offline parser and diagnosis engine for
`codex exec --json` traces. CodexTrace normalizes agent events into a stable
schema, segments runs into phases, detects interpretable process-level failure
patterns, and aggregates baseline-vs-intervention experiments. We evaluate the
tool on seven real Codex benchmark pilots: a 30-task seed benchmark with 60
runs, an early 10-task hard tier with 20 runs, a 30-task hard tier with 60
runs and hidden edge-case graders, a 12-task process-stress tier, an 8-task
verification-lift tier, an 8-task ordinary-baseline verification-lift-v2
rerun, and a 4-task no-verify ablation. The ordinary and weak-baseline pilots
have saturated verification rates, so they do not support a
verification-rate-lift claim. On the seed pilot, all runs succeed, but the
intervention reduces repeated tool calls from 10.43 to 7.00 and average token
usage from 218.7k to 184.8k. On the hard30 tier, success rate stays flat at
50%, but the intervention reduces repeated tool calls from 12.93 to 9.20,
average token usage from 355.0k to 256.3k, and failure score from 3.50 to
1.17.
A manual-label analysis also shows a boundary of trace-only diagnosis: 30
hidden semantic edge-case failures are missed by deterministic process rules
because their visible process traces often look clean. These results suggest
that trace-based diagnosis is useful for exposing observable process failures
and measuring harness interventions, but it should be paired with strong
semantic oracles for hidden correctness failures.

## 1. Introduction

Coding agents are no longer single-shot code generators. A typical run may
inspect files, search a repository, edit source code, run tests, retry failed
commands, and finally summarize the result. When the final answer is wrong, a
user often sees only the failed task outcome, not where the agent lost its way.
Conversely, when the final answer is correct, the trace may still reveal wasted
work, brittle verification, or recoverable harness friction.

This paper studies coding-agent failures as multi-turn tool-use failures. The
central claim is not that a trace analyzer can replace task-level evaluation.
Rather, the claim is narrower: many coding-agent failures and inefficiencies
leave observable traces, and simple harness interventions can reduce some of
them without retraining a model.

We ask four research questions:

- RQ1: What observable failure modes appear in multi-turn coding-agent traces?
- RQ2: Can these failure modes be detected from trace signals alone?
- RQ3: Do simple harness interventions improve success or reduce waste?
- RQ4: Which trace signals explain observable process failures, and where do
  they fail to explain hidden semantic outcomes?

## 2. Related Work

Software-engineering benchmarks such as
[SWE-bench](https://arxiv.org/abs/2310.06770) evaluate whether language models
can resolve real GitHub issues by editing repositories and passing tests. This
work is complementary: CodexTrace keeps task outcome labels, but treats the
agent trace itself as a first-class evaluation object.

Coding-agent systems and interfaces such as
[SWE-agent](https://arxiv.org/abs/2405.15793),
[OpenHands](https://arxiv.org/abs/2407.16741), and the
[OpenAI Codex CLI](https://github.com/openai/codex) show that modern coding
agents act through developer-like tools: shell commands, file edits, tests, and
repository navigation. CodexTrace does not propose a new agent interface; it
analyzes whether an existing harness produces observable process failures and
whether a simple prompt-level intervention changes those traces.

General agent-evaluation work such as
[AgentBench](https://arxiv.org/abs/2308.03688) evaluates multi-turn agents in
interactive environments. Program-repair agents such as
[RepairAgent](https://arxiv.org/abs/2403.17134) further show that autonomous
repair workflows can consume substantial token budgets. These lines motivate
tracking tool-call waste, recovery behavior, and token usage rather than only
final correctness.

The closest diagnostic thread is trajectory-level agent failure analysis, such
as [AgentRx](https://www.microsoft.com/en-us/research/publication/agentrx-diagnosing-ai-agent-failures-from-execution-trajectories/),
which diagnoses failures from execution trajectories. CodexTrace is narrower
and more structural: it focuses on coding-agent JSONL traces and uses
deterministic process rules before considering LLM-as-judge or semantic
diagnosis.

Table 1 summarizes the positioning. CodexTrace is not intended to replace
outcome benchmarks, agent frameworks, or semantic failure diagnosis. Its
contribution is a process-level layer that can be run after a coding-agent run
to explain observable tool-use failures and quantify harness interventions.

| Work line | Primary question | Typical evidence | CodexTrace difference |
| --- | --- | --- | --- |
| SWE-bench-style benchmarks | Did the patch solve a real issue? | Final tests or issue-level success | Keeps outcome labels, but analyzes how the run unfolded. |
| Coding-agent frameworks | Which interface lets agents edit and test code? | Agent success under a tool interface | Does not propose a new interface; diagnoses traces from an existing one. |
| General agent benchmarks | Can agents act in multi-turn environments? | Task score across environments | Narrows to coding traces and software-process failure modes. |
| Trajectory diagnosis | Where did an agent execution fail? | Failure localization over trajectories | Uses deterministic coding-specific rules and aggregate intervention metrics. |

## 3. Problem Definition

We define a coding-agent run as:

```text
Run = task prompt + tool-use trace + final answer + outcome label
```

The final outcome is necessary but not sufficient. Two runs can both succeed
while one wastes far more tool calls, repeats failed searches, or reaches the
answer only after preventable harness friction. Similarly, a run can have a
clean-looking process trace and still fail a hidden semantic edge case.

We define a process-level failure as a detectable trace pattern that either
reduces the probability of success or increases wasted effort before the final
outcome is known.

## 4. Failure Taxonomy

CodexTrace uses an interpretable taxonomy of observable tool-use failures:

| Failure mode | Trace-level signal |
| --- | --- |
| `verification_gap` | File edits occur, but no post-edit test/build/lint/type-check command follows. |
| `unrecovered_tool_error` | A command fails and no later repair or verification step resolves it. |
| `repetitive_exploration` | The agent repeats equivalent search/read commands. |
| `context_drift` | The trace accumulates context without implementation progress or task-relevant verification. |
| `premature_completion` | The agent claims completion without verification evidence. |
| `sandbox_permission_deadlock` | Permission, network, or sandbox errors repeat without a strategy change. |

The hard-tier pilot adds one manual label that is not a process-level detector:
`hidden_semantic_edge_case`. This label marks runs whose visible trace looks
procedurally clean but whose final code fails hidden edge-case tests.

## 5. Method: CodexTrace

CodexTrace is a lightweight offline analysis pipeline:

```text
codex exec --json
        -> JSONL event parser
        -> normalized trace schema
        -> phase segmentation
        -> failure pattern detector
        -> diagnosis report
        -> baseline vs intervention comparison
```

The normalized trace schema records the fields needed for process diagnosis
without preserving the full raw event payload in every downstream table:

| Schema object | Fields | Purpose |
| --- | --- | --- |
| `Run` | task id, prompt type, outcome, source trace, usage | Unit of experimental comparison and aggregation. |
| `TraceEvent` | id, kind, status, title/detail, raw type, timestamp | Stable event representation across Codex JSONL variants. |
| tool evidence | command, exit code, files, metadata | Captures shell/tool behavior and file-change evidence. |
| process state | phase, event ids, finding code, severity | Supports phase counts, detector evidence, and diagnosis reports. |

For paper reporting, CodexTrace exposes the schema in the Run/Step form used
by the experiment protocol:

| Paper field | Implementation source | Notes |
| --- | --- | --- |
| `Run.task_id` | run manifest `task_id` | Stable task identifier. |
| `Run.prompt_type` | run manifest `prompt_type` | `baseline` or `intervention`. |
| `Run.outcome` | run manifest `outcome` | External grader label. |
| `Run.usage` | Codex JSONL usage metadata | Token counts when present. |
| `Step.timestamp` | event timestamp / ordering | Missing timestamps fall back to trace order. |
| `Step.event_type` | `TraceEvent.kind` and `raw_type` | Normalized event kind plus original Codex type. |
| `Step.content` | event title/detail | Human-readable command, message, or evidence snippet. |
| `Step.tool_name` | command/tool event metadata | Shell command, MCP tool, or web/search tool name. |
| `Step.command` | `TraceEvent.command` | Normalized shell command for command events. |
| `Step.status` | `TraceEvent.status` and exit code | Completed, failed, blocked, or error-like status. |
| `Step.error` | failed/error event detail | Derived from failed commands, error events, or blocked tool output. |
| `Step.file_paths` | file-change metadata | Paths touched by file-change events. |
| `Step.token_usage` | run usage plus event metadata | Used for run-level token metrics and context-drift signals. |
| `Step.phase` | phase segmenter output | setup, inspect, edit, verify, recover, complete, or other. |
| `Step.failure_tags` | detector/manual-label outputs | Process taxonomy tags attached during diagnosis or labeling. |

The phase segmenter maps events into setup, inspect, edit, verify, recover,
complete, and other. It uses command shape, file-change events, completion
messages, and failed-command context to infer whether later work is still
inspection, active editing, verification, or recovery.

The detector emits rule-based findings with evidence snippets and
recommendations. The paper-facing taxonomy maps to implementation findings as
follows:

| Taxonomy label | Implementation finding | Detector signal |
| --- | --- | --- |
| `verification_gap` | `verification_gap` | File changes occur and no post-edit verification command follows. |
| `unrecovered_tool_error` | `command_failure_unhandled` | A failed command is not followed by a similar successful command or verification. |
| `repetitive_exploration` | `repeated_search_or_read` | Search/read commands repeat or repeated tool-call volume exceeds the threshold. |
| `context_drift` | `long_context_no_progress` | High input-token usage with little implementation or verification progress. |
| `premature_completion` | `premature_completion` | Final completion language appears after edits without verification evidence. |
| `sandbox_permission_deadlock` | `sandbox_or_permission_block` | Failed or blocked events mention sandbox, permission, approval, or denial. |

The research runner materializes fixture repositories in isolated run
directories, executes `codex exec --json`, and then runs an external success
check. For hard-tier tasks, the prompt exposes only a public success check such
as `python3 -m unittest discover -s tests` or `npm test`; the hidden grader is
copied into the run directory only after the Codex process exits.

No model training, fine-tuning, embedding index, or GPU inference is used by
CodexTrace itself. Once `codex exec --json` traces have been collected, all
normalization, phase segmentation, failure detection, aggregation, manual-label
evaluation, and report generation run as deterministic local Python code over
stored JSONL, JSON, CSV, and Markdown artifacts.

## 6. Benchmark

The current benchmark is organized as a seed tier, a hard hidden-grader tier,
and auxiliary stress tiers used to probe specific claims.

| Tier | Tasks | Runs | Baseline | Intervention | Outcome oracle | Primary use |
| --- | ---: | ---: | --- | --- | --- | --- |
| seed full30 | 30 | 60 | ordinary prompt | evidence-gated prompt | external visible grader | waste analysis with saturated success |
| hard10 | 10 | 20 | ordinary prompt | evidence-gated prompt | hidden grader | early outcome-failure pilot |
| hard30 | 30 | 60 | ordinary prompt | evidence-gated prompt | hidden grader | paper-facing boundary and RQ3 artifact |
| process-stress | 12 | 24 | ordinary prompt | evidence-gated prompt | hidden grader | observable-process stress slice |
| verification-lift | 8 | 16 | weak optional-verification prompt | evidence-gated prompt | hidden grader | negative stress test for verification-rate lift |
| verification-lift-v2 | 8 | 16 | ordinary prompt | evidence-gated prompt | hidden grader | negative ordinary-baseline retest for verification-rate lift |
| verification-ablation | 4 | 8 | explicit no-verify prompt | evidence-gated prompt | hidden grader | mechanism ablation for harness-controlled verification |

The seed tier contains 30 runnable coding tasks covering bug fixes, features,
test writing, refactors, CI failures, error localization, and multi-turn
changes. Each task is run with two prompt conditions:

- `baseline`: a normal task prompt with a visible success check.
- `intervention`: a harness-constrained prompt requiring inspection, minimal
  edits, post-edit verification, failed-command diagnosis, and evidence before
  completion.

The hard tier contains 50 runnable harder tasks with hidden graders. The
current paper-facing hard30 artifact selects 30 of these tasks and stores 60
real baseline/intervention runs. These tasks are designed to create outcome
failures even when visible tests pass.

### Measurement

The experiment design tracks both final outcomes and process-level waste. Each
metric is computed from the normalized trace plus the run manifest outcome
field; the generated `docs/metric_coverage_audit.md` checks that all metrics in
this table are present in run rows, CSV exports, baseline/intervention
summaries, and aggregate Markdown.

| Metric | Measurement |
| --- | --- |
| `success_rate` | Mean of binary run success labels from the external outcome oracle. |
| `verification_rate` | Share of runs with at least one test, build, lint, type-check, or equivalent verification command. |
| `unresolved_error_rate` | Share of runs with a failed command that is not followed by recovery or verification evidence. |
| `repeated_tool_call_count` | Count of repeated shell/search/read-style commands after the first occurrence. |
| `retry_count` | Count of commands retried after a previous failure of the same normalized command. |
| `turn_count` | Count of completed agent turns in the normalized trace. |
| `token_usage` | Input plus output token usage reported by the Codex JSONL stream when present. |
| `command_failure_count` | Count of command events with non-zero exit status. |
| `time_to_first_edit` | Event index of the first file-change event. |
| `time_to_first_test` | Event index of the first verification command; undefined runs are excluded from group averages. |
| `failure_score` | Weighted deterministic score over detector findings, used as a compact process-risk measure. |

## 7. Results

### RQ1: Failure Taxonomy Distribution

On the 30-task seed pilot, all 60 runs pass their external graders. CodexTrace
still detects one process failure: `CT-021/baseline` hits a sandbox or
permission deadlock pattern and receives a failure score of 35.

On the hard30 tier, manual labels mark 30 hidden semantic edge-case failures
and 4 high-volume `repetitive_exploration` process positives identified during
trace review.

| Pilot | Labeled failure tag | Count | Example |
| --- | --- | ---: | --- |
| full30 | `sandbox_permission_deadlock` | 1 | `CT-021/baseline` |
| hard30 | `hidden_semantic_edge_case` | 30 | `HARD-001/baseline` |
| hard30 | `repetitive_exploration` | 4 | `HARD-011/baseline` |

### RQ2: Detector Agreement

The current process-only detector has two different evaluation surfaces. First,
on controlled detector fixtures where each process failure mode is explicitly
present in a minimal JSONL trace, it recovers all six taxonomy labels:

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `context_drift` | 1 | 0 | 0 | 1 | 1 | 1 |
| `premature_completion` | 1 | 0 | 0 | 1 | 1 | 1 |
| `repetitive_exploration` | 1 | 0 | 0 | 1 | 1 | 1 |
| `sandbox_permission_deadlock` | 1 | 0 | 0 | 1 | 1 | 1 |
| `unrecovered_tool_error` | 2 | 0 | 0 | 1 | 1 | 1 |
| `verification_gap` | 2 | 0 | 0 | 1 | 1 | 1 |

Second, on real pilot traces, the detector identifies reviewed observable
process positives but does not detect hidden semantic edge cases. For the
hard30 manual labels, detector agreement is:

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `hidden_semantic_edge_case` | 0 | 0 | 30 | 0 | 0 | 0 |
| `repetitive_exploration` | 4 | 0 | 0 | 1 | 1 | 1 |

This is a boundary result rather than a contradiction of trace diagnosis. The
detectors target process evidence; hidden semantic failures may require visible
edge tests, stronger task oracles, or a semantic analysis layer. The
`repetitive_exploration` row shows that process-positive labels can be detected
from trace signals when the failure mode is actually observable.

A full30 process-positive slice adds one reviewed
`sandbox_permission_deadlock` example with TP=1, FP=0, FN=0, while also
showing two `repetitive_exploration` false positives. This gives a more useful
claim than "rules detect everything": deterministic trace rules can recover
explicit process failures, but they still require threshold tuning and do not
replace semantic task oracles.

### RQ3: Baseline vs Intervention

Table 4 summarizes the paper-facing result in the compact form implied by the
thesis. The current evidence supports success improvement only in the early
hard10 pilot, supports waste reduction most strongly on hard30, and gives a
negative result for verification-rate lift under ordinary or weak-baseline
conditions.

| Evidence slice | Baseline | Intervention | Interpretation |
| --- | ---: | ---: | --- |
| hard10 success | 0.70 | 0.80 | Pilot success lift; not stable enough alone for a broad claim. |
| hard30 waste | 12.93 repeated calls / 355.0k tokens | 9.20 repeated calls / 256.3k tokens | Supported paired waste reduction with flat success. |
| verification-lift stress | 1.00 broad / 1.00 exact | 1.00 broad / 1.00 exact | Negative result for ordinary or weak-baseline verification-rate lift. |
| verification-lift-v2 ordinary retest | 1.00 broad / 1.00 exact | 1.00 broad / 1.00 exact | Negative ordinary-baseline retest; waste still improves. |
| no-verify ablation | 0.00 broad / 0.00 exact | 1.00 broad / 1.00 exact | Mechanism check only; not an ordinary baseline. |

On the 30-task seed pilot, success rate is already saturated, but intervention
reduces several waste signals:

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 10.43 | 7.00 | -3.43 |
| unresolved_error_rate | 0.00 | 0.00 | 0.00 |
| avg_command_failures | 0.50 | 0.20 | -0.30 |
| avg_recover_events | 2.07 | 0.40 | -1.67 |
| avg_token_usage | 218.7k | 184.8k | -34.0k |
| avg_failure_score | 4.17 | 1.00 | -3.17 |

On the early hard10 pilot, intervention improves both outcome and waste
metrics:

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.70 | 0.80 | +0.10 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| unresolved_error_rate | 0.00 | 0.00 | 0.00 |
| avg_repeated_tool_calls | 9.20 | 6.20 | -3.00 |
| avg_token_usage | 248.9k | 187.5k | -61.4k |
| avg_verify_events | 7.30 | 3.70 | -3.60 |

On the hard30 tier, success stays flat but waste drops sharply:

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.50 | 0.50 | 0.00 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| unresolved_error_rate | 0.00 | 0.00 | 0.00 |
| avg_repeated_tool_calls | 12.93 | 9.20 | -3.73 |
| avg_command_failures | 0.30 | 0.10 | -0.20 |
| avg_token_usage | 355.0k | 256.3k | -98.7k |
| avg_failure_score | 3.50 | 1.17 | -2.33 |

Paired hard30 deltas show that token usage improves in 26 of 30 tasks,
repeated tool calls improve in 26 of 30 tasks, and success improves in one task
while regressing in one task.
The generated task-level diagnosis in `docs/hard30_task_diagnosis.md` shows
that 14 tasks fail under both prompts, `HARD-050` is the single hard30 repair,
`HARD-007` is the single outcome regression, and the largest waste reduction is
`HARD-033`, where repeated tool calls drop by 15 and token usage drops by
699.2k tokens.

Four auxiliary pilots further test whether the original thesis should claim
verification-rate lift. In the process-stress tier, success remains
flat at 0.92 -> 0.92, while repeated tool calls improve from 8.08 to 7.17 and
token usage improves from 209.0k to 185.1k. In the targeted verification-lift
tier, even a weak baseline prompt that permits skipped command execution still
verifies every run: broad verification and exact visible-success-check
verification both remain 1.00 -> 1.00, success remains 0.88 -> 0.88, repeated
tool calls improve from 6.13 to 5.38, and token usage improves from 176.8k to
172.2k. The verification-lift-v2 rerun also verifies every run: broad
verification and exact visible-success-check verification both remain 1.00 ->
1.00, success remains 0.88 -> 0.88, repeated tool calls improve from 8.62 to
5.50, and token usage improves from 224.6k to 185.5k. Finally, a no-verify
ablation intentionally forbids the baseline from running tests while requiring
the intervention to produce evidence. In that
artificial setting, broad verification and exact visible-success-check
verification both rise from 0.00 to 1.00 and failure score drops from 61.25 to
0.00, while success stays flat at 0.75 -> 0.75 and token usage increases from
145.8k to 172.1k. This supports a
narrow mechanism claim that harness constraints can control verification
behavior, but it is not ordinary-baseline evidence. Overall, the ordinary and
weak-baseline pilots are a negative result for the verification-rate-lift claim
and a positive result for the narrower waste-reduction claim.

### RQ4: Trace Signals By Outcome

On the hard30 tier, the process signals do not strongly separate successful
runs from hidden semantic failures. Failure and success runs both have
verification rate 1.0, exact visible-success-check verification rate 1.0, and
unresolved error 0. Repeated tool calls and token usage are also close across
outcomes, and failure score is higher for successful runs than failed runs.
This supports the RQ2 boundary result: when visible tests are incomplete, a run
can look procedurally sound while still failing a hidden oracle.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1.00 | 1.00 | 0.00 |
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 10.8 | 11.33 | 0.53 |
| command_failure_count | 0.23 | 0.17 | -0.07 |
| token_usage | 306.5k | 304.8k | -1.8k |
| failure_score | 1.83 | 2.83 | 1.00 |

For observable process positives, the signal story is different. In hard30
`repetitive_exploration` runs, token usage is 666.8k versus a 306.5k baseline,
failure score is 28.75 versus 1.83, and repeated tool calls are 24.25 versus
10.8. In the full30 `sandbox_permission_deadlock` example, phase-recover events
are 32 versus 1.23, command failures are 5 versus 0.35, and token usage is
529.2k versus 201.8k. The strongest current evidence for intervention is
therefore not failure-score separation on hidden semantic failures; it is
outcome improvement and reduced process waste under the intervention prompt.
The generated full signal tables are kept in `docs/results_summary.md` and
`docs/rq4_signal_audit.md`.

## 8. Analysis

The stored pilots show complementary behavior. The 30-task seed tier validates
the collection harness and shows that process-level interventions can reduce
waste even when outcomes are saturated. The hard10 pilot creates genuine
outcome failures and shows a small success-rate lift. The larger hard30 pilot
keeps success flat but sharply reduces tool-call and token waste, while also
revealing that process-only trace rules cannot detect every correctness
failure. The process-stress, verification-lift, and verification-lift-v2
pilots add a useful boundary: current Codex CLI behavior already verifies
consistently, so the paper should not claim a verification-rate lift under
ordinary or weak-baseline conditions; that remains true when verification is
restricted to the task's exact visible success check. The no-verify ablation
shows that an evidence-gated harness can force verification when the baseline
is explicitly forbidden to verify, but that result belongs in the analysis as
a mechanism check rather than a main outcome claim.

This distinction matters for a practical coding-agent harness. Trace diagnosis
is useful for asking questions such as:

- Did the agent verify after editing?
- Did a failed command get repaired or ignored?
- Did the agent repeat repository exploration?
- Did sandbox friction block progress?
- Did the intervention reduce waste?

Trace diagnosis is less suited for proving semantic correctness when the agent
ran the visible tests cleanly but missed hidden edge cases.

## 9. Threats To Validity

This study currently uses one agent interface, Codex CLI, and a pilot-scale
benchmark. The hard30 artifact has 30 selected tasks and 60 real runs, but the
70% to 80% hard10 success-rate lift should still be read as pilot evidence
rather than a stable population estimate. The detectors are rule-based and
intentionally interpretable, but incomplete. Manual labels for hidden semantic
failures are based on hidden grader outcomes and qualitative inspection of
failure messages. Larger repository tasks, repeated trials, richer process
failure labels, and lightweight semantic checks are needed before making
broader claims.

## 10. Artifact Availability

The repository contains the analyzer, fixture generators, stored Codex JSONL
manifests, generated reports, manual labels, and reproduction commands needed
to inspect the pilot artifact without rerunning Codex. The main entry points
are `docs/artifact_guide.md` for a short reviewer path,
`docs/results_summary.md` for generated RQ tables,
`docs/submission_package.md` for safe RQ-to-evidence claim framing,
`docs/metric_coverage_audit.md` for experiment-metric coverage,
`docs/paper_claim_audit.md`, `docs/claim_text_guard.md`, and
`docs/paper_number_guard.md` for claim-support and numeric-drift guards, and
`docs/reproducibility_checklist.md` for claim-to-evidence mapping and
commands.

## 11. Conclusion

CodexTrace shows that coding-agent traces can be used as first-class evaluation
objects, not merely logs. In real Codex runs, trace analysis exposes process
failures and quantifies harness-level waste reductions. The current hard-tier
pilot also gives an important limitation: hidden semantic edge failures can
escape process-only rules. A practical evaluation stack should therefore combine
trace-based diagnosis with strong task-level oracles.

The next step is to repeat the hard30 collection, add richer labels for
observable process failures, and evaluate whether additional trace signals or
lightweight semantic checks can recover hidden edge-case failures.

For a reviewer-facing walkthrough, see `docs/artifact_guide.md`. For the
generated result summary, see `docs/results_summary.md`. For claim-evidence
mapping and reproduction commands, see `docs/reproducibility_checklist.md`.
For safe claim framing and generated guard status, see
`docs/submission_package.md`, `docs/claim_text_guard.md`, and
`docs/paper_number_guard.md`.
