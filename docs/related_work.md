# Related Work Notes

This note tracks the papers and systems that position CodexTrace. It is meant
to be a compact bibliography for `docs/paper_draft.md`, not a full survey.

## Software-Engineering Benchmarks

SWE-bench asks language models to resolve real GitHub issues by editing
repository code and passing tests. It established real-world software
engineering as a benchmark setting, with 2,294 tasks from 12 Python
repositories. CodexTrace differs by treating the execution trace as the object
of analysis: final task success remains important, but the paper asks what can
be learned from the process that led to the outcome.

Source: [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)

## Coding Agents and Agent-Computer Interfaces

SWE-agent shows that the interface between a language model and a computer can
materially affect automated software-engineering performance. Its agent-computer
interface helps an agent browse repositories, edit files, and run tests.
CodexTrace is complementary: it does not propose a new coding interface, but it
measures whether a given harness produces verification gaps, repeated
exploration, unrecovered errors, or reduced waste under an intervention prompt.

Source: [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793)

OpenHands provides an open platform for software-development agents that can
write code, use a command line, and browse the web. This broadens the setting
from isolated code generation to developer-like tool use. CodexTrace focuses on
one concrete trace format and a smaller diagnosis question: given a run, what
process failures can be identified offline?

Source: [OpenHands: An Open Platform for AI Software Developers as Generalist Agents](https://arxiv.org/abs/2407.16741)

OpenAI Codex CLI is an open-source terminal coding agent that can read, modify,
and run code locally. CodexTrace uses the CLI's non-interactive JSONL event
stream as its first trace source.

Sources:

- [OpenAI Codex CLI - Getting Started](https://help.openai.com/en/articles/11096431)
- [openai/codex GitHub repository](https://github.com/openai/codex)

## General Agent Evaluation

AgentBench evaluates LLM agents across interactive environments and emphasizes
reasoning, decision-making, and instruction-following in multi-turn settings.
CodexTrace shares the focus on multi-turn behavior, but narrows the domain to
software-engineering traces and studies process-level failure signatures rather
than only task scores.

Source: [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688)

RepairAgent studies autonomous LLM-based program repair and reports that repair
runs can consume large token budgets. This motivates CodexTrace's emphasis on
tool-call and token waste as first-class evaluation metrics alongside success.

Source: [RepairAgent: An Autonomous, LLM-Based Agent for Program Repair](https://arxiv.org/abs/2403.17134)

## Trace-Based Agent Diagnosis

AgentRx is close in spirit: it diagnoses failed AI-agent executions from
trajectories and localizes critical failure steps. CodexTrace is narrower and
more structural: it focuses on coding-agent JSONL traces, uses deterministic
process rules, and reports benchmark-level baseline-vs-intervention metrics.

Source: [AgentRx: Diagnosing AI Agent Failures from Execution Trajectories](https://www.microsoft.com/en-us/research/publication/agentrx-diagnosing-ai-agent-failures-from-execution-trajectories/)

## Positioning Summary

CodexTrace sits between software-engineering benchmarks and agent observability:

- Unlike SWE-bench-style benchmarks, it does not only ask whether the final
  patch passes tests; it asks what happened during the tool-use process.
- Unlike coding-agent frameworks, it does not build a new agent interface; it
  analyzes traces emitted by an existing CLI agent.
- Unlike broad agent-evaluation benchmarks, it focuses on coding-specific
  process failures such as verification gaps, command recovery, repeated
  repository exploration, and sandbox friction.
- Unlike LLM-as-judge trajectory diagnosis, its first version uses deterministic
  rules to keep findings auditable and cheap to run.
