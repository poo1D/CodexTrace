from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_DIAGNOSE = Path("codex_trace/diagnose.py")
DEFAULT_RESEARCH = Path("codex_trace/research.py")
DEFAULT_TAXONOMY = Path("docs/failure_taxonomy.md")
DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_DETECTOR_AUDIT = Path("docs/detector_evaluation_audit.json")


RULES = (
    {
        "label": "verification_gap",
        "finding_code": "verification_gap",
        "implementation_markers": ("_post_edit_verification_count", "post_edit_verification_commands"),
        "alias_marker": '"verification_gap": "verification_gap"',
        "scope": "direct",
    },
    {
        "label": "unrecovered_tool_error",
        "finding_code": "command_failure_unhandled",
        "implementation_markers": ("_unresolved_failed_commands", "_similar_command"),
        "alias_marker": '"command_failure_unhandled": "unrecovered_tool_error"',
        "scope": "direct",
    },
    {
        "label": "repetitive_exploration",
        "finding_code": "repeated_search_or_read",
        "implementation_markers": ("_repeated_searches", "_repeated_tool_call_volume"),
        "alias_marker": '"repeated_search_or_read": "repetitive_exploration"',
        "scope": "direct",
    },
    {
        "label": "context_drift",
        "finding_code": "long_context_no_progress",
        "implementation_markers": ("_long_context_no_progress", "input_tokens"),
        "alias_marker": '"long_context_no_progress": "context_drift"',
        "scope": "v1_proxy",
    },
    {
        "label": "premature_completion",
        "finding_code": "premature_completion",
        "implementation_markers": ("_premature_completion_events", "completion_words"),
        "alias_marker": '"premature_completion": "premature_completion"',
        "scope": "direct",
    },
    {
        "label": "sandbox_permission_deadlock",
        "finding_code": "sandbox_or_permission_block",
        "implementation_markers": ("SANDBOX_WORDS", "_sandbox_events"),
        "alias_marker": '"sandbox_or_permission_block": "sandbox_permission_deadlock"',
        "scope": "direct",
    },
)


def build_rule_implementation_audit(
    diagnose_path: Path = DEFAULT_DIAGNOSE,
    research_path: Path = DEFAULT_RESEARCH,
    taxonomy_path: Path = DEFAULT_TAXONOMY,
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    detector_audit_path: Path = DEFAULT_DETECTOR_AUDIT,
) -> dict[str, Any]:
    diagnose_text = diagnose_path.read_text(encoding="utf-8")
    research_text = research_path.read_text(encoding="utf-8")
    taxonomy_text = taxonomy_path.read_text(encoding="utf-8")
    paper_text = paper_draft_path.read_text(encoding="utf-8")
    evidence_tiers = _read_evidence_tiers(detector_audit_path)

    rows = []
    for rule in RULES:
        markers = list(rule["implementation_markers"])
        tier = evidence_tiers.get(rule["label"], {})
        row = {
            "label": rule["label"],
            "finding_code": rule["finding_code"],
            "scope": rule["scope"],
            "controlled_fixture": bool(tier.get("controlled_fixture")),
            "real_pilot_tp": int(tier.get("real_pilot_tp", 0) or 0),
            "ablation_tp": int(tier.get("ablation_tp", 0) or 0),
            "evidence_tier": tier.get("evidence_tier", "missing"),
            "finding_code_present": f'code="{rule["finding_code"]}"' in diagnose_text,
            "implementation_markers_present": all(marker in diagnose_text for marker in markers),
            "alias_present": rule["alias_marker"] in research_text,
            "taxonomy_present": rule["label"] in taxonomy_text,
            "paper_present": rule["label"] in paper_text,
            "evidence_tier_present": rule["label"] in evidence_tiers,
            "markers": markers,
        }
        row["covered"] = (
            row["finding_code_present"]
            and row["implementation_markers_present"]
            and row["alias_present"]
            and row["taxonomy_present"]
            and row["paper_present"]
            and row["evidence_tier_present"]
        )
        rows.append(row)

    context_row = next(row for row in rows if row["label"] == "context_drift")
    context_proxy_disclosed = (
        context_row["scope"] == "v1_proxy"
        and "Trace signal for v1" in taxonomy_text
        and "Future signal" in taxonomy_text
        and "compare task keywords" in taxonomy_text
    )
    return {
        "summary": {
            "ready": all(row["covered"] for row in rows) and context_proxy_disclosed,
            "rule_count": len(rows),
            "covered_rule_count": sum(1 for row in rows if row["covered"]),
            "context_proxy_disclosed": context_proxy_disclosed,
            "real_pilot_positive_rule_count": sum(1 for row in rows if row["evidence_tier"] == "real-pilot-positive"),
            "ablation_positive_rule_count": sum(1 for row in rows if row["evidence_tier"] == "ablation-positive"),
            "fixture_only_rule_count": sum(1 for row in rows if row["evidence_tier"] == "fixture-only"),
            "diagnose_path": str(diagnose_path),
            "research_path": str(research_path),
            "taxonomy_path": str(taxonomy_path),
            "paper_draft_path": str(paper_draft_path),
            "detector_audit_path": str(detector_audit_path),
        },
        "rules": rows,
    }


def _read_evidence_tiers(detector_audit_path: Path) -> dict[str, dict[str, Any]]:
    detector_audit = json.loads(detector_audit_path.read_text(encoding="utf-8"))
    return {
        row["label"]: row
        for row in detector_audit.get("process_label_evidence_tiers", [])
    }


def render_rule_implementation_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Rule Implementation Audit",
        "",
        "This generated audit checks that each paper-facing taxonomy label is backed by an implemented diagnosis rule and a paper-label alias.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Rules covered: {summary['covered_rule_count']} / {summary['rule_count']}",
        f"- Context drift v1 proxy disclosed: {'yes' if summary['context_proxy_disclosed'] else 'no'}",
        f"- Real-pilot-positive rules: {summary['real_pilot_positive_rule_count']} / {summary['rule_count']}",
        f"- Ablation-positive rules: {summary['ablation_positive_rule_count']} / {summary['rule_count']}",
        f"- Fixture-only rules: {summary['fixture_only_rule_count']} / {summary['rule_count']}",
        f"- Diagnosis source: `{summary['diagnose_path']}`",
        f"- Label alias source: `{summary['research_path']}`",
        f"- Detector evidence source: `{summary['detector_audit_path']}`",
        "",
        "## Rule Coverage",
        "",
        "| Label | Finding code | Scope | Evidence tier | Real TP | Ablation TP | Code | Markers | Alias | Docs | Covered |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in result["rules"]:
        docs = row["taxonomy_present"] and row["paper_present"]
        lines.append(
            f"| `{row['label']}` | `{row['finding_code']}` | `{row['scope']}` | "
            f"`{row['evidence_tier']}` | {row['real_pilot_tp']} | {row['ablation_tp']} | "
            f"{_yes(row['finding_code_present'])} | {_yes(row['implementation_markers_present'])} | "
            f"{_yes(row['alias_present'])} | {_yes(docs)} | {_yes(row['covered'])} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit checks implementation coverage, label mapping, and the detector evidence tier for each rule. It also records that `context_drift` is a v1 proxy based on high context with weak progress, not a full semantic task-keyword drift detector.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_rule_implementation_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit implemented diagnosis rules against paper taxonomy labels.")
    parser.add_argument("--diagnose", type=Path, default=DEFAULT_DIAGNOSE)
    parser.add_argument("--research", type=Path, default=DEFAULT_RESEARCH)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--detector-audit", type=Path, default=DEFAULT_DETECTOR_AUDIT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_rule_implementation_audit(
        args.diagnose,
        args.research,
        args.taxonomy,
        args.paper_draft,
        args.detector_audit,
    )
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_rule_implementation_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
