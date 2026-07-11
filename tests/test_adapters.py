import json
from pathlib import Path

import pytest

from codex_trace.adapters import adapter_names, get_adapter, load_trace
from codex_trace.cli import main
from codex_trace.diagnose import diagnose
from codex_trace.parser import parse_jsonl


FIXTURES = Path("tests/fixtures/openai_agents")
TOOL_RUN_TRACE_ID = "trace_00000000000000000000000000000001"


def test_codex_adapter_is_backward_compatible():
    path = Path("demo/failing-codex-trace.jsonl")

    assert load_trace(path, adapter="codex").to_dict() == parse_jsonl(path).to_dict()


def test_registry_requires_an_explicit_known_adapter():
    assert adapter_names() == ("codex", "openai-agents")

    with pytest.raises(ValueError, match="Unknown trace adapter"):
        get_adapter("auto")


def test_openai_agents_tool_run_maps_to_existing_schema():
    trace = load_trace(FIXTURES / "tool_run.jsonl", adapter="openai-agents")

    assert trace.thread_id == TOOL_RUN_TRACE_ID
    assert [event.kind for event in trace.events] == [
        "thread",
        "agent_message",
        "usage",
        "command",
        "file_change",
        "command",
        "mcp_tool",
        "unknown",
    ]

    inspect, edit, verify = trace.events[3:6]
    assert (inspect.command, inspect.exit_code, inspect.phase) == ("rg -n TODO src", 0, "inspect")
    assert (edit.files, edit.phase) == (["src/app.py"], "edit")
    assert (verify.command, verify.exit_code, verify.phase) == ("pytest -q", 0, "verify")
    assert trace.events[6].title == "fetch_weather"
    assert trace.events[2].metadata["span_data"]["usage"]["future_usage"] == {
        "sentinel": "kept"
    }

    assert trace.usage == {
        "input_tokens": 120,
        "cached_input_tokens": 20,
        "output_tokens": 30,
        "reasoning_output_tokens": 10,
        "total_tokens": 150,
        "requests": 1,
    }


def test_openai_agents_failed_tool_keeps_error_and_recovery_phase():
    trace = load_trace(FIXTURES / "failed_tool.jsonl", adapter="openai-agents")
    command = trace.events[1]
    tool = trace.events[2]
    recovery = trace.events[3]

    assert (command.kind, command.status, command.exit_code, command.phase) == (
        "command",
        "failed",
        1,
        "verify",
    )
    assert (tool.kind, tool.status, tool.phase) == ("mcp_tool", "failed", "recover")
    assert tool.metadata["error"]["message"] == "fixture timeout"
    assert recovery.phase == "recover"


def test_usage_uses_high_level_fields_and_backfills_missing_generation_fields():
    trace = load_trace(FIXTURES / "usage_priority.jsonl", adapter="openai-agents")

    assert trace.usage == {
        "input_tokens": 100,
        "cached_input_tokens": 10,
        "output_tokens": 20,
        "reasoning_output_tokens": 5,
        "total_tokens": 120,
        "requests": 2,
    }


def test_error_only_command_is_diagnosed_and_keeps_permission_detail():
    records = [
        {
            "object": "trace",
            "id": "trace_error_only",
            "workflow_name": "Error-only command",
        },
        {
            "object": "trace.span",
            "id": "span_error_only",
            "trace_id": "trace_error_only",
            "parent_id": None,
            "started_at": "2026-07-01T00:00:01+00:00",
            "ended_at": "2026-07-01T00:00:02+00:00",
            "span_data": {
                "type": "function",
                "name": "exec_command",
                "input": '{"command":"npm install"}',
                "output": None,
                "mcp_data": None,
            },
            "error": {"message": "permission denied by sandbox"},
        },
    ]
    trace = get_adapter("openai-agents").parse_lines(json.dumps(row) for row in records)
    result = diagnose(trace)

    command = trace.events[1]
    assert (command.kind, command.status, command.exit_code) == ("command", "failed", None)
    assert "permission denied by sandbox" in command.detail
    assert result.metrics["failed_commands"] == 1
    assert {finding.code for finding in result.findings} >= {
        "command_failure_unhandled",
        "sandbox_or_permission_block",
    }


def test_file_tools_require_success_and_extract_patch_headers():
    base = {
        "object": "trace.span",
        "trace_id": "trace_file_tools",
        "parent_id": None,
        "started_at": "2026-07-01T00:00:01+00:00",
        "ended_at": "2026-07-01T00:00:02+00:00",
    }
    records = [
        {
            "object": "trace",
            "id": "trace_file_tools",
            "workflow_name": "File tools",
        },
        {
            **base,
            "id": "span_good_patch",
            "span_data": {
                "type": "function",
                "name": "apply_patch",
                "input": json.dumps({
                    "patch": (
                        "*** Begin Patch\n"
                        "*** Update File: src/app.py\n"
                        "*** Add File: tests/test_app.py\n"
                        "*** End Patch"
                    )
                }),
                "output": "Done",
                "mcp_data": None,
            },
            "error": None,
        },
        {
            **base,
            "id": "span_failed_patch",
            "started_at": "2026-07-01T00:00:03+00:00",
            "ended_at": "2026-07-01T00:00:04+00:00",
            "span_data": {
                "type": "function",
                "name": "apply_patch",
                "input": '{"patch":"*** Update File: src/broken.py"}',
                "output": None,
                "mcp_data": None,
            },
            "error": {"message": "permission denied"},
        },
    ]

    trace = get_adapter("openai-agents").parse_lines(json.dumps(row) for row in records)
    good, failed = trace.events[1:]

    assert (good.kind, good.files) == ("file_change", ["src/app.py", "tests/test_app.py"])
    assert (failed.kind, failed.status, failed.files) == ("mcp_tool", "failed", [])
    assert failed.phase == "recover"


def test_command_named_tool_without_structured_command_stays_generic():
    records = [
        {"object": "trace", "id": "trace_generic_shell", "workflow_name": "Generic shell"},
        {
            "object": "trace.span",
            "id": "span_generic_shell",
            "trace_id": "trace_generic_shell",
            "parent_id": None,
            "started_at": "2026-07-01T00:00:01+00:00",
            "ended_at": "2026-07-01T00:00:02+00:00",
            "span_data": {
                "type": "function",
                "name": "shell",
                "input": '{"query":"not a command"}',
                "output": "ignored",
                "mcp_data": None,
            },
            "error": None,
        },
    ]

    trace = get_adapter("openai-agents").parse_lines(json.dumps(row) for row in records)

    assert (trace.events[1].kind, trace.events[1].command) == ("mcp_tool", None)


def test_openai_agents_unknown_fields_are_preserved_verbatim():
    trace = load_trace(FIXTURES / "unknown_fields.jsonl", adapter="openai-agents")
    thread, future = trace.events

    assert thread.metadata["future_trace_field"] == {"nested": True}
    assert thread.metadata["metadata"]["trace_metadata_sentinel"] == "kept"
    assert future.kind == "unknown"
    assert future.metadata["future_span_field"] == {"nested": True}
    assert future.metadata["metadata"]["span_metadata_sentinel"] == "kept"
    assert future.metadata["span_data"]["future_span_data_field"] == [1, 2, 3]
    assert future.metadata["span_data"]["data"]["span_data_sentinel"] == {"nested": "kept"}


def test_openai_agents_rejects_mixed_trace_ids():
    with pytest.raises(ValueError, match="mixes multiple trace ids"):
        load_trace(FIXTURES / "multiple_traces.jsonl", adapter="openai-agents")


def test_collect_cli_accepts_openai_agents_adapter(capsys):
    assert main([
        "collect",
        str(FIXTURES / "tool_run.jsonl"),
        "--adapter",
        "openai-agents",
    ]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["thread_id"] == TOOL_RUN_TRACE_ID
    assert output["events"][4]["files"] == ["src/app.py"]


def test_diagnose_cli_accepts_openai_agents_adapter(capsys):
    assert main([
        "diagnose",
        str(FIXTURES / "tool_run.jsonl"),
        "--adapter",
        "openai-agents",
        "--format",
        "json",
    ]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["trace"]["thread_id"] == TOOL_RUN_TRACE_ID
    assert output["diagnosis"]["outcome"] == "healthy"


@pytest.mark.parametrize("adapter_args", [[], ["--adapter", "codex"]])
def test_collect_cli_keeps_codex_default_output(adapter_args, capsys):
    path = "demo/failing-codex-trace.jsonl"

    assert main(["collect", path, *adapter_args]) == 0

    assert json.loads(capsys.readouterr().out) == parse_jsonl(path).to_dict()
