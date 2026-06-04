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
against simple harness interventions. In a small coding-task benchmark, we
measure whether trace-based rules can identify failure modes and whether
interventions improve verification behavior, reduce unresolved errors, and
lower token/tool-call waste.

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

- 30-50 small tasks
- categories: bug fix, feature, test writing, refactor, CI failure, error
  localization, multi-turn change
- two prompt conditions: baseline and intervention
- traces collected with `codex exec --json`
- outcomes labeled from success-check commands and manual inspection

## 5. Method: CodexTrace

Pipeline:

```text
codex exec --json
        ↓
JSONL event parser
        ↓
normalized trace schema
        ↓
failure pattern detector
        ↓
diagnosis report
        ↓
baseline vs intervention comparison
```

Core modules:

- parser: maps JSONL events to a stable schema
- detector: emits interpretable failure tags
- aggregator: computes benchmark-level metrics
- report: generates JSON/Markdown tables

## 6. Experiments

### E1: Failure Taxonomy Distribution

Question:

- Which failures appear most often in baseline runs?

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

### E4: Explanatory Trace Signals

Question:

- Which trace signals best explain failure?

Candidate signals:

- no post-edit verification
- failed command count
- repeated search/read count
- input token usage
- time to first test
- time to first edit

## 7. Analysis

- verification gap is expected to be a high-impact failure mode
- intervention should most strongly improve verification rate
- success-rate gains may be smaller than process-quality gains
- some sandbox failures require system-level changes, not prompt changes

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
