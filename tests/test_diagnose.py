from codex_trace.diagnose import diagnose
from codex_trace.parser import parse_jsonl
from codex_trace.report import render_markdown


def finding_codes(trace_path):
    return {finding.code for finding in diagnose(parse_jsonl(trace_path)).findings}


def test_detects_required_failure_modes():
    diagnosis = diagnose(parse_jsonl("demo/failing-codex-trace.jsonl"))
    codes = {finding.code for finding in diagnosis.findings}

    assert "command_failure_unhandled" in codes
    assert "verification_gap" in codes
    assert "premature_completion" in codes
    assert "repeated_search_or_read" in codes
    assert "sandbox_or_permission_block" in codes
    assert all(finding.event_ids for finding in diagnosis.findings)


def test_markdown_report_lists_finding_event_ids():
    trace = parse_jsonl("demo/failing-codex-trace.jsonl")
    markdown = render_markdown(trace, diagnose(trace))

    assert "- Event IDs: `e0005`, `e0007`" in markdown
    assert "- Event IDs: `e0006`" in markdown
    assert "- Event IDs: `e0003`, `e0004`" in markdown


def test_detects_verification_gap_when_changed_without_tests():
    trace = parse_jsonl("demo/failing-codex-trace.jsonl")
    trace.events = [event for event in trace.events if not (event.kind == "command" and "pytest" in (event.command or ""))]
    diagnosis = diagnose(trace)

    assert "verification_gap" in {finding.code for finding in diagnosis.findings}


def test_detects_long_context_no_progress():
    trace = parse_jsonl("demo/failing-codex-trace.jsonl")
    trace.events = [event for event in trace.events if event.kind not in {"file_change", "command"}]
    diagnosis = diagnose(trace)

    assert "long_context_no_progress" in {finding.code for finding in diagnosis.findings}


def test_healthy_trace_has_no_findings():
    diagnosis = diagnose(parse_jsonl("demo/healthy-codex-trace.jsonl"))

    assert diagnosis.outcome == "healthy"
    assert diagnosis.findings == []


def test_real_trace_does_not_treat_readme_text_as_sandbox_failure():
    diagnosis = diagnose(parse_jsonl("demo/real-codex-run.jsonl"))

    assert diagnosis.outcome == "healthy"
    assert "sandbox_or_permission_block" not in {finding.code for finding in diagnosis.findings}


def test_detects_high_repeated_tool_call_volume_in_real_hard_trace():
    diagnosis = diagnose(parse_jsonl("benchmark/hard/pilot/hard30-real/shards/HARD-033/HARD-033/baseline/trace.jsonl"))

    assert "repeated_search_or_read" in {finding.code for finding in diagnosis.findings}
    assert any(
        "repeated command invocation" in evidence
        for finding in diagnosis.findings
        for evidence in finding.evidence
    )


def test_diagnoses_mcp_tool_call_trace_fixture():
    trace = parse_jsonl("tests/fixtures/mcp-tool-trace.jsonl")
    diagnosis = diagnose(trace)
    codes = {finding.code for finding in diagnosis.findings}

    assert diagnosis.outcome == "failed"
    assert trace.events[0].tool_name == "filesystem.read_file"
    assert trace.events[1].tool_arguments["path"] == "src/calc.py"
    assert trace.events[2].tool_error["message"].startswith("FAILED")
    assert "command_failure_unhandled" in codes
    assert diagnosis.metrics["tool_call_events"] == 3
    assert diagnosis.metrics["failed_tool_events"] == 1
    assert diagnosis.metrics["verification_tool_events"] == 1
    assert diagnosis.metrics["post_edit_verification_commands"] == 1


def test_diagnoses_openai_function_call_trace_fixture():
    trace = parse_jsonl("tests/fixtures/openai-function-trace.jsonl")
    diagnosis = diagnose(trace)
    codes = {finding.code for finding in diagnosis.findings}

    assert diagnosis.outcome == "failed"
    assert trace.events[1].tool_name == "edit_file"
    assert trace.events[1].files == ["src/search_index.py"]
    assert trace.events[2].tool_arguments["command"] == "python3 -m unittest discover -s tests"
    assert "command_failure_unhandled" in codes
    assert "sandbox_or_permission_block" in codes
