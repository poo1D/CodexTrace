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
tool on two real Codex benchmark pilots: a 30-task seed benchmark with 60 runs,
and a 10-task hard tier with 20 runs and hidden edge-case graders. On the
30-task pilot, all runs succeed, but the intervention reduces repeated tool
calls from 10.43 to 7.00 and average token usage from 218.7k to 184.8k. On the
hard tier, intervention improves success rate from 70% to 80%, reduces repeated
tool calls from 9.2 to 6.2, and reduces average token usage from 248.9k to
187.5k. A manual-label analysis also shows a boundary of trace-only diagnosis:
five hidden semantic edge-case failures receive failure score 0 because their
visible process traces look clean. These results suggest that trace-based
diagnosis is useful for exposing observable process failures and measuring
harness interventions, but it should be paired with strong semantic oracles for
hidden correctness failures.

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
- RQ4: Which trace signals best explain whether a run will fail?

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

The normalized trace schema records event type, status, content, command,
paths, token usage, inferred phase, and failure tags. The phase segmenter maps
events into setup, inspect, edit, verify, recover, complete, and other. The
detector emits rule-based findings with evidence snippets and recommendations.

The research runner materializes fixture repositories in isolated run
directories, executes `codex exec --json`, and then runs an external success
check. For hard-tier tasks, the prompt exposes only a public success check such
as `python3 -m unittest discover -s tests` or `npm test`; the hidden grader is
copied into the run directory only after the Codex process exits.

## 6. Benchmark

The current benchmark has two tiers.

The seed tier contains 30 runnable coding tasks covering bug fixes, features,
test writing, refactors, CI failures, error localization, and multi-turn
changes. Each task is run with two prompt conditions:

- `baseline`: a normal task prompt with a visible success check.
- `intervention`: a harness-constrained prompt requiring inspection, minimal
  edits, post-edit verification, failed-command diagnosis, and evidence before
  completion.

The hard tier contains 47 runnable harder tasks with hidden graders; the
evaluated hard10 pilot uses the first 10. These tasks are designed to create
outcome failures even when visible tests pass.

## 7. Results

### RQ1: Failure Taxonomy Distribution

On the 30-task seed pilot, all 60 runs pass their external graders. CodexTrace
still detects one process failure: `CT-021/baseline` hits a sandbox or
permission deadlock pattern and receives a failure score of 35.

On the hard tier, manual labels mark all five outcome failures as
`hidden_semantic_edge_case`.

| Pilot | Labeled failure tag | Count | Example |
| --- | --- | ---: | --- |
| full30 | `sandbox_permission_deadlock` | 1 | `CT-021/baseline` |
| hard10 | `hidden_semantic_edge_case` | 5 | `HARD-001/baseline` |

### RQ2: Detector Agreement

The current process-only detector does not detect hidden semantic edge cases.
For the hard-tier manual labels, detector agreement is:

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `hidden_semantic_edge_case` | 0 | 0 | 5 | 0 | 0 | 0 |

This is a boundary result rather than a contradiction of trace diagnosis. The
detectors target process evidence; hidden semantic failures may require visible
edge tests, stronger task oracles, or a semantic analysis layer.

### RQ3: Baseline vs Intervention

On the 30-task seed pilot, success rate is already saturated, but intervention
reduces several waste signals:

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 10.43 | 7.00 | -3.43 |
| avg_command_failures | 0.50 | 0.20 | -0.30 |
| avg_recover_events | 2.07 | 0.40 | -1.67 |
| avg_token_usage | 218.7k | 184.8k | -34.0k |
| avg_failure_score | 2.83 | 1.00 | -1.83 |

On the hard tier, intervention improves both outcome and waste metrics:

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.70 | 0.80 | +0.10 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 9.20 | 6.20 | -3.00 |
| avg_token_usage | 248.9k | 187.5k | -61.5k |
| avg_verify_events | 7.30 | 3.70 | -3.60 |

### RQ4: Trace Signals By Outcome

On the hard tier, the process signals do not strongly separate successful runs
from hidden semantic failures. Failure and success runs both have verification
rate 1.0, unresolved error 0, command failure count 0, and failure score 0.
This supports the RQ2 boundary result: when visible tests are incomplete, a run
can look procedurally sound while still failing a hidden oracle.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1.00 | 1.00 | 0.00 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 8.00 | 7.60 | -0.40 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 225.6k | 215.7k | -9.9k |
| failure_score | 0 | 0 | 0 |

The strongest current evidence for intervention is therefore not failure-score
separation on hard semantic failures; it is outcome improvement and reduced
process waste under the intervention prompt. The generated full signal table is
kept in `docs/results_summary.md`.

## 8. Analysis

The two pilots show complementary behavior. The 30-task seed tier validates the
collection harness and shows that process-level interventions can reduce waste
even when outcomes are saturated. The hard tier creates genuine outcome
failures and shows a small success-rate lift, but also reveals that process-only
trace rules cannot detect every correctness failure.

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

This study currently uses one agent interface, Codex CLI, and a small benchmark.
The hard tier has only 10 tasks, so the 70% to 80% success-rate lift should be
read as pilot evidence rather than a stable population estimate. The detectors
are rule-based and intentionally interpretable, but incomplete. Manual labels
for hidden semantic failures are based on hidden grader outcomes and qualitative
inspection of failure messages. Larger repository tasks and repeated trials are
needed before making broader claims.

## 10. Conclusion

CodexTrace shows that coding-agent traces can be used as first-class evaluation
objects, not merely logs. In real Codex runs, trace analysis exposes process
failures and quantifies harness-level waste reductions. The current hard-tier
pilot also gives an important limitation: hidden semantic edge failures can
escape process-only rules. A practical evaluation stack should therefore combine
trace-based diagnosis with strong task-level oracles.

The next step is to expand the hard tier from 10 tasks toward 30-50 tasks,
include more observable process failures, and evaluate whether additional trace
signals or lightweight semantic checks can recover hidden edge-case failures.

For a reviewer-facing walkthrough, see `docs/artifact_guide.md`. For the
generated result summary, see `docs/results_summary.md`. For claim-evidence
mapping and reproduction commands, see `docs/reproducibility_checklist.md`.
