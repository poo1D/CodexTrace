from __future__ import annotations

from collections import Counter

from .parser import is_search_command, is_verification_command
from .schema import Diagnosis, Finding, Trace, TraceEvent


SANDBOX_WORDS = ("sandbox", "permission", "approval", "denied", "not permitted", "requires approval")


def diagnose(trace: Trace) -> Diagnosis:
    findings: list[Finding] = []
    metrics = _metrics(trace)

    failed_commands = [event for event in trace.events if event.kind == "command" and event.exit_code not in (None, 0)]
    unresolved_failed_commands = _unresolved_failed_commands(trace.events, failed_commands)
    if unresolved_failed_commands:
        findings.append(Finding(
            code="command_failure_unhandled",
            title="Command failures were not clearly handled",
            severity="high",
            evidence=[_event_label(event) for event in unresolved_failed_commands],
            recommendation="After a failed command, add an explicit repair step and rerun the relevant verification command before ending the turn.",
            event_ids=[event.id for event in unresolved_failed_commands],
        ))

    if metrics["file_change_events"] > 0 and metrics["post_edit_verification_commands"] == 0:
        changed = [event.id for event in trace.events if event.kind == "file_change"]
        findings.append(Finding(
            code="verification_gap",
            title="Files changed without a verification command",
            severity="high",
            evidence=[f"{metrics['file_change_events']} file-change event(s), 0 post-edit verification command(s)."],
            recommendation="Add a post-edit validation step such as tests, type checks, or a focused smoke command.",
            event_ids=changed,
        ))

    premature_events = _premature_completion_events(trace.events, metrics)
    if premature_events:
        findings.append(Finding(
            code="premature_completion",
            title="Agent claimed completion without verification evidence",
            severity="high",
            evidence=[_event_label(event) for event in premature_events],
            recommendation="Require the final answer to cite a passing post-edit verification command before declaring the task complete.",
            event_ids=[event.id for event in premature_events],
        ))

    repeated = _repeated_searches(trace.events)
    if repeated:
        findings.append(Finding(
            code="repeated_search_or_read",
            title="Repeated search/read commands suggest inefficient exploration",
            severity="medium",
            evidence=[f"`{cmd}` repeated {count} times" for cmd, count in repeated],
            recommendation="Summarize discovered facts after each exploration pass and switch from broad search to targeted file reads.",
        ))

    repeated_volume = _repeated_tool_call_volume(trace.events)
    if repeated_volume and not repeated:
        findings.append(Finding(
            code="repeated_search_or_read",
            title="High repeated tool-call volume suggests inefficient exploration",
            severity="medium",
            evidence=repeated_volume,
            recommendation="Checkpoint what has already been learned, then switch to a narrower edit/verification loop instead of repeating the same commands.",
        ))

    sandbox_events = _sandbox_events(trace.events)
    if sandbox_events:
        findings.append(Finding(
            code="sandbox_or_permission_block",
            title="Sandbox or permission friction blocked progress",
            severity="medium",
            evidence=[_event_label(event) for event in sandbox_events],
            recommendation="Declare the needed permission up front, reduce the command scope, or redesign the workflow to keep privileged steps outside the agent loop.",
            event_ids=[event.id for event in sandbox_events],
        ))

    if _long_context_no_progress(trace, metrics):
        findings.append(Finding(
            code="long_context_no_progress",
            title="High context usage with weak implementation progress",
            severity="medium",
            evidence=[f"input_tokens={metrics['input_tokens']}, command_events={metrics['command_events']}, file_change_events={metrics['file_change_events']}"],
            recommendation="Introduce a compact task state, explicit next action, and stop condition before adding more context.",
        ))

    if any(event.status == "failed" and event.kind == "turn" for event in trace.events):
        findings.append(Finding(
            code="turn_failed",
            title="Codex turn failed",
            severity="high",
            evidence=[_event_label(event) for event in trace.events if event.status == "failed" and event.kind == "turn"],
            recommendation="Inspect the last successful tool event before the failed turn and resume from that narrower state.",
        ))

    score = _score(findings, metrics)
    outcome = "failed" if any(f.severity == "high" for f in findings) or score >= 70 else "warning" if findings else "healthy"
    summary = _summary(outcome, findings, metrics)
    return Diagnosis(outcome=outcome, failure_score=score, summary=summary, findings=findings, metrics=metrics)


def _metrics(trace: Trace) -> dict[str, int]:
    usage = trace.usage or {}
    phase_counts = Counter(event.phase for event in trace.events)
    return {
        "events": len(trace.events),
        "command_events": sum(event.kind == "command" and event.status != "in_progress" for event in trace.events),
        "failed_commands": sum(event.kind == "command" and event.exit_code not in (None, 0) for event in trace.events),
        "file_change_events": sum(event.kind == "file_change" for event in trace.events),
        "verification_commands": sum(event.kind == "command" and _is_verification(event.command or "") for event in trace.events),
        "post_edit_verification_commands": _post_edit_verification_count(trace.events),
        "search_commands": sum(event.kind == "command" and event.status != "in_progress" and _is_search(event.command or "") for event in trace.events),
        "phase_setup_events": phase_counts["setup"],
        "phase_inspect_events": phase_counts["inspect"],
        "phase_edit_events": phase_counts["edit"],
        "phase_verify_events": phase_counts["verify"],
        "phase_recover_events": phase_counts["recover"],
        "phase_complete_events": phase_counts["complete"],
        "phase_other_events": phase_counts["other"],
        "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "reasoning_output_tokens": int(usage.get("reasoning_output_tokens") or 0),
    }


def _unresolved_failed_commands(events: list[TraceEvent], failed: list[TraceEvent]) -> list[TraceEvent]:
    unresolved = []
    for failed_event in failed:
        idx = events.index(failed_event)
        later_commands = [event for event in events[idx + 1 :] if event.kind == "command"]
        has_later_success = any(event.exit_code in (None, 0) and (_is_verification(event.command or "") or _similar_command(failed_event.command or "", event.command or "")) for event in later_commands)
        if not has_later_success:
            unresolved.append(failed_event)
    return unresolved


def _repeated_searches(events: list[TraceEvent]) -> list[tuple[str, int]]:
    commands = [_normalize_command(event.command or "") for event in events if event.kind == "command" and _is_search(event.command or "")]
    return [(cmd, count) for cmd, count in Counter(commands).items() if count >= 2]


def _repeated_tool_call_volume(events: list[TraceEvent], threshold: int = 20) -> list[str]:
    commands = [_normalize_command(event.command or "") for event in events if event.kind == "command" and event.command]
    counts = Counter(commands)
    repeated_total = sum(count - 1 for count in counts.values() if count > 1)
    if repeated_total < threshold:
        return []
    top_repeats = [
        f"`{command}` repeated {count} times"
        for command, count in counts.most_common(3)
        if count > 1
    ]
    return [f"{repeated_total} repeated command invocation(s) across the trace."] + top_repeats


def _sandbox_events(events: list[TraceEvent]) -> list[TraceEvent]:
    matches = []
    for event in events:
        if event.status not in {"failed", "blocked", "error"} and event.exit_code in (None, 0):
            continue
        haystack = f"{event.title}\n{event.detail}".lower()
        if any(word in haystack for word in SANDBOX_WORDS):
            matches.append(event)
    return matches


def _long_context_no_progress(trace: Trace, metrics: dict[str, int]) -> bool:
    return metrics["input_tokens"] >= 20000 and metrics["file_change_events"] == 0 and metrics["verification_commands"] == 0 and metrics["command_events"] <= 3


def _post_edit_verification_count(events: list[TraceEvent]) -> int:
    last_change = None
    for index, event in enumerate(events):
        if event.kind == "file_change":
            last_change = index
    if last_change is None:
        return 0
    return sum(event.kind == "command" and _is_verification(event.command or "") for event in events[last_change + 1 :])


def _premature_completion_events(events: list[TraceEvent], metrics: dict[str, int]) -> list[TraceEvent]:
    if metrics["file_change_events"] == 0 or metrics["post_edit_verification_commands"] > 0:
        return []
    completion_words = ("complete", "completed", "done", "fixed", "implemented", "updated")
    candidates = [event for event in events if event.kind == "agent_message"]
    if not candidates:
        return []
    final_message = candidates[-1]
    text = f"{final_message.title}\n{final_message.detail}".lower()
    return [final_message] if any(word in text for word in completion_words) else []


def _score(findings: list[Finding], metrics: dict[str, int]) -> int:
    score = 0
    for finding in findings:
        score += {"low": 10, "medium": 20, "high": 35}[finding.severity]
    score += min(metrics["failed_commands"] * 5, 15)
    return min(score, 100)


def _summary(outcome: str, findings: list[Finding], metrics: dict[str, int]) -> str:
    if not findings:
        return "No obvious failure pattern was detected in this trace."
    top = findings[0].title
    return f"{outcome.title()} trace: {top}. {metrics['events']} events, {metrics['command_events']} commands, {metrics['failed_commands']} failed commands."


def _is_verification(command: str) -> bool:
    return is_verification_command(command)


def _is_search(command: str) -> bool:
    return is_search_command(command)


def _normalize_command(command: str) -> str:
    return " ".join(command.strip().split())


def _similar_command(left: str, right: str) -> bool:
    left_head = _normalize_command(left).split(" ")[:2]
    right_head = _normalize_command(right).split(" ")[:2]
    return bool(left_head and left_head == right_head)


def _event_label(event: TraceEvent) -> str:
    suffix = f" exit_code={event.exit_code}" if event.exit_code is not None else ""
    return f"{event.id} {event.kind}: {event.title}{suffix}"
