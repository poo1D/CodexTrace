from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")


def build_paper_contribution_audit(paper_draft_path: Path = DEFAULT_PAPER_DRAFT) -> dict[str, Any]:
    text = paper_draft_path.read_text(encoding="utf-8")
    normalized = _normalize(text)
    checks = [
        _check("contribution_section", "Our contributions are:", text),
        _check("taxonomy_contribution", "six-label process-failure taxonomy", text),
        _check("benchmark_contribution", "Codex JSONL trace benchmark", text),
        _check("codextrace_contribution", "offline parser and diagnosis engine", text),
        _check("empirical_boundary_contribution", "boundary-result empirical analysis", text),
        _check("waste_reduction", "tool-call and token waste", text),
        _check("verification_negative", "does not support an ordinary verification-rate lift", text),
        _check("semantic_oracle_boundary", "strong task-level oracles", text),
        {
            "id": "no_verification_lift_contribution",
            "passed": "contribution: verification-rate lift" not in normalized
            and "contribution: harness intervention increases verification" not in normalized
            and "we show harness intervention increases verification rate" not in normalized,
            "expected": "no contribution claims ordinary verification-rate lift",
        },
    ]
    missing = [row for row in checks if not row["passed"]]
    return {
        "summary": {
            "ready": not missing,
            "checks": len(checks),
            "passed": sum(1 for row in checks if row["passed"]),
            "missing": len(missing),
            "paper_draft": str(paper_draft_path),
        },
        "checks": checks,
        "missing": missing,
    }


def render_paper_contribution_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Paper Contribution Audit",
        "",
        "This generated audit checks that the paper's contribution claims match the current evidence-backed boundary-result thesis.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Checks passed: {summary['passed']} / {summary['checks']}",
        f"- Missing checks: {summary['missing']}",
        f"- Paper draft: `{summary['paper_draft']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Expected |",
        "| --- | --- | --- |",
    ]
    for row in result["checks"]:
        lines.append(f"| `{row['id']}` | {'pass' if row['passed'] else 'fail'} | {row['expected']} |")
    lines.extend([
        "",
        "Interpretation: contribution claims are ready only if they state taxonomy, benchmark, CodexTrace, and boundary-result empirical contributions without presenting ordinary verification-rate lift as a finding.",
    ])
    return "\n".join(lines) + "\n"


def _check(check_id: str, phrase: str, text: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": _normalize(phrase) in _normalize(text),
        "expected": phrase,
    }


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper contribution claims against current CodexTrace evidence boundaries.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_paper_contribution_audit(args.paper_draft)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_paper_contribution_audit_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
