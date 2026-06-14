from __future__ import annotations

import json

from .schema import Diagnosis, Trace


def render_json(trace: Trace, diagnosis: Diagnosis) -> str:
    payload = {"trace": trace.to_dict(), "diagnosis": diagnosis.to_dict()}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_markdown(trace: Trace, diagnosis: Diagnosis) -> str:
    lines = [
        "# CodexTrace Diagnosis Report",
        "",
        f"**Outcome:** {diagnosis.outcome}",
        f"**Failure score:** {diagnosis.failure_score}/100",
        f"**Thread:** {trace.thread_id or 'unknown'}",
        "",
        "## Summary",
        "",
        diagnosis.summary,
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in diagnosis.metrics.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Findings", ""])
    if not diagnosis.findings:
        lines.append("No findings.")
    for finding in diagnosis.findings:
        lines.extend([
            f"### {finding.title}",
            "",
            f"- Code: `{finding.code}`",
            f"- Severity: `{finding.severity}`",
            f"- Recommendation: {finding.recommendation}",
            f"- Event IDs: {_format_event_ids(finding.event_ids)}",
            "- Evidence:",
        ])
        for evidence in finding.evidence:
            lines.append(f"  - {evidence}")
        lines.append("")

    lines.extend(["## Timeline", ""])
    for event in trace.events:
        detail = f" - {event.detail[:140]}" if event.detail else ""
        lines.append(f"- `{event.id}` **{event.kind}** `{event.phase}` `{event.status}`: {event.title}{detail}")

    return "\n".join(lines).rstrip() + "\n"


def _format_event_ids(event_ids: list[str]) -> str:
    return ", ".join(f"`{event_id}`" for event_id in event_ids) if event_ids else "-"
