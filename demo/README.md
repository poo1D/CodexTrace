# CodexTrace Demo

This demo shows CodexTrace as a practical failure-debugging tool for Codex
agent runs.

## Demo Story

A Codex run claims the task is complete, but the trace reveals four problems:

- a failed test command was not repaired
- files were edited without a post-edit verification command
- the agent repeated the same repository search
- a sandbox/network permission error was left unresolved

CodexTrace parses the JSONL trace, turns it into a normalized event timeline,
and produces a report that explains what failed and how to improve the next
agent run.

## Run

```bash
./scripts/demo.sh
```

By default, this writes reports to `/tmp/codextrace-demo` so the repository
stays clean after a reviewer runs the demo.

Then open the Web UI:

```bash
./scripts/demo.sh --update-ui
cd web
npm install
npm run dev
```

Open the printed Vite URL, usually `http://localhost:5173`. The UI reads
`web/public/report.json`, which `--update-ui` refreshes explicitly.

## Try the Real Codex Fixture

```bash
./scripts/demo.sh demo/real-codex-run.jsonl
./scripts/demo.sh demo/real-codex-run.jsonl --update-ui
```

The real fixture is a healthy read-only Codex run captured from this repository.
It is useful for showing that CodexTrace can parse actual `codex exec --json`
events, not only synthetic examples.

## Interview Talk Track

1. The problem is not model training; it is harness observability.
2. `codex exec --json` already emits machine-readable agent events.
3. CodexTrace normalizes those events into a stable trace schema.
4. Diagnosis rules catch concrete failure modes that make coding agents hard to
   trust in real engineering workflows.
5. The Web UI turns a long transcript into a debuggable timeline.
