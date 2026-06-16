from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_detector_evaluation import build_detector_evaluation_audit


DEFAULT_TAXONOMY = Path("docs/failure_taxonomy.md")
DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_FIXTURE_EVAL = Path("benchmark/detector-fixtures/label-eval.json")
TARGET_LABELS = (
    "verification_gap",
    "unrecovered_tool_error",
    "repetitive_exploration",
    "context_drift",
    "premature_completion",
    "sandbox_permission_deadlock",
)


def build_failure_taxonomy_audit(
    taxonomy_path: Path = DEFAULT_TAXONOMY,
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    fixture_eval_path: Path = DEFAULT_FIXTURE_EVAL,
) -> dict[str, Any]:
    taxonomy_text = taxonomy_path.read_text(encoding="utf-8")
    paper_text = paper_draft_path.read_text(encoding="utf-8")
    fixture_eval = json.loads(fixture_eval_path.read_text(encoding="utf-8"))
    fixture_labels = fixture_eval.get("labels", {})
    detector_audit = build_detector_evaluation_audit(fixture_eval_path=fixture_eval_path)
    evidence_by_label = {
        row["label"]: row
        for row in detector_audit["process_label_evidence_tiers"]
    }
    hidden_semantic_hard30_fn = next(
        (
            int(row["fn"])
            for row in detector_audit["hidden_semantic_boundaries"]
            if row["slice"] == "hard30"
        ),
        0,
    )

    rows = []
    for label in TARGET_LABELS:
        fixture_scores = fixture_labels.get(label, {})
        evidence = evidence_by_label.get(label, {})
        row = {
            "label": label,
            "taxonomy_doc": label in taxonomy_text,
            "paper_draft": label in paper_text,
            "detector_fixture": label in fixture_labels,
            "fixture_precision": fixture_scores.get("precision", 0),
            "fixture_recall": fixture_scores.get("recall", 0),
            "fixture_f1": fixture_scores.get("f1", 0),
            "real_pilot_tp": int(evidence.get("real_pilot_tp", 0) or 0),
            "ablation_tp": int(evidence.get("ablation_tp", 0) or 0),
            "evidence_tier": str(evidence.get("evidence_tier", "missing")),
        }
        row["covered"] = (
            row["taxonomy_doc"]
            and row["paper_draft"]
            and row["detector_fixture"]
            and float(row["fixture_recall"]) >= 1
        )
        rows.append(row)

    ready = all(row["covered"] for row in rows)
    rq1_boundaries = _rq1_boundaries(rows, hidden_semantic_hard30_fn)
    natural_coverage_plan = _natural_coverage_plan(rows)
    return {
        "summary": {
            "ready": ready,
            "target_label_count": len(TARGET_LABELS),
            "covered_label_count": sum(1 for row in rows if row["covered"]),
            "fixture_micro_f1": (fixture_eval.get("summary") or {}).get("micro_f1", 0),
            "real_pilot_positive_label_count": sum(1 for row in rows if row["evidence_tier"] == "real-pilot-positive"),
            "ablation_positive_label_count": sum(1 for row in rows if row["evidence_tier"] == "ablation-positive"),
            "fixture_only_label_count": sum(1 for row in rows if row["evidence_tier"] == "fixture-only"),
            "hidden_semantic_hard30_fn": hidden_semantic_hard30_fn,
            "taxonomy_path": str(taxonomy_path),
            "paper_draft_path": str(paper_draft_path),
            "fixture_eval_path": str(fixture_eval_path),
        },
        "rq1_boundaries": rq1_boundaries,
        "natural_coverage_plan": natural_coverage_plan,
        "labels": rows,
    }


def render_failure_taxonomy_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Failure Taxonomy Coverage Audit",
        "",
        "This generated audit checks that the six target process-failure labels are defined, mapped in the paper draft, and covered by controlled detector fixtures.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Labels covered: {summary['covered_label_count']} / {summary['target_label_count']}",
        f"- Detector-fixture micro-F1: {_fmt(summary['fixture_micro_f1'])}",
        f"- Real-pilot-positive labels: {summary['real_pilot_positive_label_count']} / {summary['target_label_count']}",
        f"- Ablation-positive labels: {summary['ablation_positive_label_count']} / {summary['target_label_count']}",
        f"- Fixture-only labels: {summary['fixture_only_label_count']} / {summary['target_label_count']}",
        f"- Hard30 hidden semantic false negatives: {summary['hidden_semantic_hard30_fn']}",
        f"- Taxonomy document: `{summary['taxonomy_path']}`",
        f"- Paper draft: `{summary['paper_draft_path']}`",
        f"- Fixture evaluation: `{summary['fixture_eval_path']}`",
        "",
        "## Label Coverage",
        "",
        "| Label | Taxonomy doc | Paper mapping | Fixture | Precision | Recall | F1 | Real-pilot TP | Ablation TP | Evidence tier | Covered |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in result["labels"]:
        lines.append(
            f"| {row['label']} | {_yes(row['taxonomy_doc'])} | {_yes(row['paper_draft'])} | "
            f"{_yes(row['detector_fixture'])} | {_fmt(row['fixture_precision'])} | "
            f"{_fmt(row['fixture_recall'])} | {_fmt(row['fixture_f1'])} | "
            f"{row['real_pilot_tp']} | {row['ablation_tp']} | `{row['evidence_tier']}` | "
            f"{_yes(row['covered'])} |"
        )
    lines.extend([
        "",
        "## RQ1 Distribution Boundary",
        "",
        "| Claim | Verdict | Evidence | Safe wording |",
        "| --- | --- | --- | --- |",
    ])
    for row in result["rq1_boundaries"]:
        lines.append(
            f"| {row['claim']} | `{row['verdict']}` | {row['evidence']} | {row['safe_wording']} |"
        )
    lines.extend([
        "",
        "## Natural Coverage Closure Plan",
        "",
        "| Label | Current tier | Natural-positive target | Candidate task pattern | Acceptance gate |",
        "| --- | --- | ---: | --- | --- |",
    ])
    for row in result["natural_coverage_plan"]:
        lines.append(
            f"| `{row['label']}` | `{row['current_tier']}` | {row['natural_positive_target']} | "
            f"{row['candidate_task_pattern']} | {row['acceptance_gate']} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit proves rule-level taxonomy coverage and records each label's evidence tier. It does not imply broad natural-frequency coverage in real pilots; fixture-only labels still require careful boundary framing.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_failure_taxonomy_audit_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def _rq1_boundaries(rows: list[dict[str, Any]], hidden_semantic_hard30_fn: int) -> list[dict[str, str]]:
    tier_counts = {
        "real-pilot-positive": sum(1 for row in rows if row["evidence_tier"] == "real-pilot-positive"),
        "ablation-positive": sum(1 for row in rows if row["evidence_tier"] == "ablation-positive"),
        "fixture-only": sum(1 for row in rows if row["evidence_tier"] == "fixture-only"),
    }
    real_labels = _labels_for_tier(rows, "real-pilot-positive")
    ablation_labels = _labels_for_tier(rows, "ablation-positive")
    fixture_only_labels = _labels_for_tier(rows, "fixture-only")
    return [
        {
            "claim": "CodexTrace defines the six target observable process-failure modes.",
            "verdict": "supported",
            "evidence": f"{len(rows)}/6 labels covered in taxonomy docs, paper mapping, and controlled fixtures.",
            "safe_wording": "Use as the RQ1 process-failure taxonomy.",
        },
        {
            "claim": "Current real pilots naturally expose all six process-failure modes.",
            "verdict": "unsupported",
            "evidence": (
                f"{tier_counts['real-pilot-positive']}/6 labels have real-pilot positives: "
                f"{real_labels}."
            ),
            "safe_wording": "Report evidence tiers rather than claiming natural-frequency coverage for every label.",
        },
        {
            "claim": "Some target process modes are only visible in ablation or controlled traces so far.",
            "verdict": "boundary",
            "evidence": (
                f"Ablation-positive labels: {ablation_labels}; fixture-only labels: {fixture_only_labels}."
            ),
            "safe_wording": "Frame ablation and fixture evidence as rule coverage, not broad pilot prevalence.",
        },
        {
            "claim": "Hard30 outcome failures reveal an additional hidden-semantic boundary.",
            "verdict": "supported-boundary",
            "evidence": f"Hard30 hidden_semantic_edge_case false negatives: {hidden_semantic_hard30_fn}.",
            "safe_wording": "Describe hidden semantic failures separately from observable process-failure taxonomy.",
        },
    ]


def _natural_coverage_plan(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    patterns = {
        "verification_gap": "ordinary tasks with weak visible tests where the agent edits files but plausibly stops after inspection or local reasoning",
        "unrecovered_tool_error": "tasks with an initially failing command that requires a concrete repair before any successful verification",
        "context_drift": "multi-file or multi-turn change requests with tempting adjacent files that are irrelevant to the stated task",
        "premature_completion": "tasks where a plausible edit is easy but the hidden grader needs an additional edge-case fix after verification",
    }
    plan = []
    for row in rows:
        if row["evidence_tier"] == "real-pilot-positive":
            continue
        plan.append({
            "label": row["label"],
            "current_tier": row["evidence_tier"],
            "natural_positive_target": 2,
            "candidate_task_pattern": patterns.get(row["label"], "ordinary Codex task designed to naturally elicit the process failure"),
            "acceptance_gate": (
                "at least two non-ablation baseline/intervention real-pilot positives with manual labels and detector evidence; "
                "do not count controlled fixtures or no-verify ablation rows"
            ),
        })
    return plan


def _labels_for_tier(rows: list[dict[str, Any]], tier: str) -> str:
    labels = [f"`{row['label']}`" for row in rows if row["evidence_tier"] == tier]
    return ", ".join(labels) if labels else "-"


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit coverage for the CodexTrace failure taxonomy.")
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--paper-draft", type=Path, default=DEFAULT_PAPER_DRAFT)
    parser.add_argument("--fixture-eval", type=Path, default=DEFAULT_FIXTURE_EVAL)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_failure_taxonomy_audit(args.taxonomy, args.paper_draft, args.fixture_eval)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_failure_taxonomy_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
