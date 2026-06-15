from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACT_GUIDE = Path("docs/artifact_guide.md")

STEP_PATTERN = re.compile(r"^(\d+)\. ")
REQUIRED_LINKS = (
    "docs/paper_draft.md",
    "docs/results_summary.md",
    "docs/submission_package.md",
    "docs/reproducibility_checklist.md",
    "docs/paired_effect_limitations_audit.md",
)


def build_artifact_guide_sequence_audit(path: Path = DEFAULT_ARTIFACT_GUIDE) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    review_path = _extract_section(text, "## Fifteen-Minute Core Path", "## Extended Evidence Path")
    numbers = _step_numbers(review_path)
    expected = list(range(1, len(numbers) + 1))
    duplicate_numbers = sorted({number for number in numbers if numbers.count(number) > 1})
    missing_numbers = [number for number in expected if number not in numbers]
    out_of_order = numbers != expected
    missing_links = [link for link in REQUIRED_LINKS if link not in review_path]
    problems = []
    if out_of_order:
        problems.append("review path numbering is not contiguous from 1")
    if duplicate_numbers:
        problems.append("review path contains duplicate step numbers")
    if missing_numbers:
        problems.append("review path skips step numbers")
    if missing_links:
        problems.append("review path is missing required links")

    return {
        "summary": {
            "ready": not problems,
            "step_count": len(numbers),
            "first_step": numbers[0] if numbers else None,
            "last_step": numbers[-1] if numbers else None,
            "expected_last_step": expected[-1] if expected else None,
            "duplicate_numbers": duplicate_numbers,
            "missing_numbers": missing_numbers,
            "missing_links": missing_links,
            "artifact_guide": str(path),
        },
        "steps": numbers,
        "expected": expected,
        "required_links": list(REQUIRED_LINKS),
        "problems": problems,
    }


def render_artifact_guide_sequence_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Artifact Guide Sequence Audit",
        "",
        "This generated audit checks that the reviewer-facing artifact-guide path has contiguous numbering and includes the required evidence links.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Step count: {summary['step_count']}",
        f"- First step: {summary['first_step']}",
        f"- Last step: {summary['last_step']}",
        f"- Expected last step: {summary['expected_last_step']}",
        f"- Duplicate numbers: {_fmt_list(summary['duplicate_numbers'])}",
        f"- Missing numbers: {_fmt_list(summary['missing_numbers'])}",
        f"- Missing required links: {_fmt_list(summary['missing_links'])}",
        f"- Artifact guide: `{summary['artifact_guide']}`",
        "",
        "## Required Links",
        "",
        "| Link | Present |",
        "| --- | --- |",
    ]
    missing_links = set(summary["missing_links"])
    for link in result["required_links"]:
        lines.append(f"| `{link}` | {'no' if link in missing_links else 'yes'} |")
    lines.extend([
        "",
        "Interpretation: the artifact guide is reviewer-ready only if the numbered path is mechanically navigable and points to the core evidence chain.",
    ])
    return "\n".join(lines) + "\n"


def _extract_section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end]


def _step_numbers(text: str) -> list[int]:
    numbers = []
    for line in text.splitlines():
        match = STEP_PATTERN.match(line)
        if match:
            numbers.append(int(match.group(1)))
    return numbers


def _fmt_list(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "-"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit artifact-guide review-path numbering.")
    parser.add_argument("--artifact-guide", type=Path, default=DEFAULT_ARTIFACT_GUIDE)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_artifact_guide_sequence_audit(args.artifact_guide)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_artifact_guide_sequence_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
