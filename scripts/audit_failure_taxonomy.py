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
    return {
        "summary": {
            "ready": ready,
            "target_label_count": len(TARGET_LABELS),
            "covered_label_count": sum(1 for row in rows if row["covered"]),
            "fixture_micro_f1": (fixture_eval.get("summary") or {}).get("micro_f1", 0),
            "real_pilot_positive_label_count": sum(1 for row in rows if row["evidence_tier"] == "real-pilot-positive"),
            "ablation_positive_label_count": sum(1 for row in rows if row["evidence_tier"] == "ablation-positive"),
            "fixture_only_label_count": sum(1 for row in rows if row["evidence_tier"] == "fixture-only"),
            "taxonomy_path": str(taxonomy_path),
            "paper_draft_path": str(paper_draft_path),
            "fixture_eval_path": str(fixture_eval_path),
        },
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
