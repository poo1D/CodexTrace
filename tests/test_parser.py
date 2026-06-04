from codex_trace.parser import parse_jsonl


def test_parse_demo_trace():
    trace = parse_jsonl("demo/failing-codex-trace.jsonl")

    assert trace.thread_id == "demo-thread-001"
    assert len(trace.events) == 10
    assert trace.usage["input_tokens"] == 28600
    assert any(event.kind == "command" and event.command == "pytest -q" for event in trace.events)
    assert any(event.kind == "file_change" and event.files == ["src/cart.py"] for event in trace.events)


def test_parse_codex_aggregated_output():
    trace = parse_jsonl("demo/real-codex-run.jsonl")
    command_events = [event for event in trace.events if event.kind == "command" and event.status == "completed"]

    assert trace.thread_id
    assert any("README.md" in event.detail for event in command_events)
