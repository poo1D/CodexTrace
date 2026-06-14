import json

from codex_trace.parser import is_verification_command, parse_jsonl, parse_lines


def test_unittest_command_counts_as_verification():
    assert is_verification_command("python3 -m unittest discover -s tests")
    assert is_verification_command("python3 ../grader/check.py")
    assert is_verification_command("node ../grader/check.mjs")


def test_parse_demo_trace():
    trace = parse_jsonl("demo/failing-codex-trace.jsonl")

    assert trace.thread_id == "demo-thread-001"
    assert len(trace.events) == 10
    assert trace.usage["input_tokens"] == 28600
    assert any(event.kind == "command" and event.command == "pytest -q" for event in trace.events)
    assert any(event.kind == "file_change" and event.files == ["src/cart.py"] for event in trace.events)
    assert trace.events[3].phase == "inspect"
    assert trace.events[5].phase == "verify"
    assert trace.events[6].phase == "edit"
    assert trace.events[7].phase == "recover"
    assert trace.events[8].phase == "complete"


def test_parse_codex_aggregated_output():
    trace = parse_jsonl("demo/real-codex-run.jsonl")
    command_events = [event for event in trace.events if event.kind == "command" and event.status == "completed"]

    assert trace.thread_id
    assert all(event.phase for event in trace.events)
    assert any("README.md" in event.detail for event in command_events)


def test_parse_lines_covers_codex_event_variants():
    payloads = [
        {"type": "thread.started", "thread_id": "parser-test-thread"},
        {"type": "unrecognized.top_level"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "Working."}},
        {"type": "item.completed", "item": {"type": "reasoning", "summary": "Inspect first."}},
        {"type": "item.completed", "item": {"type": "command_execution", "command": "rg target", "exit_code": 0}},
        {"type": "item.completed", "item": {"type": "file_change", "files": ["src/app.py"]}},
        {"type": "item.completed", "item": {"type": "command", "cmd": "pytest -q", "exit_code": 0}},
        {"type": "item.completed", "item": {"type": "mcp_tool_call", "name": "github.fetch", "arguments": {"path": "README.md"}}},
        {"type": "item.completed", "item": {"type": "web_search", "query": "codex trace parser"}},
        {"type": "item.completed", "item": {"type": "plan_update", "steps": []}},
        {"type": "error", "message": "runtime error"},
        {"type": "turn.completed", "usage": {"input_tokens": 123, "output_tokens": 45}},
    ]
    trace = parse_lines(json.dumps(payload) for payload in payloads)
    kinds = {event.kind for event in trace.events}

    assert trace.thread_id == "parser-test-thread"
    assert trace.usage["input_tokens"] == 123
    assert {"thread", "agent_message", "reasoning", "command", "file_change", "mcp_tool", "web_search", "plan", "error", "unknown", "turn"} <= kinds
    assert any(event.phase == "other" for event in trace.events)
    assert any(event.kind == "mcp_tool" and event.title == "github.fetch" for event in trace.events)
