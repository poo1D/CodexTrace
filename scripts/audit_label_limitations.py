from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_LABEL_PROVENANCE = Path("docs/label_provenance_audit.md")


def build_label_limitations_audit(
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    label_provenance_path: Path = DEFAULT_LABEL_PROVENANCE,
) -> dict[str, Any]:
    paper = paper_draft_path.read_text(encoding="utf-8")
    provenance = label_provenance_path.read_text(encoding="utf-8")
    limitations = _extract_section(paper, "## 9. Threats To Validity", "## 10. Artifact Availability")

    checks = [
        _check("hidden_grader_basis", "hidden grader outcomes and qualitative inspection", limitations),
        _check("single_artifact_caveat", "single-artifact diagnostic labels", limitations),
        _check("no_inter_annotator_claim", "not inter-annotator-agreement evidence", limitations),
        _check("richer_labels_needed", "richer process failure labels", limitations),
        _check("provenance_ready", "Ready: yes", provenance),
        _check("provenance_failure_notes", "Failure rows with notes: 30 / 30", provenance),
        _check("provenance_inter_annotator_caveat", "does not prove inter-annotator agreement", provenance),
    ]
    overclaim_checks = [
        {
            "id": "no_gold_label_claim",
            "passed": "gold labels" not in _normalize(limitations)
            and "ground-truth process labels" not in _normalize(limitations)
            and "inter-annotator agreement" not in _normalize(limitations).replace("not inter-annotator-agreement evidence", ""),
            "expected": "no gold-label or inter-annotator-agreement claim",
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
            "label_provenance": str(label_provenance_path),
        },
        "checks": all_checks,
        "missing": missing,
    }


def render_label_limitations_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Label Limitations Audit",
        "",
        "This generated audit checks that manual-label provenance is paired with safe paper limitations.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Checks passed: {summary['passed']} / {summary['checks']}",
        f"- Missing checks: {summary['missing']}",
        f"- Paper draft: `{summary['paper_draft']}`",
        f"- Label provenance: `{summary['label_provenance']}`",
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
        "Interpretation: this audit guards against treating single-artifact manual diagnostic labels as broad gold-standard process labels or inter-annotator-agreement evidence.",
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
    parser = argparse.ArgumentParser(description="Audit manual-label limitations in the paper draft.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--label-provenance", type=Path, default=DEFAULT_LABEL_PROVENANCE)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_label_limitations_audit(args.paper_draft, args.label_provenance)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_label_limitations_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
