# When Coding Agents Get Lost

Trace-Based Diagnosis of Multi-Turn Tool-Use Failures

## Abstract Draft

Coding agents increasingly solve realistic software tasks through multi-turn
tool use, but their failures are often diagnosed only by final task outcome. We
argue that many failures arise inside the agent harness: missing verification,
unrecovered tool errors, repetitive exploration, context drift, premature
completion, and sandbox deadlocks. We introduce CodexTrace, an offline parser
and diagnosis engine for `codex exec --json` traces. CodexTrace normalizes agent
events, detects process-level failure patterns, and compares baseline prompts
against simple harness interventions. Across a 30-task seed pilot, a 10-task
hard pilot, a 30-task hard-tier artifact with hidden graders, and auxiliary
process-stress / verification-lift / verification-lift-v2 / no-verify
ablation pilots, intervention primarily reduces token and tool-call waste; it
improves success in the hard10 pilot but not in the larger hard30 pilot. The
ordinary and weak-baseline verification-lift pilots remain saturated at
1.00 -> 1.00, so they are negative evidence for a verification-rate-lift
claim. The no-verify ablation shows harness constraints can force verification
only under an artificial baseline condition, not under the ordinary Codex
baseline. The hard30 labels also expose a boundary result: trace-only process
rules detect reviewed repetitive exploration positives but miss hidden semantic
edge-case failures whose visible process traces look clean. A task-level
hard30 diagnosis identifies 14 double-failure tasks, one intervention repair
(`HARD-050`), one intervention regression (`HARD-007`), and the largest
token-waste reduction (`HARD-033`).

## 1. Introduction

- Coding agents are no longer single-shot code generators.
- They inspect files, call tools, edit code, run commands, and summarize results.
- Final success/failure hides the process by which the agent got lost.
- Thesis: harness-level trace diagnosis exposes failures that are invisible from
  final answers alone and can guide simple interventions.

## 2. Related Work

Topics to cover:

- coding-agent benchmarks such as SWE-bench-style evaluation
- coding agents and tool-use systems such as SWE-agent, OpenHands, and Codex CLI
- tool-use and agent evaluation
- multi-turn degradation and context management
- trace/debugging tools for agents

## 3. Problem Definition

Define a coding-agent run as:

```text
Run = task prompt + multi-turn tool-use trace + final answer + outcome
```

Define process-level failure:

```text
A detectable trace pattern that makes success less likely or increases waste,
even before final outcome is known.
```

## 4. Benchmark

- 30-task seed tier with 60 real baseline/intervention runs
- 50-task hard tier with hidden graders; current paper-facing hard30 selection
  has 30 tasks and 60 real runs
- categories include bug fix, feature, test writing, refactor, CI failure,
  error localization, and multi-turn change
- traces collected with `codex exec --json`
- outcomes labeled from external success checks; hard-tier hidden graders are
  copied only after Codex exits

## 5. Method: CodexTrace

Pipeline:

```text
codex exec --json
        ↓
JSONL event parser
        ↓
normalized trace schema
        ↓
phase segmentation
        ↓
failure pattern detector
        ↓
diagnosis report
        ↓
baseline vs intervention comparison
```

Core modules:

- parser: maps JSONL events to a stable schema
- phase segmenter: assigns setup/inspect/edit/verify/recover/complete labels
- detector: emits interpretable failure tags
- aggregator: computes benchmark-level metrics
- report: generates JSON/Markdown tables

## 6. Experiments

### E1: Failure Taxonomy Distribution

Question:

- Which failures appear most often in baseline runs?
- Which labeled hard-tier failures are observable process failures versus
  hidden semantic edge cases?

Table:

```text
failure_tag | count | percentage | example_task
```

### E2: Detector Agreement

Question:

- How well do rule-based trace detectors match manual labels?

Metrics:

- precision
- recall
- F1 by tag

### E3: Baseline vs Intervention

Question:

- Does a simple harness prompt improve process quality and outcomes?

Metrics:

- success rate
- verification rate
- unresolved error rate
- repeated tool-call count
- token usage
- failure score
- paired task repair/regression
- task-level waste delta

### E4: Explanatory Trace Signals

Question:

- Which trace signals explain observable process failures, and where do they
  fail to explain hidden semantic failures?

Candidate signals:

- no post-edit verification
- failed command count
- repeated search/read count
- retry count
- recover-phase event count
- verify-phase event count
- input token usage
- time to first test
- time to first edit

## 7. Analysis

- verification is saturated in the stored hard pilots, so the paper should not
  claim a verification-rate lift; the targeted verification-lift pilot also
  stays saturated at 1.00 -> 1.00 for both broad verification and exact visible
  success-check verification
- the ordinary-baseline verification-lift-v2 retest also remains saturated at
  1.00 -> 1.00, while repeated tool calls improve 8.62 -> 5.50 and token usage
  improves 224.6k -> 185.5k
- the no-verify verification-ablation pilot is a mechanism check only:
  broad and exact success-check verification rise 0.00 -> 1.00 and failure
  score drops 61.25 -> 0.00, but it is not ordinary-baseline evidence
- intervention most consistently reduces process waste: repeated tool calls,
  command failures, recovery events, token usage, and failure score
- success improves in the early hard10 pilot but is flat on hard30
- task-level hard30 diagnosis shows 14 double failures, one repair
  (`HARD-050`), one regression (`HARD-007`), and token/repeated-call
  improvements in 26 of 30 tasks
- hidden semantic edge-case failures can pass visible verification and remain
  invisible to deterministic process rules
- controlled detector fixtures cover the six process labels, while real pilots
  show only partial natural coverage and threshold false positives
- trace diagnosis should be paired with strong task-level oracles rather than
  used as a replacement for correctness evaluation

## 8. Limitations

- Codex CLI only
- small task set
- rule-based detectors
- possible prompt/order effects
- no large-scale SWE-bench comparison yet

## 9. Conclusion

The key claim is not that CodexTrace solves coding-agent evaluation. The claim
is narrower and testable: many coding-agent failures leave observable trace
signatures, and simple harness interventions can reduce some of those failures.
