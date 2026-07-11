#!/usr/bin/env python3
"""Reject machine-specific paths and raw runtime logs in tracked artifacts."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOME_NAMES = frozenset({".", "..", "EXAMPLE", "REDACTED", "runner", "user"})
ALLOWED_ACCOUNT_NAMES = frozenset({"REDACTED", "root", "runner", "user"})
HOME_PATH_RE = re.compile(r"/(?:Users|home)/(?P<name>[^/\s\"'\\]+)(?=/)")
LS_OWNER_RE = re.compile(
    r"(?:^|\\n|\n)[bcdlps-][rwxStTs-]{9}[@+]?\s+\d+\s+"
    r"(?P<owner>[^\s\\]+)\s+(?P<group>[^\s\\]+)"
)
SECRET_PATTERNS = (
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "private key material",
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |PGP )?PRIVATE KEY-----"),
    ),
    ("Bearer token", re.compile(r"\bBearer [A-Za-z0-9._~-]{20,}\b")),
)


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    reason: str

    def render(self) -> str:
        location = f"{self.path}:{self.line}" if self.line else self.path
        return f"{location}: {self.reason}"


def tracked_paths(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [root / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def find_violations(paths: Iterable[Path], root: Path = ROOT) -> list[Violation]:
    violations: list[Violation] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if path.name == "codex.stderr":
            violations.append(Violation(relative, 0, "raw codex.stderr must not be tracked"))
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            for match in HOME_PATH_RE.finditer(line):
                name = match.group("name")
                if name not in ALLOWED_HOME_NAMES:
                    violations.append(
                        Violation(
                            relative,
                            line_number,
                            f"machine-specific home path uses non-placeholder account {name!r}",
                        )
                    )
            for match in LS_OWNER_RE.finditer(line):
                owner = match.group("owner")
                if owner not in ALLOWED_ACCOUNT_NAMES:
                    violations.append(
                        Violation(
                            relative,
                            line_number,
                            f"captured directory listing uses non-placeholder owner {owner!r}",
                        )
                    )
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        Violation(relative, line_number, f"possible {label} in tracked text")
                    )
    return violations


def main() -> int:
    violations = find_violations(tracked_paths())
    if violations:
        print("Public artifact hygiene check failed:", file=sys.stderr)
        for violation in violations:
            print(f"- {violation.render()}", file=sys.stderr)
        return 1
    print("Public artifact hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
