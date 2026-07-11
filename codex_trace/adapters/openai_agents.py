from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from ..parser import assign_phases
from ..schema import Trace, TraceEvent


COMMAND_TOOL_NAMES = frozenset(
    {
        "bash",
        "command",
        "exec",
        "exec_command",
        "execute_command",
        "run_command",
        "shell",
        "terminal",
    }
)
FILE_TOOL_NAMES = frozenset(
    {
        "apply_patch",
        "create_file",
        "delete_file",
        "edit_file",
        "file_change",
        "patch_file",
        "write_file",
    }
)
USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
    "requests",
)


@dataclass(frozen=True)
class _Record:
    payload: dict[str, Any]
    order: int

    @property
    def timestamp(self) -> str | None:
        value = self.payload.get("started_at")
        return value if isinstance(value, str) and value else None


class OpenAIAgentsAdapter:
    """Adapter for JSONL emitted from OpenAI Agents SDK trace/span exports."""

    name = "openai-agents"

    def parse_lines(
        self,
        lines: Iterable[str],
        *,
        source: str | None = None,
    ) -> Trace:
        trace = Trace(source=source)
        trace_record: dict[str, Any] | None = None
        span_records: list[_Record] = []
        unknown_records: list[_Record] = []
        trace_ids: set[str] = set()

        for order, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError("OpenAI Agents trace records must be JSON objects")

            object_type = payload.get("object")
            if object_type == "trace":
                if trace_record is not None:
                    raise ValueError("OpenAI Agents JSONL must contain at most one trace record")
                trace_record = payload
                trace_id = payload.get("id")
                if isinstance(trace_id, str) and trace_id:
                    trace_ids.add(trace_id)
                continue

            record = _Record(payload=payload, order=order)
            if object_type == "trace.span":
                span_records.append(record)
                trace_id = payload.get("trace_id")
                if isinstance(trace_id, str) and trace_id:
                    trace_ids.add(trace_id)
            else:
                unknown_records.append(record)

        if len(trace_ids) > 1:
            found = ", ".join(sorted(trace_ids))
            raise ValueError(f"OpenAI Agents JSONL mixes multiple trace ids: {found}")

        trace.thread_id = next(iter(trace_ids), None)
        counter = 0
        if trace_record is not None:
            trace.events.append(_thread_event(trace_record, counter))
            counter += 1

        ordered_spans = sorted(
            span_records,
            key=lambda record: (
                record.timestamp is None,
                record.timestamp or "",
                record.order,
            ),
        )
        for record in ordered_spans:
            event = _span_event(record.payload, counter)
            trace.events.append(event)
            counter += 1

        for record in unknown_records:
            trace.events.append(
                TraceEvent(
                    id=f"e{counter:04d}",
                    kind="unknown",
                    status="completed",
                    title=str(record.payload.get("object") or "unknown record"),
                    detail=_compact(record.payload),
                    raw_type=f"openai_agents.{record.payload.get('object') or 'unknown'}",
                    metadata=record.payload,
                )
            )
            counter += 1

        trace.usage = _select_usage(ordered_spans)
        assign_phases(trace.events)
        return trace


def _thread_event(payload: dict[str, Any], counter: int) -> TraceEvent:
    return TraceEvent(
        id=f"e{counter:04d}",
        kind="thread",
        status="completed",
        title=str(payload.get("workflow_name") or "OpenAI Agents trace"),
        raw_type="openai_agents.trace",
        metadata=payload,
    )


def _span_event(payload: dict[str, Any], counter: int) -> TraceEvent:
    span_data = payload.get("span_data")
    data = span_data if isinstance(span_data, dict) else {}
    span_type = str(data.get("type") or "unknown")
    raw_type = f"openai_agents.span.{span_type}"
    error = payload.get("error")
    status = "failed" if error else ("completed" if payload.get("ended_at") else "in_progress")
    timestamp = payload.get("started_at") if isinstance(payload.get("started_at"), str) else None
    event_id = f"e{counter:04d}"

    if error and span_type not in {"function", "custom"}:
        return TraceEvent(
            id=event_id,
            kind="error",
            status="failed",
            title=f"{span_type} span failed",
            detail=_compact(error),
            raw_type=raw_type,
            timestamp=timestamp,
            metadata=payload,
        )

    if span_type == "agent":
        name = str(data.get("name") or "agent")
        detail = _compact(
            {
                "handoffs": data.get("handoffs"),
                "tools": data.get("tools"),
                "output_type": data.get("output_type"),
            }
        )
        return TraceEvent(
            event_id,
            "agent_message",
            status,
            f"agent: {name}",
            detail=detail,
            raw_type=raw_type,
            timestamp=timestamp,
            metadata=payload,
        )

    if span_type in {"generation", "response"}:
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        label = data.get("model") or data.get("response_id") or span_type
        return TraceEvent(
            event_id,
            "usage",
            status,
            f"{span_type}: {label}",
            detail=_usage_detail(_normalize_usage(usage)),
            raw_type=raw_type,
            timestamp=timestamp,
            metadata=payload,
        )

    if span_type == "function":
        return _function_event(payload, data, event_id, raw_type, status, timestamp)

    if span_type == "custom":
        return _custom_event(payload, data, event_id, raw_type, status, timestamp)

    if span_type == "guardrail":
        triggered = bool(data.get("triggered"))
        kind = "error" if triggered else "mcp_tool"
        event_status = "failed" if triggered else status
        return TraceEvent(
            event_id,
            kind,
            event_status,
            f"guardrail: {data.get('name') or 'unnamed'}",
            detail=_compact(data),
            raw_type=raw_type,
            timestamp=timestamp,
            metadata=payload,
        )

    if span_type in {"handoff", "mcp_tools"}:
        return TraceEvent(
            event_id,
            "mcp_tool",
            status,
            span_type.replace("_", " "),
            detail=_compact(data),
            raw_type=raw_type,
            timestamp=timestamp,
            metadata=payload,
        )

    return TraceEvent(
        event_id,
        "unknown",
        status,
        span_type,
        detail=_compact(data),
        raw_type=raw_type,
        timestamp=timestamp,
        metadata=payload,
    )


def _function_event(
    payload: dict[str, Any],
    data: dict[str, Any],
    event_id: str,
    raw_type: str,
    status: str,
    timestamp: str | None,
) -> TraceEvent:
    name = str(data.get("name") or "function")
    normalized_name = _normalize_name(name)
    input_mapping = _as_mapping(data.get("input"))
    output_mapping = _as_mapping(data.get("output"))
    exit_code = _extract_exit_code(output_mapping, data.get("mcp_data"), payload.get("error"))

    if normalized_name in COMMAND_TOOL_NAMES:
        command = _extract_command(data.get("input"), input_mapping)
        event_status = "failed" if payload.get("error") or exit_code not in (None, 0) else status
        if not command:
            return TraceEvent(
                event_id,
                "mcp_tool",
                event_status,
                name,
                detail=_event_detail(data.get("input"), data.get("output"), payload.get("error")),
                raw_type=raw_type,
                timestamp=timestamp,
                exit_code=exit_code,
                metadata=payload,
            )
        return TraceEvent(
            event_id,
            "command",
            event_status,
            command,
            detail=_event_detail(data.get("output"), payload.get("error")),
            raw_type=raw_type,
            timestamp=timestamp,
            command=command,
            exit_code=exit_code,
            metadata=payload,
        )

    if normalized_name in FILE_TOOL_NAMES:
        files = _extract_files(input_mapping or data.get("input"))
        failed = bool(payload.get("error")) or exit_code not in (None, 0)
        if failed or not files:
            return TraceEvent(
                event_id,
                "mcp_tool" if failed else "unknown",
                "failed" if failed else status,
                name,
                detail=_event_detail(data.get("input"), data.get("output"), payload.get("error")),
                raw_type=raw_type,
                timestamp=timestamp,
                exit_code=exit_code,
                metadata=payload,
            )
        return TraceEvent(
            event_id,
            "file_change",
            status,
            name,
            detail=", ".join(files) or _compact(input_mapping),
            raw_type=raw_type,
            timestamp=timestamp,
            files=files,
            metadata=payload,
        )

    return TraceEvent(
        event_id,
        "mcp_tool",
        "failed" if payload.get("error") else status,
        name,
        detail=_event_detail(data.get("input"), data.get("output"), payload.get("error")),
        raw_type=raw_type,
        timestamp=timestamp,
        exit_code=exit_code,
        metadata=payload,
    )


def _custom_event(
    payload: dict[str, Any],
    data: dict[str, Any],
    event_id: str,
    raw_type: str,
    status: str,
    timestamp: str | None,
) -> TraceEvent:
    name = str(data.get("name") or "custom")
    normalized_name = _normalize_name(name)
    custom_data = data.get("data")
    custom_mapping = custom_data if isinstance(custom_data, dict) else {}

    if normalized_name in FILE_TOOL_NAMES:
        files = _extract_files(custom_mapping)
        exit_code = _extract_exit_code(custom_mapping, payload.get("error"))
        failed = bool(payload.get("error")) or exit_code not in (None, 0)
        if failed or not files:
            return TraceEvent(
                event_id,
                "mcp_tool" if failed else "unknown",
                "failed" if failed else status,
                name,
                detail=_event_detail(custom_data, payload.get("error")),
                raw_type=raw_type,
                timestamp=timestamp,
                exit_code=exit_code,
                metadata=payload,
            )
        return TraceEvent(
            event_id,
            "file_change",
            status,
            name,
            detail=", ".join(files) or _compact(custom_mapping),
            raw_type=raw_type,
            timestamp=timestamp,
            files=files,
            metadata=payload,
        )

    if normalized_name in COMMAND_TOOL_NAMES:
        command = _extract_command(custom_data, custom_mapping)
        exit_code = _extract_exit_code(custom_mapping, payload.get("error"))
        event_status = "failed" if payload.get("error") or exit_code not in (None, 0) else status
        if not command:
            return TraceEvent(
                event_id,
                "mcp_tool",
                event_status,
                name,
                detail=_event_detail(custom_data, payload.get("error")),
                raw_type=raw_type,
                timestamp=timestamp,
                exit_code=exit_code,
                metadata=payload,
            )
        return TraceEvent(
            event_id,
            "command",
            event_status,
            command,
            detail=_event_detail(custom_mapping.get("output"), payload.get("error")),
            raw_type=raw_type,
            timestamp=timestamp,
            command=command,
            exit_code=exit_code,
            metadata=payload,
        )

    if normalized_name in {"task", "turn"}:
        return TraceEvent(
            event_id,
            "turn",
            status,
            name,
            detail=_compact(custom_mapping),
            raw_type=raw_type,
            timestamp=timestamp,
            metadata=payload,
        )

    return TraceEvent(
        event_id,
        "unknown",
        status,
        name,
        detail=_compact(custom_data),
        raw_type=raw_type,
        timestamp=timestamp,
        metadata=payload,
    )


def _select_usage(records: list[_Record]) -> dict[str, Any]:
    candidates: dict[str, list[dict[str, Any]]] = {
        "task": [],
        "turn": [],
        "generation": [],
    }
    for record in records:
        span_data = record.payload.get("span_data")
        if not isinstance(span_data, dict):
            continue
        span_type = span_data.get("type")
        if span_type in {"generation", "response"} and isinstance(span_data.get("usage"), dict):
            candidates["generation"].append(span_data["usage"])
            continue
        if span_type != "custom":
            continue
        name = _normalize_name(str(span_data.get("name") or ""))
        custom_data = span_data.get("data")
        if name in {"task", "turn"} and isinstance(custom_data, dict):
            usage = custom_data.get("usage")
            if isinstance(usage, dict):
                candidates[name].append(usage)

    tier_totals = {
        source: _sum_usage(raw_values, infer_requests=source == "generation")
        for source, raw_values in candidates.items()
    }
    result: dict[str, int | float] = {}
    for key in USAGE_KEYS:
        for source in ("task", "turn", "generation"):
            if key in tier_totals[source]:
                result[key] = tier_totals[source][key]
                break
    return result


def _sum_usage(
    raw_values: list[dict[str, Any]],
    *,
    infer_requests: bool,
) -> dict[str, int | float]:
    totals: dict[str, int | float] = {}
    for raw_usage in raw_values:
        for key, value in _normalize_usage(raw_usage).items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[key] = totals.get(key, 0) + value
    if infer_requests and raw_values and "requests" not in totals:
        totals["requests"] = len(raw_values)
    return totals


def _normalize_usage(usage: Mapping[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key in USAGE_KEYS:
        value = usage.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            normalized[key] = value

    input_details = usage.get("input_tokens_details")
    if "cached_input_tokens" not in normalized and isinstance(input_details, Mapping):
        cached = input_details.get("cached_tokens")
        if isinstance(cached, (int, float)) and not isinstance(cached, bool):
            normalized["cached_input_tokens"] = cached

    output_details = usage.get("output_tokens_details")
    if "reasoning_output_tokens" not in normalized and isinstance(output_details, Mapping):
        reasoning = output_details.get("reasoning_tokens")
        if isinstance(reasoning, (int, float)) and not isinstance(reasoning, bool):
            normalized["reasoning_output_tokens"] = reasoning
    return normalized


def _extract_command(raw_input: Any, parsed: Mapping[str, Any]) -> str | None:
    for key in ("command", "cmd", "script"):
        value = parsed.get(key)
        if isinstance(value, str) and value:
            return value
    if isinstance(raw_input, str) and raw_input and not parsed:
        return raw_input
    return None


def _extract_exit_code(*values: Any) -> int | None:
    for value in values:
        if isinstance(value, Mapping):
            for key in ("exit_code", "exitCode", "return_code", "returncode"):
                candidate = value.get(key)
                if isinstance(candidate, int) and not isinstance(candidate, bool):
                    return candidate
            nested = _extract_exit_code(*value.values())
            if nested is not None:
                return nested
        elif isinstance(value, str):
            parsed = _as_mapping(value)
            if parsed:
                nested = _extract_exit_code(parsed)
                if nested is not None:
                    return nested
    return None


def _extract_files(value: Any) -> list[str]:
    found: list[str] = []

    def visit(item: Any, key: str | None = None) -> None:
        if isinstance(item, Mapping):
            for child_key, child_value in item.items():
                visit(child_value, str(child_key))
            return
        if isinstance(item, list):
            for child in item:
                visit(child, key)
            return
        if key in {"file", "filename", "path"} and isinstance(item, str) and item:
            found.append(item)
        elif key == "files" and isinstance(item, str) and item:
            found.append(item)
        elif key in {"diff", "patch"} and isinstance(item, str):
            found.extend(_patch_files(item))

    visit(value)
    return list(dict.fromkeys(found))


def _patch_files(patch: str) -> list[str]:
    found: list[str] = []
    prefixes = (
        "*** Add File: ",
        "*** Delete File: ",
        "*** Update File: ",
        "+++ ",
        "--- ",
    )
    for line in patch.splitlines():
        for prefix in prefixes:
            if not line.startswith(prefix):
                continue
            path = line[len(prefix) :].strip().split("\t", maxsplit=1)[0]
            if path in {"/dev/null", ""}:
                break
            if prefix in {"+++ ", "--- "} and path.startswith(("a/", "b/")):
                path = path[2:]
            found.append(path)
            break
    return found


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _normalize_name(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(".", "_").replace(" ", "_")


def _usage_detail(usage: Mapping[str, Any]) -> str:
    return ", ".join(f"{key}={value}" for key, value in usage.items())


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return value if isinstance(value, str) else _compact(value)


def _event_detail(*values: Any) -> str:
    return "\n".join(part for value in values if (part := _stringify(value)))


def _compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
