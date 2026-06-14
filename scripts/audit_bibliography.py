from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_RELATED_WORK = Path("docs/related_work.md")

REQUIRED_REFERENCES = (
    {
        "id": "swe_bench",
        "title": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
        "url": "https://arxiv.org/abs/2310.06770",
    },
    {
        "id": "swe_agent",
        "title": "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering",
        "url": "https://arxiv.org/abs/2405.15793",
    },
    {
        "id": "openhands",
        "title": "OpenHands: An Open Platform for AI Software Developers as Generalist Agents",
        "url": "https://arxiv.org/abs/2407.16741",
    },
    {
        "id": "codex_cli_help",
        "title": "OpenAI Codex CLI - Getting Started",
        "url": "https://help.openai.com/en/articles/11096431",
    },
    {
        "id": "codex_cli_repo",
        "title": "openai/codex GitHub repository",
        "url": "https://github.com/openai/codex",
    },
    {
        "id": "agentbench",
        "title": "AgentBench: Evaluating LLMs as Agents",
        "url": "https://arxiv.org/abs/2308.03688",
    },
    {
        "id": "repairagent",
        "title": "RepairAgent: An Autonomous, LLM-Based Agent for Program Repair",
        "url": "https://arxiv.org/abs/2403.17134",
    },
    {
        "id": "agentrx",
        "title": "AgentRx: Diagnosing AI Agent Failures from Execution Trajectories",
        "url": "https://www.microsoft.com/en-us/research/publication/agentrx-diagnosing-ai-agent-failures-from-execution-trajectories/",
    },
)


def build_bibliography_audit(
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    related_work_path: Path = DEFAULT_RELATED_WORK,
) -> dict[str, Any]:
    paper_text = paper_draft_path.read_text(encoding="utf-8")
    related_text = related_work_path.read_text(encoding="utf-8")

    rows = []
    for ref in REQUIRED_REFERENCES:
        paper_has_title = ref["title"] in paper_text
        paper_has_url = ref["url"] in paper_text
        related_has_title = ref["title"] in related_text
        related_has_url = ref["url"] in related_text
        rows.append({
            "id": ref["id"],
            "title": ref["title"],
            "url": ref["url"],
            "paper_has_title": paper_has_title,
            "paper_has_url": paper_has_url,
            "related_work_has_title": related_has_title,
            "related_work_has_url": related_has_url,
            "covered": paper_has_title and paper_has_url and related_has_title and related_has_url,
        })

    paper_has_references = "## References" in paper_text
    return {
        "summary": {
            "ready": paper_has_references and all(row["covered"] for row in rows),
            "paper_has_references": paper_has_references,
            "reference_count": len(rows),
            "covered_reference_count": sum(1 for row in rows if row["covered"]),
            "paper_draft_path": str(paper_draft_path),
            "related_work_path": str(related_work_path),
        },
        "references": rows,
    }


def render_bibliography_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Bibliography Audit",
        "",
        "This generated audit checks that the paper draft has a References section and that each related-work source is visible in both the draft and the compact related-work notes.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Paper has References section: {'yes' if summary['paper_has_references'] else 'no'}",
        f"- References covered: {summary['covered_reference_count']} / {summary['reference_count']}",
        f"- Paper draft: `{summary['paper_draft_path']}`",
        f"- Related-work notes: `{summary['related_work_path']}`",
        "",
        "## Reference Coverage",
        "",
        "| Reference | Paper title | Paper URL | Notes title | Notes URL | Covered |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["references"]:
        lines.append(
            "| `{id}` | {paper_title} | {paper_url} | {notes_title} | {notes_url} | {covered} |".format(
                id=row["id"],
                paper_title="yes" if row["paper_has_title"] else "no",
                paper_url="yes" if row["paper_has_url"] else "no",
                notes_title="yes" if row["related_work_has_title"] else "no",
                notes_url="yes" if row["related_work_has_url"] else "no",
                covered="yes" if row["covered"] else "no",
            )
        )
    lines.extend([
        "",
        "Interpretation: this audit checks source discoverability only. It does not replace venue-specific citation formatting or external bibliographic verification.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_bibliography_audit_markdown(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit bibliography coverage for the CodexTrace paper draft.")
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--related-work", type=Path, default=DEFAULT_RELATED_WORK)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_bibliography_audit(args.paper_draft, args.related_work)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_bibliography_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
