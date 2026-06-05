from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .schema import EventPhase, Trace, TraceEvent


VERIFY_KEYWORDS = (
    "pytest",
    "npm test",
    "npm run test",
    "pnpm test",
    "yarn test",
    "cargo test",
    "go test",
    "mvn test",
    "gradle test",
    "ruff",
    "mypy",
    "tsc",
    "npm run build",
    "pnpm build",
)
SEARCH_PREFIXES = ("rg ", "grep ", "find ", "ls", "sed ", "cat ", "git grep")
COMPLETION_WORDS = ("complete", "completed", "done", "fixed", "implemented", "updated")


def parse_jsonl(path: str | Path) -> Trace:
    source = Path(path)
    return parse_lines(source.read_text(encoding="utf-8").splitlines(), source=str(source))


def parse_lines(lines: Iterable[str], source: str | None = None) -> Trace:
    trace = Trace(source=source)
    counter = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if payload.get("type") == "thread.started":
            trace.thread_id = payload.get("thread_id")
        if payload.get("type") == "turn.completed" and isinstance(payload.get("usage"), dict):
            trace.usage = payload["usage"]

        event = _event_from_payload(payload, counter)
        if event:
            trace.events.append(event)
            counter += 1
    assign_phases(trace.events)
    return trace


def assign_phases(events: list[TraceEvent]) -> None:
    after_failure = False
    current: EventPhase = "setup"
    for event in events:
        phase = _infer_event_phase(event, current, after_failure)
        event.phase = phase

        if event.kind == "command" and event.exit_code not in (None, 0):
            after_failure = True
        elif phase in {"verify", "complete"} and event.status != "failed":
            after_failure = False
        elif event.kind == "file_change":
            after_failure = False

        if phase not in {"setup", "other"}:
            current = phase


def _infer_event_phase(event: TraceEvent, current: EventPhase, after_failure: bool) -> EventPhase:
    if event.kind == "thread":
        return "setup"
    if event.kind == "turn":
        return "complete" if event.status == "completed" else "setup"
    if event.kind == "file_change":
        return "edit"
    if event.kind == "web_search":
        return "inspect"
    if event.kind == "plan":
        return current
    if event.kind == "agent_message":
        text = f"{event.title}\n{event.detail}".lower()
        if any(word in text for word in COMPLETION_WORDS):
            return "complete"
        return "recover" if after_failure else current
    if event.kind == "reasoning":
        return "recover" if after_failure else current
    if event.kind == "mcp_tool":
        return "recover" if event.status in {"failed", "blocked", "error"} or after_failure else current
    if event.kind == "command":
        command = event.command or ""
        if is_verification_command(command):
            return "verify"
        if event.exit_code not in (None, 0) or after_failure:
            return "recover"
        if is_search_command(command):
            return "inspect"
        return current if current != "setup" else "inspect"
    if event.kind == "error":
        return "recover"
    return current if current != "setup" else "other"


def _event_from_payload(payload: dict[str, Any], counter: int) -> TraceEvent | None:
    raw_type = str(payload.get("type", "unknown"))
    event_id = f"e{counter:04d}"

    if raw_type.startswith("thread."):
        return TraceEvent(event_id, "thread", _status(payload), raw_type, raw_type=raw_type, metadata=payload)

    if raw_type.startswith("turn."):
        usage = payload.get("usage") or {}
        detail = _usage_detail(usage) if usage else ""
        return TraceEvent(event_id, "turn", _status(payload), raw_type, detail=detail, raw_type=raw_type, metadata=payload)

    if raw_type == "error":
        return TraceEvent(event_id, "error", "failed", "runtime error", detail=str(payload.get("message", "")), raw_type=raw_type, metadata=payload)

    item = payload.get("item")
    if isinstance(item, dict):
        return _event_from_item(item, event_id, raw_type, payload)

    return TraceEvent(event_id, "unknown", _status(payload), raw_type, raw_type=raw_type, metadata=payload)


def _event_from_item(item: dict[str, Any], event_id: str, raw_type: str, payload: dict[str, Any]) -> TraceEvent:
    item_type = str(item.get("type", "unknown"))
    status = str(item.get("status") or payload.get("status") or "completed")

    if item_type == "agent_message":
        text = str(item.get("text", ""))
        return TraceEvent(event_id, "agent_message", status, _shorten(text, 90) or "agent message", detail=text, raw_type=raw_type, metadata=payload)

    if item_type == "reasoning":
        text = str(item.get("text") or item.get("summary") or "")
        return TraceEvent(event_id, "reasoning", status, _shorten(text, 90) or "reasoning", detail=text, raw_type=raw_type, metadata=payload)

    if item_type in {"command_execution", "command"}:
        command = str(item.get("command") or item.get("cmd") or "")
        exit_code = _extract_exit_code(item)
        detail = str(item.get("output") or item.get("aggregated_output") or item.get("stderr") or item.get("stdout") or "")
        event_status = "failed" if exit_code not in (None, 0) else status
        return TraceEvent(event_id, "command", event_status, command or "command", detail=detail, raw_type=raw_type, command=command, exit_code=exit_code, metadata=payload)

    if item_type in {"file_change", "file_changes", "patch"}:
        files = _extract_files(item)
        return TraceEvent(event_id, "file_change", status, "file change", detail=", ".join(files), raw_type=raw_type, files=files, metadata=payload)

    if item_type in {"mcp_tool_call", "tool_call", "function_call"}:
        name = str(item.get("name") or item.get("tool_name") or "tool call")
        detail = json_dumps_compact(item.get("arguments") or item.get("input") or {})
        return TraceEvent(event_id, "mcp_tool", status, name, detail=detail, raw_type=raw_type, metadata=payload)

    if item_type == "web_search":
        query = str(item.get("query") or item.get("text") or "")
        return TraceEvent(event_id, "web_search", status, _shorten(query, 90) or "web search", detail=query, raw_type=raw_type, metadata=payload)

    if item_type == "plan_update":
        return TraceEvent(event_id, "plan", status, "plan update", detail=json_dumps_compact(item), raw_type=raw_type, metadata=payload)

    return TraceEvent(event_id, "unknown", status, item_type, detail=json_dumps_compact(item), raw_type=raw_type, metadata=payload)


def _status(payload: dict[str, Any]) -> str:
    raw_type = str(payload.get("type", ""))
    if raw_type.endswith(".failed"):
        return "failed"
    if raw_type.endswith(".started"):
        return "in_progress"
    return str(payload.get("status") or "completed")


def is_verification_command(command: str) -> bool:
    lowered = command.lower()
    return any(keyword in lowered for keyword in VERIFY_KEYWORDS)


def is_search_command(command: str) -> bool:
    stripped = command.strip().lower()
    return any(stripped.startswith(prefix) for prefix in SEARCH_PREFIXES)


def _extract_exit_code(item: dict[str, Any]) -> int | None:
    for key in ("exit_code", "exitCode", "returncode", "return_code"):
        value = item.get(key)
        if isinstance(value, int):
            return value
    result = item.get("result")
    if isinstance(result, dict):
        return _extract_exit_code(result)
    return None


def _extract_files(item: dict[str, Any]) -> list[str]:
    files = item.get("files")
    if isinstance(files, list):
        return [str(file) for file in files]
    path = item.get("path") or item.get("file")
    if path:
        return [str(path)]
    changes = item.get("changes")
    if isinstance(changes, list):
        found = []
        for change in changes:
            if isinstance(change, dict) and (change.get("path") or change.get("file")):
                found.append(str(change.get("path") or change.get("file")))
        return found
    return []


def _usage_detail(usage: dict[str, Any]) -> str:
    parts = []
    for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
        if key in usage:
            parts.append(f"{key}={usage[key]}")
    return ", ".join(parts)


def _shorten(text: str, limit: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "..."


def json_dumps_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
