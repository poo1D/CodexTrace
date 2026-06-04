from codex_trace.diagnose import diagnose
from codex_trace.parser import parse_jsonl


def finding_codes(trace_path):
    return {finding.code for finding in diagnose(parse_jsonl(trace_path)).findings}


def test_detects_required_failure_modes():
    codes = finding_codes("demo/failing-codex-trace.jsonl")

    assert "command_failure_unhandled" in codes
    assert "verification_gap" in codes
    assert "repeated_search_or_read" in codes
    assert "sandbox_or_permission_block" in codes


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
