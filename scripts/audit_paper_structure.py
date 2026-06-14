from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")

REQUIRED_SECTIONS = (
    {
        "id": "title_and_abstract",
        "phrases": (
            "# When Coding Agents Get Lost",
            "## Abstract",
            "verification-rate-lift claim",
            "hidden semantic edge-case failures",
        ),
    },
    {
        "id": "introduction_and_rqs",
        "phrases": (
            "## 1. Introduction",
            "RQ1: What observable failure modes appear",
            "RQ2: Can these failure modes be detected",
            "RQ3: Do simple harness interventions improve success or reduce waste",
            "RQ4: Which trace signals explain observable process failures",
        ),
    },
    {
        "id": "related_work",
        "phrases": (
            "## 2. Related Work",
            "SWE-bench",
            "SWE-agent",
            "AgentRx",
            "| Work line | Primary question | Typical evidence | CodexTrace difference |",
        ),
    },
    {
        "id": "problem_and_taxonomy",
        "phrases": (
            "## 3. Problem Definition",
            "## 4. Failure Taxonomy",
            "`verification_gap`",
            "`sandbox_permission_deadlock`",
            "`hidden_semantic_edge_case`",
        ),
    },
    {
        "id": "method_and_schema",
        "phrases": (
            "## 5. Method: CodexTrace",
            "JSONL event parser",
            "phase segmentation",
            "| Schema object | Fields | Purpose |",
            "| Taxonomy label | Implementation finding | Detector signal |",
        ),
    },
    {
        "id": "benchmark_and_measurement",
        "phrases": (
            "## 6. Benchmark",
            "| Tier | Tasks | Runs | Baseline | Intervention | Outcome oracle | Primary use |",
            "### Measurement",
            "`time_to_first_test`",
            "`failure_score`",
        ),
    },
    {
        "id": "rq_results",
        "phrases": (
            "## 7. Results",
            "### RQ1: Failure Taxonomy Distribution",
            "### RQ2: Detector Agreement",
            "### RQ3: Baseline vs Intervention",
            "### RQ4: Trace Signals By Outcome",
        ),
    },
    {
        "id": "boundary_result_framing",
        "phrases": (
            "verification-lift-v2 ordinary retest",
            "no-verify ablation",
            "not ordinary-baseline evidence",
            "negative result for the verification-rate-lift claim",
            "process-only trace rules cannot detect every correctness failure",
        ),
    },
    {
        "id": "analysis_and_limitations",
        "phrases": (
            "## 8. Analysis",
            "## 9. Threats To Validity",
            "pilot-scale benchmark",
            "rule-based and intentionally interpretable, but incomplete",
            "Larger repository tasks, repeated trials",
        ),
    },
    {
        "id": "artifact_and_conclusion",
        "phrases": (
            "## 10. Artifact Availability",
            "docs/artifact_guide.md",
            "docs/submission_package.md",
            "## 11. Conclusion",
            "strong task-level oracles",
        ),
    },
    {
        "id": "references",
        "phrases": (
            "## References",
            "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
            "AgentRx: Diagnosing AI Agent Failures from Execution Trajectories",
        ),
    },
)


def build_paper_structure_audit(paper_draft_path: Path = DEFAULT_PAPER_DRAFT) -> dict[str, Any]:
    text = paper_draft_path.read_text(encoding="utf-8")
    normalized_text = _normalize(text)
    rows = []
    for section in REQUIRED_SECTIONS:
        missing = [
            phrase for phrase in section["phrases"]
            if _normalize(phrase) not in normalized_text
        ]
        rows.append({
            "id": section["id"],
            "required_phrases": list(section["phrases"]),
            "missing": missing,
            "covered": not missing,
        })
    return {
        "summary": {
            "ready": all(row["covered"] for row in rows),
            "section_count": len(rows),
            "covered_section_count": sum(1 for row in rows if row["covered"]),
            "paper_draft_path": str(paper_draft_path),
        },
        "sections": rows,
    }


def _normalize(text: str) -> str:
    return " ".join(text.split())


def render_paper_structure_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Paper Structure Audit",
        "",
        "This generated audit checks that the paper draft covers the required sections, RQ result blocks, and boundary-result framing for the CodexTrace thesis.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Sections covered: {summary['covered_section_count']} / {summary['section_count']}",
        f"- Paper draft: `{summary['paper_draft_path']}`",
        "",
        "## Section Coverage",
        "",
        "| Section | Covered | Missing phrases |",
        "| --- | --- | --- |",
    ]
    for row in result["sections"]:
        missing = ", ".join(f"`{phrase}`" for phrase in row["missing"]) or "-"
        lines.append(f"| {row['id']} | {'yes' if row['covered'] else 'no'} | {missing} |")
    lines.extend([
        "",
        "Interpretation: this audit verifies structural and claim-boundary coverage. It does not judge prose quality, novelty, or venue fit.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_paper_structure_audit_markdown(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the CodexTrace paper draft structure.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_paper_structure_audit(args.paper_draft)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_paper_structure_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
