from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_PAIRED_EFFECTS = Path("docs/paired_effects_audit.md")


def build_paired_effect_limitations_audit(
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    paired_effects_path: Path = DEFAULT_PAIRED_EFFECTS,
) -> dict[str, Any]:
    paper = paper_draft_path.read_text(encoding="utf-8")
    paired_effects = paired_effects_path.read_text(encoding="utf-8")
    limitations = _extract_section(paper, "## 9. Threats To Validity", "## 10. Artifact Availability")

    checks = [
        _check("paired_audit_ready", "Ready: yes", paired_effects),
        _check("hard30_paired_tasks", "Hard30 paired tasks: 30", paired_effects),
        _check("hard30_repeated_delta", "Hard30 repeated tool-call delta: -3.733", paired_effects),
        _check("hard30_token_delta", "Hard30 token-usage delta: -98.7k", paired_effects),
        _check("bootstrap_interval_table", "95% bootstrap CI", paired_effects),
        _check("sign_test_table", "Sign p", paired_effects),
        _check("paired_audit_population_caveat", "not population-level significance claims", paired_effects),
        _check("paper_pilot_evidence", "pilot evidence", limitations),
        _check("paper_stable_population_caveat", "stable population estimate", limitations),
        _check("paper_repeated_trials_needed", "repeated trials", limitations),
        _check("paper_paired_audit_reference", "docs/paired_effects_audit.md", paper),
    ]
    overclaim_checks = [
        {
            "id": "no_statistically_significant_population_effect",
            "passed": "statistically significant population effect" not in _normalize(paper),
            "expected": "no statistically significant population effect overclaim",
        },
        {
            "id": "no_proves_general_effect",
            "passed": "proves general" not in _normalize(paper),
            "expected": "no proves-general-effect overclaim",
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
            "paper_draft": str(paper_draft_path),
            "paired_effects": str(paired_effects_path),
        },
        "checks": all_checks,
        "missing": missing,
    }


def render_paired_effect_limitations_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Paired Effect Limitations Audit",
        "",
        "This generated audit checks that task-paired RQ3 effect-size evidence is paired with pilot-scale and population-claim limitations.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Checks passed: {summary['passed']} / {summary['checks']}",
        f"- Missing checks: {summary['missing']}",
        f"- Paper draft: `{summary['paper_draft']}`",
        f"- Paired effects audit: `{summary['paired_effects']}`",
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
        "Interpretation: the paired-effect evidence supports a current-sample RQ3 waste-reduction claim, while the paper must keep repeated trials and population-level significance claims out of the headline.",
    ])
    return "\n".join(lines) + "\n"


def _extract_section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end]


def _check(check_id: str, phrase: str, text: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": _normalize(phrase) in _normalize(text),
        "expected": phrase,
    }


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paired-effect limitations in the paper draft.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--paired-effects", type=Path, default=DEFAULT_PAIRED_EFFECTS)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_paired_effect_limitations_audit(args.paper_draft, args.paired_effects)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_paired_effect_limitations_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
