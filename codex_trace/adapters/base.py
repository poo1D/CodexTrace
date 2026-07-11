from __future__ import annotations

from typing import Iterable, Protocol

from ..schema import Trace


class TraceAdapter(Protocol):
    """Normalize one documented trace source into the public Trace schema."""

    name: str

    def parse_lines(
        self,
        lines: Iterable[str],
        *,
        source: str | None = None,
    ) -> Trace: ...
