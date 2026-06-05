from codex_trace.parser import parse_jsonl


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
