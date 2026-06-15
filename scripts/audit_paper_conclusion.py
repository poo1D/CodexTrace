from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")


def build_paper_conclusion_audit(paper_draft_path: Path = DEFAULT_PAPER_DRAFT) -> dict[str, Any]:
    text = paper_draft_path.read_text(encoding="utf-8")
    conclusion = _extract_conclusion(text)
    normalized = _normalize(conclusion)
    checks = [
        _check("first_class_traces", "traces can be used as first-class evaluation objects", conclusion),
        _check("waste_reduction", "harness-level waste reductions", conclusion),
        _check("ordinary_verification_boundary", "should not claim an ordinary verification-rate lift", conclusion),
        _check("hidden_semantic_boundary", "hidden semantic edge failures can escape process-only rules", conclusion),
        _check("semantic_oracles", "strong task-level oracles", conclusion),
        _check("next_step_repeat_hard30", "repeat the hard30 collection", conclusion),
        _check("headline_link", "docs/headline_results.md", conclusion),
        _check("thesis_revision_link", "docs/thesis_revision_decision.md", conclusion),
        _check("claim_framing_link", "docs/submission_package.md", conclusion),
        _check("paired_effect_limitations_link", "docs/paired_effect_limitations_audit.md", conclusion),
        _check("detector_evidence_tiers_boundary", "detector evidence tiers distinguish real-pilot positives from ablation and fixture coverage", conclusion),
        _check("hard_tier_test_writing_boundary", "hard-tier `test_writing` remains seed-only", conclusion),
        _check("nullable_timing_boundary", "nullable timing metrics exclude undefined runs rather than converting them to zero", conclusion),
        _check("metric_coverage_link", "docs/metric_coverage_audit.md", conclusion),
    ]
    overclaim_checks = [
        {
            "id": "no_verification_lift_overclaim",
            "passed": "intervention increases verification rate" not in normalized
            and "intervention raises verification rate" not in normalized
            and "ordinary verification-rate lift is supported" not in normalized,
            "expected": "no ordinary verification-rate lift conclusion claim",
        },
        {
            "id": "no_hidden_correctness_overclaim",
            "passed": "trace-based diagnosis predicts hidden correctness" not in normalized
            and "process-only rules catch hidden semantic" not in normalized,
            "expected": "no trace-only hidden-correctness conclusion claim",
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
            "conclusion_word_count": len(conclusion.split()),
            "paper_draft": str(paper_draft_path),
        },
        "checks": all_checks,
        "missing": missing,
        "conclusion": conclusion,
    }


def render_paper_conclusion_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Paper Conclusion Audit",
        "",
        "This generated audit checks that the paper conclusion restates the evidence-backed boundary result without reintroducing unsupported claims.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Checks passed: {summary['passed']} / {summary['checks']}",
        f"- Missing checks: {summary['missing']}",
        f"- Conclusion words: {summary['conclusion_word_count']}",
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
        "Interpretation: the conclusion is ready only if it closes on trace diagnosis, waste reduction, the ordinary-verification boundary, and hidden-semantic limitations without turning unsupported claims into findings.",
    ])
    return "\n".join(lines) + "\n"


def _extract_conclusion(text: str) -> str:
    start_marker = "## 11. Conclusion"
    end_marker = "## References"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start + len(start_marker):end].strip()


def _check(check_id: str, phrase: str, text: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": _normalize(phrase) in _normalize(text),
        "expected": phrase,
    }


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper conclusion against current CodexTrace evidence boundaries.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_paper_conclusion_audit(args.paper_draft)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_paper_conclusion_audit_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
