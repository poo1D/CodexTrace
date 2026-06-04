# CodexTrace

CodexTrace is a flight recorder and failure debugger for `codex exec --json` runs.
It turns Codex JSONL event streams into a normalized trace, detects agent failure
patterns, and produces a report plus a replay UI.

The practical problem is simple: after a coding agent fails, the transcript is
long and noisy. CodexTrace answers:

- Where did the run fail?
- Did Codex edit files without verifying them?
- Which commands or tool calls were repeated?
- Was the failure caused by sandbox/permission friction?
- Did the harness burn a large context window without useful progress?

## Why This Exists

This project is designed for Agent Harness work rather than model training. It
does not need a GPU and does not depend on Codex Web or private IDE-extension
interfaces. The first version focuses on the open Codex CLI/SDK surface and the
machine-readable events emitted by:

```bash
codex exec --json "your coding task" > traces/run.jsonl
```

## Features

- Normalize `codex exec --json` JSONL into a stable trace schema.
- Detect five concrete failure or inefficiency modes:
  - command failure not clearly handled
  - file edits without post-edit verification
  - repeated search/read commands
  - sandbox or permission blocks
  - long context with weak progress
- Generate Markdown and JSON diagnosis reports.
- Replay a trace in a TypeScript Web UI with highlighted failure nodes.
- Run offline with demo traces; optional LLM judging can be added later.
- Includes `demo/real-codex-run.jsonl`, a real `codex exec --json` fixture captured from this repository.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

codex-trace diagnose demo/failing-codex-trace.jsonl
codex-trace diagnose demo/failing-codex-trace.jsonl --format json -o demo/report.json
pytest
```

To run the Web UI:

```bash
cd web
npm install
npm run dev
```

## Capturing a Real Codex Trace

From any Git repository:

```bash
codex exec --json "inspect this repo and identify one risky area" > run.jsonl
codex-trace diagnose run.jsonl -o report.md
codex-trace diagnose run.jsonl --format json -o report.json
```

## CLI

```bash
codex-trace collect TRACE.jsonl -o trace.json
codex-trace diagnose TRACE.jsonl --format markdown -o report.md
codex-trace diagnose TRACE.jsonl --format json -o report.json
```

## Trace Schema

CodexTrace maps raw Codex events into:

- `thread`
- `turn`
- `agent_message`
- `reasoning`
- `command`
- `file_change`
- `mcp_tool`
- `web_search`
- `plan`
- `error`
- `unknown`

This keeps the first version Codex-first while leaving room for future adapters
for Claude Code, SWE-agent, OpenHands, or custom MCP agents.

## Example Diagnosis

```text
Failed trace: Command failures were not clearly handled.
10 events, 4 commands, 2 failed commands.

Findings:
- Command failures were not clearly handled
- Files changed without a verification command
- Repeated search/read commands suggest inefficient exploration
- Sandbox or permission friction blocked progress
```

## CV Bullets

- Built `CodexTrace`, an Agent Harness debugging tool that parses `codex exec --json` event streams into normalized traces and detects failure modes such as unhandled command errors, missing post-edit validation, repeated tool use, and sandbox blocks.
- Developed a TypeScript trace replay dashboard and Python CLI that generate Markdown/JSON diagnosis reports, highlighting failed tool calls, token usage, file edits, and run-level inefficiencies for coding-agent workflows.
- Packaged the project as a reproducible open-source repo with demo traces, pytest coverage, Docker support, and GitHub Actions CI, aligning with Agent evaluation, Tool Use, and developer-experience infrastructure.

## Non-goals

- No model training.
- No GPU dependency.
- No private Codex Web or IDE-extension interfaces.
- No attempt to clone Codex.
- No multi-agent platform in v1.

## Roadmap

- Load generated report JSON directly in the Web UI.
- Add Codex SDK capture helpers.
- Add optional LLM-as-judge scoring.
- Add run-to-run diff for prompt and harness interventions.
- Extend adapters to other coding-agent traces.
