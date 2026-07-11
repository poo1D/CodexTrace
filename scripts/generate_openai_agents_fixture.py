#!/usr/bin/env python3
"""Generate a deterministic, API-free OpenAI Agents SDK export fixture."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
from typing import Any


TRACE_ID = "trace_00000000000000000000000000000001"
SPAN_IDS = {
    "agent": "span_000000000000000000000001",
    "generation": "span_000000000000000000000002",
    "inspect": "span_000000000000000000000003",
    "edit": "span_000000000000000000000004",
    "verify": "span_000000000000000000000005",
    "tool": "span_000000000000000000000006",
    "unknown": "span_000000000000000000000007",
}


def build_records() -> list[dict[str, Any]]:
    try:
        from agents.tracing import (
            TracingProcessor,
            agent_span,
            custom_span,
            function_span,
            generation_span,
            set_trace_processors,
            trace,
        )
    except ImportError as exc:
        raise SystemExit(
            "Install the fixture-only dependency first: uv run --with openai-agents "
            "python scripts/generate_openai_agents_fixture.py"
        ) from exc

    class CaptureProcessor(TracingProcessor):
        def __init__(self) -> None:
            self.trace_payload: dict[str, Any] | None = None
            self.span_payloads: list[dict[str, Any]] = []

        def on_trace_start(self, trace_object) -> None:
            self.trace_payload = trace_object.export()

        def on_trace_end(self, trace_object) -> None:
            self.trace_payload = trace_object.export()

        def on_span_start(self, span) -> None:
            return None

        def on_span_end(self, span) -> None:
            payload = span.export()
            if payload is not None:
                self.span_payloads.append(payload)

        def shutdown(self) -> None:
            return None

        def force_flush(self) -> None:
            return None

    capture = CaptureProcessor()
    set_trace_processors([capture])

    with trace(
        "Repository repair",
        trace_id=TRACE_ID,
        group_id="fixture-group",
        metadata={"environment": "sanitized"},
    ):
        with agent_span(
            "Builder",
            handoffs=[],
            tools=["exec_command", "apply_patch", "fetch_weather"],
            output_type="text",
            span_id=SPAN_IDS["agent"],
        ):
            with generation_span(
                input=[],
                output=[],
                model="gpt-fixture",
                model_config={},
                usage={
                    "input_tokens": 120,
                    "input_tokens_details": {"cached_tokens": 20},
                    "output_tokens": 30,
                    "output_tokens_details": {"reasoning_tokens": 10},
                    "total_tokens": 150,
                    "future_usage": {"sentinel": "kept"},
                },
                span_id=SPAN_IDS["generation"],
            ):
                pass
            with function_span(
                "exec_command",
                input='{"command":"rg -n TODO src"}',
                output='{"exit_code":0,"stdout":"src/app.py:4: TODO"}',
                span_id=SPAN_IDS["inspect"],
            ):
                pass
            with function_span(
                "apply_patch",
                input=(
                    '{"patch":"*** Begin Patch\\n*** Update File: src/app.py'
                    '\\n@@ fixture @@\\n*** End Patch"}'
                ),
                output="Done",
                span_id=SPAN_IDS["edit"],
            ):
                pass
            with function_span(
                "exec_command",
                input='{"command":"pytest -q"}',
                output='{"exit_code":0,"stdout":"3 passed"}',
                span_id=SPAN_IDS["verify"],
            ):
                pass
            with function_span(
                "fetch_weather",
                input='{"city":"Shanghai"}',
                output="sunny",
                span_id=SPAN_IDS["tool"],
            ):
                pass
            with custom_span(
                "cache.lookup",
                {"hit": True, "span_data_sentinel": "kept"},
                span_id=SPAN_IDS["unknown"],
            ):
                pass

    if capture.trace_payload is None:
        raise RuntimeError("Agents SDK did not emit a trace export")

    rank = {span_id: index for index, span_id in enumerate(SPAN_IDS.values(), start=1)}
    for payload in capture.span_payloads:
        index = rank[str(payload["id"])]
        payload["started_at"] = f"2026-07-01T00:00:{index:02d}.000000+00:00"
        end_second = 8 if payload["id"] == SPAN_IDS["agent"] else index
        payload["ended_at"] = f"2026-07-01T00:00:{end_second:02d}.100000+00:00"
    capture.span_payloads.sort(key=lambda payload: rank[str(payload["id"])])
    return [capture.trace_payload, *capture.span_payloads]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tests/fixtures/openai_agents/tool_run.jsonl"),
    )
    args = parser.parse_args()

    records = build_records()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )
    version = importlib.metadata.version("openai-agents")
    print(f"Wrote {len(records)} record(s) from openai-agents {version} to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
