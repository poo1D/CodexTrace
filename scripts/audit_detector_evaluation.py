from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FIXTURE_EVAL = Path("benchmark/detector-fixtures/label-eval.json")
DEFAULT_HARD30_EVAL = Path("benchmark/hard/pilot/hard30-real/label-eval.json")
DEFAULT_FULL30_PROCESS_EVAL = Path("benchmark/pilot/full30-real/process-label-eval.json")
DEFAULT_PROCESS_STRESS_EVAL = Path("benchmark/process-stress/pilot/full-real/label-eval.json")
DEFAULT_VERIFICATION_LIFT_EVAL = Path("benchmark/verification-lift/pilot/full-real/label-eval.json")
DEFAULT_VERIFICATION_ABLATION_EVAL = Path("benchmark/verification-ablation/pilot/full-real/label-eval.json")


TARGET_PROCESS_LABELS = (
    "verification_gap",
    "unrecovered_tool_error",
    "repetitive_exploration",
    "context_drift",
    "premature_completion",
    "sandbox_permission_deadlock",
)


def build_detector_evaluation_audit(
    fixture_eval_path: Path = DEFAULT_FIXTURE_EVAL,
    hard30_eval_path: Path = DEFAULT_HARD30_EVAL,
    full30_process_eval_path: Path = DEFAULT_FULL30_PROCESS_EVAL,
    process_stress_eval_path: Path = DEFAULT_PROCESS_STRESS_EVAL,
    verification_lift_eval_path: Path = DEFAULT_VERIFICATION_LIFT_EVAL,
    verification_ablation_eval_path: Path = DEFAULT_VERIFICATION_ABLATION_EVAL,
) -> dict[str, Any]:
    fixtures = _read_json(fixture_eval_path)
    hard30 = _read_json(hard30_eval_path)
    full30 = _read_json(full30_process_eval_path)
    process_stress = _read_json(process_stress_eval_path)
    verification_lift = _read_json(verification_lift_eval_path)
    verification_ablation = _read_json(verification_ablation_eval_path)

    fixture_labels = fixtures["labels"]
    hard30_labels = hard30["labels"]
    full30_labels = full30["labels"]
    process_stress_labels = process_stress["labels"]
    verification_lift_labels = verification_lift["labels"]
    verification_ablation_labels = verification_ablation["labels"]

    controlled_labels_covered = sum(1 for label in TARGET_PROCESS_LABELS if label in fixture_labels)
    hidden_fn_total = (
        _metric(hard30_labels, "hidden_semantic_edge_case", "fn")
        + _metric(process_stress_labels, "hidden_semantic_edge_case", "fn")
        + _metric(verification_lift_labels, "hidden_semantic_edge_case", "fn")
        + _metric(verification_ablation_labels, "hidden_semantic_edge_case", "fn")
    )
    observable_positive_rows = [
        {
            "slice": "hard30",
            "label": "repetitive_exploration",
            **_scores(hard30_labels, "repetitive_exploration"),
        },
        {
            "slice": "full30_process",
            "label": "sandbox_permission_deadlock",
            **_scores(full30_labels, "sandbox_permission_deadlock"),
        },
        {
            "slice": "verification_ablation",
            "label": "verification_gap",
            **_scores(verification_ablation_labels, "verification_gap"),
        },
        {
            "slice": "verification_ablation",
            "label": "premature_completion",
            **_scores(verification_ablation_labels, "premature_completion"),
        },
    ]
    evidence_tiers = []
    for label in TARGET_PROCESS_LABELS:
        real_pilot_tp = (
            _metric(hard30_labels, label, "tp")
            + _metric(full30_labels, label, "tp")
            + _metric(process_stress_labels, label, "tp")
            + _metric(verification_lift_labels, label, "tp")
        )
        ablation_tp = _metric(verification_ablation_labels, label, "tp")
        tier = "fixture-only"
        if real_pilot_tp > 0:
            tier = "real-pilot-positive"
        elif ablation_tp > 0:
            tier = "ablation-positive"
        evidence_tiers.append({
            "label": label,
            "controlled_fixture": label in fixture_labels,
            "real_pilot_tp": real_pilot_tp,
            "ablation_tp": ablation_tp,
            "evidence_tier": tier,
        })
    boundary_rows = [
        {
            "slice": "hard30",
            "label": "hidden_semantic_edge_case",
            **_scores(hard30_labels, "hidden_semantic_edge_case"),
        },
        {
            "slice": "process_stress",
            "label": "hidden_semantic_edge_case",
            **_scores(process_stress_labels, "hidden_semantic_edge_case"),
        },
        {
            "slice": "verification_lift",
            "label": "hidden_semantic_edge_case",
            **_scores(verification_lift_labels, "hidden_semantic_edge_case"),
        },
        {
            "slice": "verification_ablation",
            "label": "hidden_semantic_edge_case",
            **_scores(verification_ablation_labels, "hidden_semantic_edge_case"),
        },
    ]
    ready = (
        controlled_labels_covered == len(TARGET_PROCESS_LABELS)
        and float(fixtures["summary"]["micro_f1"]) == 1.0
        and _metric(hard30_labels, "repetitive_exploration", "tp") == 4
        and _metric(full30_labels, "sandbox_permission_deadlock", "tp") == 1
        and _metric(verification_ablation_labels, "verification_gap", "tp") == 4
        and _metric(verification_ablation_labels, "premature_completion", "tp") == 3
        and _metric(hard30_labels, "hidden_semantic_edge_case", "fn") == 30
        and hidden_fn_total == 36
        and sum(1 for row in evidence_tiers if row["evidence_tier"] == "real-pilot-positive") == 2
        and sum(1 for row in evidence_tiers if row["evidence_tier"] == "ablation-positive") == 2
        and sum(1 for row in evidence_tiers if row["evidence_tier"] == "fixture-only") == 2
    )
    claim_boundaries = _claim_boundaries(
        controlled_labels_covered=controlled_labels_covered,
        target_label_count=len(TARGET_PROCESS_LABELS),
        controlled_micro_f1=float(fixtures["summary"]["micro_f1"]),
        real_positive_label_count=sum(1 for row in evidence_tiers if row["evidence_tier"] == "real-pilot-positive"),
        ablation_positive_label_count=sum(1 for row in evidence_tiers if row["evidence_tier"] == "ablation-positive"),
        fixture_only_label_count=sum(1 for row in evidence_tiers if row["evidence_tier"] == "fixture-only"),
        hidden_fn_total=hidden_fn_total,
        hard30_hidden_fn=_metric(hard30_labels, "hidden_semantic_edge_case", "fn"),
    )
    return {
        "summary": {
            "ready": ready,
            "controlled_label_count": controlled_labels_covered,
            "target_label_count": len(TARGET_PROCESS_LABELS),
            "controlled_micro_f1": fixtures["summary"]["micro_f1"],
            "hard30_repetitive_tp": _metric(hard30_labels, "repetitive_exploration", "tp"),
            "full30_sandbox_tp": _metric(full30_labels, "sandbox_permission_deadlock", "tp"),
            "ablation_verification_gap_tp": _metric(verification_ablation_labels, "verification_gap", "tp"),
            "ablation_premature_completion_tp": _metric(verification_ablation_labels, "premature_completion", "tp"),
            "hidden_semantic_fn_total": hidden_fn_total,
            "real_pilot_positive_label_count": sum(1 for row in evidence_tiers if row["evidence_tier"] == "real-pilot-positive"),
            "ablation_positive_label_count": sum(1 for row in evidence_tiers if row["evidence_tier"] == "ablation-positive"),
            "fixture_only_label_count": sum(1 for row in evidence_tiers if row["evidence_tier"] == "fixture-only"),
        },
        "claim_boundaries": claim_boundaries,
        "controlled_fixture_labels": [
            {"label": label, **_scores(fixture_labels, label)}
            for label in TARGET_PROCESS_LABELS
        ],
        "process_label_evidence_tiers": evidence_tiers,
        "observable_process_positives": observable_positive_rows,
        "hidden_semantic_boundaries": boundary_rows,
        "false_positive_boundaries": [
            {"slice": "full30_process", "label": "repetitive_exploration", **_scores(full30_labels, "repetitive_exploration")},
        ],
        "sources": {
            "fixture_eval": str(fixture_eval_path),
            "hard30_eval": str(hard30_eval_path),
            "full30_process_eval": str(full30_process_eval_path),
            "process_stress_eval": str(process_stress_eval_path),
            "verification_lift_eval": str(verification_lift_eval_path),
            "verification_ablation_eval": str(verification_ablation_eval_path),
        },
    }


def render_detector_evaluation_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Detector Evaluation Audit",
        "",
        "This generated audit consolidates the detector precision/recall evidence used for RQ2.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Controlled process labels covered: {summary['controlled_label_count']} / {summary['target_label_count']}",
        f"- Controlled detector micro-F1: {_fmt(summary['controlled_micro_f1'])}",
        f"- Hard30 repetitive_exploration TP: {summary['hard30_repetitive_tp']}",
        f"- Full30 sandbox_permission_deadlock TP: {summary['full30_sandbox_tp']}",
        f"- Verification-ablation verification_gap TP: {summary['ablation_verification_gap_tp']}",
        f"- Verification-ablation premature_completion TP: {summary['ablation_premature_completion_tp']}",
        f"- Hidden semantic false negatives: {summary['hidden_semantic_fn_total']}",
        f"- Real-pilot-positive process labels: {summary['real_pilot_positive_label_count']} / {summary['target_label_count']}",
        f"- Ablation-positive process labels: {summary['ablation_positive_label_count']} / {summary['target_label_count']}",
        f"- Fixture-only process labels: {summary['fixture_only_label_count']} / {summary['target_label_count']}",
        "",
        "## Controlled Fixture Coverage",
        "",
        "| Label | TP | FP | FN | Precision | Recall | F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["controlled_fixture_labels"]:
        lines.append(_label_row(row))
    lines.extend([
        "",
        "## Evidence Tier By Process Label",
        "",
        "| Label | Controlled fixture | Real-pilot TP | Ablation TP | Evidence tier |",
        "| --- | --- | ---: | ---: | --- |",
    ])
    for row in result["process_label_evidence_tiers"]:
        lines.append(
            f"| `{row['label']}` | {'yes' if row['controlled_fixture'] else 'no'} | "
            f"{row['real_pilot_tp']} | {row['ablation_tp']} | `{row['evidence_tier']}` |"
        )
    lines.extend([
        "",
        "## Claim Boundary Verdicts",
        "",
        "| Claim | Verdict | Evidence | Safe wording |",
        "| --- | --- | --- | --- |",
    ])
    for row in result["claim_boundaries"]:
        lines.append(
            f"| {row['claim']} | `{row['verdict']}` | {row['evidence']} | {row['safe_wording']} |"
        )
    lines.extend([
        "",
        "## Observable Process Positives",
        "",
        "| Slice | Label | TP | FP | FN | Precision | Recall | F1 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in result["observable_process_positives"]:
        lines.append(_slice_label_row(row))
    lines.extend([
        "",
        "## Hidden Semantic Boundary",
        "",
        "| Slice | Label | TP | FP | FN | Precision | Recall | F1 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in result["hidden_semantic_boundaries"]:
        lines.append(_slice_label_row(row))
    lines.extend([
        "",
        "## False Positive Boundary",
        "",
        "| Slice | Label | TP | FP | FN | Precision | Recall | F1 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in result["false_positive_boundaries"]:
        lines.append(_slice_label_row(row))
    lines.extend([
        "",
        "Interpretation: deterministic process rules cover the six-label taxonomy on controlled fixtures and detect several observed process-positive slices, but they do not detect hidden semantic correctness failures.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_detector_evaluation_markdown(result), encoding="utf-8")


def _scores(labels: dict[str, Any], label: str) -> dict[str, Any]:
    row = labels.get(label, {})
    return {
        "tp": int(row.get("tp", 0) or 0),
        "fp": int(row.get("fp", 0) or 0),
        "fn": int(row.get("fn", 0) or 0),
        "precision": float(row.get("precision", 0) or 0),
        "recall": float(row.get("recall", 0) or 0),
        "f1": float(row.get("f1", 0) or 0),
    }


def _claim_boundaries(
    *,
    controlled_labels_covered: int,
    target_label_count: int,
    controlled_micro_f1: float,
    real_positive_label_count: int,
    ablation_positive_label_count: int,
    fixture_only_label_count: int,
    hidden_fn_total: int,
    hard30_hidden_fn: int,
) -> list[dict[str, str]]:
    return [
        {
            "claim": "Rules cover the six process-failure labels on controlled traces.",
            "verdict": "supported",
            "evidence": (
                f"{controlled_labels_covered}/{target_label_count} controlled labels, "
                f"micro-F1={_fmt(controlled_micro_f1)}."
            ),
            "safe_wording": "Use as rule-level taxonomy coverage, not natural-frequency evidence.",
        },
        {
            "claim": "Rules detect observed process-positive slices in real or ablation pilots.",
            "verdict": "supported-with-boundary",
            "evidence": (
                f"{real_positive_label_count} real-pilot-positive labels, "
                f"{ablation_positive_label_count} ablation-positive labels, "
                f"{fixture_only_label_count} fixture-only labels."
            ),
            "safe_wording": "Claim detection of reviewed observable process positives and report evidence tiers.",
        },
        {
            "claim": "Rules detect most real-world outcome failures.",
            "verdict": "unsupported",
            "evidence": (
                f"Hidden semantic false negatives total {hidden_fn_total}, including "
                f"{hard30_hidden_fn} hard30 false negatives."
            ),
            "safe_wording": "Do not claim majority real-world failure detection; keep the claim process-scoped.",
        },
        {
            "claim": "Rules detect hidden semantic correctness failures.",
            "verdict": "contradicted",
            "evidence": f"Hidden semantic false negatives total {hidden_fn_total}.",
            "safe_wording": "State that hidden semantic failures require stronger task oracles or semantic checks.",
        },
    ]


def _metric(labels: dict[str, Any], label: str, metric: str) -> int:
    return int(labels.get(label, {}).get(metric, 0) or 0)


def _label_row(row: dict[str, Any]) -> str:
    return (
        f"| `{row['label']}` | {row['tp']} | {row['fp']} | {row['fn']} | "
        f"{_fmt(row['precision'])} | {_fmt(row['recall'])} | {_fmt(row['f1'])} |"
    )


def _slice_label_row(row: dict[str, Any]) -> str:
    return (
        f"| `{row['slice']}` | `{row['label']}` | {row['tp']} | {row['fp']} | {row['fn']} | "
        f"{_fmt(row['precision'])} | {_fmt(row['recall'])} | {_fmt(row['f1'])} |"
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit detector evaluation evidence for RQ2.")
    parser.add_argument("--fixture-eval", type=Path, default=DEFAULT_FIXTURE_EVAL)
    parser.add_argument("--hard30-eval", type=Path, default=DEFAULT_HARD30_EVAL)
    parser.add_argument("--full30-process-eval", type=Path, default=DEFAULT_FULL30_PROCESS_EVAL)
    parser.add_argument("--process-stress-eval", type=Path, default=DEFAULT_PROCESS_STRESS_EVAL)
    parser.add_argument("--verification-lift-eval", type=Path, default=DEFAULT_VERIFICATION_LIFT_EVAL)
    parser.add_argument("--verification-ablation-eval", type=Path, default=DEFAULT_VERIFICATION_ABLATION_EVAL)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_detector_evaluation_audit(
        args.fixture_eval,
        args.hard30_eval,
        args.full30_process_eval,
        args.process_stress_eval,
        args.verification_lift_eval,
        args.verification_ablation_eval,
    )
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_detector_evaluation_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
