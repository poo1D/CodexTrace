from __future__ import annotations

from pathlib import Path

from ..schema import Trace
from .base import TraceAdapter
from .codex import CodexAdapter
from .openai_agents import OpenAIAgentsAdapter


_ADAPTERS: dict[str, TraceAdapter] = {
    "codex": CodexAdapter(),
    "openai-agents": OpenAIAgentsAdapter(),
}


def adapter_names() -> tuple[str, ...]:
    return tuple(_ADAPTERS)


def get_adapter(name: str) -> TraceAdapter:
    try:
        return _ADAPTERS[name]
    except KeyError as exc:
        choices = ", ".join(adapter_names())
        raise ValueError(f"Unknown trace adapter {name!r}; choose one of: {choices}") from exc


def load_trace(path: str | Path, *, adapter: str = "codex") -> Trace:
    source = Path(path)
    lines = source.read_text(encoding="utf-8").splitlines()
    return get_adapter(adapter).parse_lines(lines, source=str(source))


__all__ = [
    "TraceAdapter",
    "adapter_names",
    "get_adapter",
    "load_trace",
]
