from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")


def build_paper_abstract_audit(paper_draft_path: Path = DEFAULT_PAPER_DRAFT) -> dict[str, Any]:
    text = paper_draft_path.read_text(encoding="utf-8")
    abstract = _extract_abstract(text)
    normalized = _normalize(abstract)
    checks = [
        _check("codextrace_system", "We introduce CodexTrace", abstract),
        _check("offline_parser", "offline parser and diagnosis engine", abstract),
        _check("seven_pilots", "seven real Codex benchmark pilots", abstract),
        _check("verification_negative", "do not support a verification-rate-lift claim", abstract),
        _check("full30_waste", "10.43 to 7.00", abstract),
        _check("full30_tokens", "218.7k to 184.8k", abstract),
        _check("hard30_success_flat", "success rate stays flat at 50%", abstract),
        _check("hard30_repeated_calls", "12.93 to 9.20", abstract),
        _check("hard30_tokens", "355.0k to 256.3k", abstract),
        _check("hard30_failure_score", "3.50 to 1.17", abstract),
        _check("hidden_semantic_boundary", "30 hidden semantic edge-case failures", abstract),
        _check("semantic_oracles", "strong semantic oracles", abstract),
        _check("process_failures", "observable process failures", abstract),
        _check("detector_evidence_tiers", "detector evidence tiers", abstract),
        _check("hard30_category_diagnosis", "hard30 category-level lost-task diagnosis", abstract),
        _check("harness_proxy_checks", "run-level harness proxy checks", abstract),
    ]
    overclaim_checks = [
        {
            "id": "no_unqualified_verification_lift",
            "passed": "intervention increases verification rate" not in normalized
            and "intervention improves verification rate" not in normalized
            and "intervention raises verification rate" not in normalized,
            "expected": "no unqualified verification-rate lift claim",
        },
        {
            "id": "no_hidden_correctness_claim",
            "passed": "trace-based diagnosis predicts hidden correctness" not in normalized
            and "process rules detect hidden semantic" not in normalized,
            "expected": "no trace-only hidden-correctness claim",
        },
    ]
    all_checks = checks + overclaim_checks
    missing = [row for row in all_checks if not row["passed"]]
    return {
        "summary": {
            "ready": not missing,
            "checks": len(all_checks),
            "passed": sum(1 for row in all_checks if row["passed"]),
            "missing": len(missing),
            "abstract_word_count": len(abstract.split()),
            "paper_draft": str(paper_draft_path),
        },
        "checks": all_checks,
        "missing": missing,
        "abstract": abstract,
    }


def render_paper_abstract_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Paper Abstract Audit",
        "",
        "This generated audit checks that the paper abstract states the current evidence-backed boundary-result thesis without overclaiming.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Checks passed: {summary['passed']} / {summary['checks']}",
        f"- Missing checks: {summary['missing']}",
        f"- Abstract words: {summary['abstract_word_count']}",
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
        "Interpretation: the abstract is ready only if it includes the supported waste-reduction and trace-boundary results while avoiding the unsupported ordinary verification-rate-lift claim.",
    ])
    return "\n".join(lines) + "\n"


def _extract_abstract(text: str) -> str:
    start_marker = "## Abstract"
    end_marker = "## 1. Introduction"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start + len(start_marker):end].strip()


def _check(check_id: str, phrase: str, abstract: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": _normalize(phrase) in _normalize(abstract),
        "expected": phrase,
    }


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper abstract against current CodexTrace evidence boundaries.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_paper_abstract_audit(args.paper_draft)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_paper_abstract_audit_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
