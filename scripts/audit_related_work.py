from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_RELATED_WORK = Path("docs/related_work.md")
DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")

REQUIRED_TOPICS = (
    {
        "topic": "software_engineering_benchmarks",
        "related_work_phrases": ("SWE-bench", "real GitHub issues"),
        "paper_phrases": ("SWE-bench", "Final tests or issue-level success"),
    },
    {
        "topic": "multi_turn_degradation",
        "related_work_phrases": ("LLMs Get Lost In Multi-Turn Conversation", "fail to recover"),
        "paper_phrases": ("LLMs Get Lost In Multi-Turn Conversation", "early assumptions shape later answers"),
    },
    {
        "topic": "coding_agents_and_interfaces",
        "related_work_phrases": ("SWE-agent", "OpenHands", "Codex CLI"),
        "paper_phrases": ("SWE-agent", "OpenHands", "OpenAI Codex CLI"),
    },
    {
        "topic": "tool_use_agents_and_feedback",
        "related_work_phrases": ("ReAct", "Toolformer", "Reflexion"),
        "paper_phrases": ("ReAct", "Toolformer", "Reflexion"),
    },
    {
        "topic": "general_agent_evaluation",
        "related_work_phrases": ("AgentBench", "multi-turn settings"),
        "paper_phrases": ("AgentBench", "multi-turn agents"),
    },
    {
        "topic": "program_repair_waste",
        "related_work_phrases": ("RepairAgent", "token budgets"),
        "paper_phrases": ("RepairAgent", "token budgets"),
    },
    {
        "topic": "trace_based_agent_diagnosis",
        "related_work_phrases": ("AgentRx", "execution trajectories"),
        "paper_phrases": ("AgentRx", "execution trajectories"),
    },
    {
        "topic": "codextrace_positioning",
        "related_work_phrases": ("Positioning Matrix", "CodexTrace difference"),
        "paper_phrases": ("Table 1 summarizes the positioning", "CodexTrace difference"),
    },
)


def build_related_work_audit(
    related_work_path: Path = DEFAULT_RELATED_WORK,
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
) -> dict[str, Any]:
    related_work_text = related_work_path.read_text(encoding="utf-8")
    paper_text = paper_draft_path.read_text(encoding="utf-8")

    rows = []
    for topic in REQUIRED_TOPICS:
        related_missing = [
            phrase for phrase in topic["related_work_phrases"]
            if phrase not in related_work_text
        ]
        paper_missing = [
            phrase for phrase in topic["paper_phrases"]
            if phrase not in paper_text
        ]
        rows.append({
            "topic": topic["topic"],
            "related_work_phrases": list(topic["related_work_phrases"]),
            "paper_phrases": list(topic["paper_phrases"]),
            "related_work_covered": not related_missing,
            "paper_draft_covered": not paper_missing,
            "related_work_missing": related_missing,
            "paper_draft_missing": paper_missing,
            "covered": not related_missing and not paper_missing,
        })

    return {
        "summary": {
            "ready": all(row["covered"] for row in rows),
            "topic_count": len(rows),
            "covered_topic_count": sum(1 for row in rows if row["covered"]),
            "related_work_path": str(related_work_path),
            "paper_draft_path": str(paper_draft_path),
        },
        "topics": rows,
    }


def render_related_work_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Related Work Coverage Audit",
        "",
        "This generated audit checks that the compact related-work notes and paper draft cover the positioning axes needed for the CodexTrace paper.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Topics covered: {summary['covered_topic_count']} / {summary['topic_count']}",
        f"- Related-work notes: `{summary['related_work_path']}`",
        f"- Paper draft: `{summary['paper_draft_path']}`",
        "",
        "## Topic Coverage",
        "",
        "| Topic | Related-work notes | Paper draft | Covered |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["topics"]:
        related_status = "yes" if row["related_work_covered"] else "missing: " + ", ".join(row["related_work_missing"])
        paper_status = "yes" if row["paper_draft_covered"] else "missing: " + ", ".join(row["paper_draft_missing"])
        lines.append(
            f"| {row['topic']} | {related_status} | {paper_status} | {'yes' if row['covered'] else 'no'} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit checks coverage and positioning alignment only. It is not a full literature review or citation-quality assessment.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_related_work_audit_markdown(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit related-work coverage for the CodexTrace paper.")
    parser.add_argument("--related-work", type=Path, default=DEFAULT_RELATED_WORK)
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_related_work_audit(args.related_work, args.paper_draft)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_related_work_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
