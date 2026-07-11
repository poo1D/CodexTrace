from __future__ import annotations

from typing import Iterable

from ..parser import parse_lines
from ..schema import Trace


class CodexAdapter:
    """Backward-compatible adapter for codex exec --json event streams."""

    name = "codex"

    def parse_lines(
        self,
        lines: Iterable[str],
        *,
        source: str | None = None,
    ) -> Trace:
        return parse_lines(lines, source=source)
