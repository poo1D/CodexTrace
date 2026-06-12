from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TARGETS = (
    Path("README.md"),
    Path("docs/paper_draft.md"),
    Path("docs/paper_outline.md"),
    Path("docs/results_summary.md"),
    Path("docs/reproducibility_checklist.md"),
)


@dataclass(frozen=True)
class RequiredCaveat:
    path: Path
    phrases: tuple[str, ...]
    description: str


REQUIRED_CAVEATS = (
    RequiredCaveat(
        path=Path("README.md"),
        phrases=("not verification-rate lift", "mechanism check"),
        description="README should frame ordinary-pilot verification lift as unsupported and the no-verify ablation as mechanism-only.",
    ),
    RequiredCaveat(
        path=Path("docs/paper_draft.md"),
        phrases=("negative result for the verification-rate-lift claim", "not claim a verification-rate lift"),
        description="Paper draft should present verification-lift as a negative result, not as a supported main finding.",
    ),
    RequiredCaveat(
        path=Path("docs/results_summary.md"),
        phrases=("does not support a verification-rate lift", "not an ordinary baseline"),
        description="Generated results summary should preserve the verification-lift boundary and no-verify ablation qualifier.",
    ),
    RequiredCaveat(
        path=Path("docs/reproducibility_checklist.md"),
        phrases=("Original-thesis verification-rate lift is not yet supported", "mechanism ablation"),
        description="Reproducibility checklist should map unsupported verification lift and ablation evidence explicitly.",
    ),
)

UNQUALIFIED_OVERCLAIM_PATTERNS = (
    re.compile(r"\b(?:harness\s+)?intervention\s+(?:increases|improves|raises)\s+(?:the\s+)?verification(?:-rate|\s+rate)\b", re.I),
    re.compile(r"\bverification(?:-rate|\s+rate)\s+(?:increases|improves|rises)\s+under\s+(?:the\s+)?(?:ordinary|baseline|weak-baseline)\b", re.I),
    re.compile(r"\btrace(?:-based)?\s+(?:rules|signals)\s+(?:detect|predict|explain)\s+hidden\s+semantic\s+(?:failures|correctness)\b", re.I),
)

QUALIFIER_WORDS = (
    "not",
    "unsupported",
    "negative result",
    "does not support",
    "no-verify",
    "ablation",
    "mechanism",
    "boundary",
    "limitation",
)


def audit_claim_text_guard(targets: tuple[Path, ...] = DEFAULT_TARGETS) -> dict[str, Any]:
    target_set = {path for path in targets}
    files = []
    problems = []

    for path in targets:
        text = path.read_text(encoding="utf-8")
        file_problems = _overclaim_problems(path, text)
        files.append({
            "path": str(path),
            "line_count": len(text.splitlines()),
            "problems": file_problems,
        })
        problems.extend(file_problems)

    for caveat in REQUIRED_CAVEATS:
        if caveat.path not in target_set:
            continue
        text = _normalize_text(caveat.path.read_text(encoding="utf-8"))
        missing = [_normalize_text(phrase) for phrase in caveat.phrases if _normalize_text(phrase) not in text]
        if missing:
            problem = {
                "path": str(caveat.path),
                "line": None,
                "kind": "missing_caveat",
                "match": ", ".join(missing),
                "detail": caveat.description,
            }
            problems.append(problem)
            for file_row in files:
                if file_row["path"] == str(caveat.path):
                    file_row["problems"].append(problem)

    return {
        "ok": not problems,
        "problem_count": len(problems),
        "files": files,
        "problems": problems,
    }


def render_claim_text_guard_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Claim Text Guard",
        "",
        "This generated guard checks paper-facing text for unsupported claim drift.",
        "",
        f"- Status: {'pass' if result['ok'] else 'fail'}",
        f"- Files checked: {len(result['files'])}",
        f"- Problems: {result['problem_count']}",
        "",
        "## Files",
        "",
        "| File | Lines | Problems |",
        "| --- | ---: | ---: |",
    ]
    for row in result["files"]:
        lines.append(f"| `{row['path']}` | {row['line_count']} | {len(row['problems'])} |")

    lines.extend(["", "## Problems", ""])
    if not result["problems"]:
        lines.append("No unsupported-claim drift detected.")
    else:
        lines.extend([
            "| File | Line | Kind | Match | Detail |",
            "| --- | ---: | --- | --- | --- |",
        ])
        for problem in result["problems"]:
            line = "" if problem["line"] is None else str(problem["line"])
            lines.append(
                f"| `{problem['path']}` | {line} | {problem['kind']} | `{problem['match']}` | {problem['detail']} |"
            )
    lines.append("")
    return "\n".join(lines)


def write_claim_text_guard_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_claim_text_guard_markdown(result), encoding="utf-8")


def _overclaim_problems(path: Path, text: str) -> list[dict[str, Any]]:
    problems = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        for pattern in UNQUALIFIED_OVERCLAIM_PATTERNS:
            match = pattern.search(line)
            if match and not _has_local_qualifier(lines, line_number):
                problems.append({
                    "path": str(path),
                    "line": line_number,
                    "kind": "unqualified_overclaim",
                    "match": match.group(0),
                    "detail": "Add the negative-result, boundary, or ablation qualifier required by the current evidence.",
                })
    return problems


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _has_local_qualifier(lines: list[str], line_number: int) -> bool:
    start = max(0, line_number - 2)
    end = min(len(lines), line_number + 1)
    window = " ".join(lines[start:end]).lower()
    return any(word in window for word in QUALIFIER_WORDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Guard paper-facing text against unsupported claim drift.")
    parser.add_argument("--target", action="append", type=Path, help="Paper-facing markdown path to check. Defaults to standard docs.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    targets = tuple(args.target) if args.target else DEFAULT_TARGETS
    result = audit_claim_text_guard(targets)
    if args.json_output or args.markdown_output:
        write_claim_text_guard_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_claim_text_guard_markdown(result), end="")
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
