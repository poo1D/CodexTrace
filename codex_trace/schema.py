from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


EventKind = Literal[
    "thread",
    "turn",
    "agent_message",
    "reasoning",
    "command",
    "file_change",
    "mcp_tool",
    "web_search",
    "plan",
    "error",
    "usage",
    "unknown",
]


@dataclass
class TraceEvent:
    id: str
    kind: EventKind
    status: str
    title: str
    detail: str = ""
    raw_type: str = ""
    timestamp: str | None = None
    command: str | None = None
    exit_code: int | None = None
    files: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "status": self.status,
            "title": self.title,
            "detail": self.detail,
            "raw_type": self.raw_type,
            "timestamp": self.timestamp,
            "command": self.command,
            "exit_code": self.exit_code,
            "files": self.files,
            "metadata": self.metadata,
        }


@dataclass
class Trace:
    thread_id: str | None = None
    events: list[TraceEvent] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "source": self.source,
            "usage": self.usage,
            "events": [event.to_dict() for event in self.events],
        }


@dataclass
class Finding:
    code: str
    title: str
    severity: Literal["low", "medium", "high"]
    evidence: list[str]
    recommendation: str
    event_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "title": self.title,
            "severity": self.severity,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "event_ids": self.event_ids,
        }


@dataclass
class Diagnosis:
    outcome: Literal["healthy", "warning", "failed"]
    failure_score: int
    summary: str
    findings: list[Finding]
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "failure_score": self.failure_score,
            "summary": self.summary,
            "metrics": self.metrics,
            "findings": [finding.to_dict() for finding in self.findings],
        }
