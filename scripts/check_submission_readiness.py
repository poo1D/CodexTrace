from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.finalize_hard30_pilot import preflight


DEFAULT_HARD30_SELECTION_DIR = Path("benchmark/hard/pilot/hard30-selection")
DEFAULT_HARD30_RUN_DIR = Path("benchmark/hard/pilot/hard30-real")
REQUIRED_HARD30_OUTPUTS = (
    "aggregate.json",
    "aggregate.md",
    "runs.csv",
    "paired-task-deltas.csv",
    "paired-task-summary.csv",
    "labels.jsonl",
    "paper-report.json",
    "paper-report.md",
    "paper-report-labeled.json",
    "paper-report-labeled.md",
    "label-eval.json",
    "label-eval.md",
)
VALID_FAILURE_TAGS = {
    "verification_gap",
    "unrecovered_tool_error",
    "repetitive_exploration",
    "context_drift",
    "premature_completion",
    "sandbox_permission_deadlock",
    "hidden_semantic_edge_case",
}


def check_exists(path: Path, description: str) -> dict[str, Any]:
    return {
        "name": description,
        "ok": path.exists(),
        "evidence": str(path),
    }


def check_hard30_selection(selection_dir: Path) -> dict[str, Any]:
    task_ids_path = selection_dir / "task_ids.txt"
    tasks_path = selection_dir / "tasks.jsonl"
    manifest_path = selection_dir / "manifest.json"
    if not task_ids_path.exists():
        return {"name": "hard30 selection", "ok": False, "evidence": str(task_ids_path), "detail": "missing task_ids.txt"}

    task_ids = [line.strip() for line in task_ids_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ok = len(task_ids) == 30 and len(set(task_ids)) == 30 and tasks_path.exists() and manifest_path.exists()
    detail = f"{len(task_ids)} selected task(s), {len(set(task_ids))} unique"
    return {"name": "hard30 selection", "ok": ok, "evidence": str(selection_dir), "detail": detail}


def check_hard30_real_runs(run_dir: Path, selection_dir: Path) -> dict[str, Any]:
    summary = preflight(run_dir, selection_dir)
    return {
        "name": "hard30 real runs",
        "ok": bool(summary["ok"]),
        "evidence": str(run_dir / "runs.jsonl"),
        "detail": f"{summary['run_records']} / {summary['expected_run_records']} run records",
        "preflight": summary,
    }


def check_hard30_outputs(run_dir: Path) -> dict[str, Any]:
    missing = [name for name in REQUIRED_HARD30_OUTPUTS if not (run_dir / name).exists()]
    return {
        "name": "hard30 finalized outputs",
        "ok": not missing,
        "evidence": str(run_dir),
        "missing": missing,
    }


def check_manual_labels(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "runs.jsonl"
    labels_path = run_dir / "manual-labels.jsonl"
    if not labels_path.exists():
        return {
            "name": "hard30 manual labels",
            "ok": False,
            "evidence": str(labels_path),
            "detail": "missing manual-labels.jsonl",
        }
    manifest_rows = []
    if manifest_path.exists():
        manifest_rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [json.loads(line) for line in labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest_by_key = {
        (str(row.get("task_id")), str(row.get("prompt_type"))): row
        for row in manifest_rows
    }
    label_by_key = {
        (str(row.get("task_id")), str(row.get("prompt_type"))): row
        for row in rows
    }
    missing_failure_labels = [
        f"{task_id}/{prompt_type}"
        for (task_id, prompt_type), row in sorted(manifest_by_key.items())
        if row.get("outcome") == "failure" and (task_id, prompt_type) not in label_by_key
    ]
    extra_labels = [
        f"{task_id}/{prompt_type}"
        for task_id, prompt_type in sorted(label_by_key)
        if manifest_by_key and (task_id, prompt_type) not in manifest_by_key
    ]
    outcome_mismatches = [
        f"{task_id}/{prompt_type}"
        for (task_id, prompt_type), row in sorted(label_by_key.items())
        if (task_id, prompt_type) in manifest_by_key
        and str(row.get("outcome", "")) != str(manifest_by_key[(task_id, prompt_type)].get("outcome", ""))
    ]
    unlabeled_failures = [
        f"{row.get('task_id')}/{row.get('prompt_type')}"
        for row in rows
        if row.get("outcome") == "failure" and not row.get("failure_tags")
    ]
    missing_notes = [
        f"{row.get('task_id')}/{row.get('prompt_type')}"
        for row in rows
        if row.get("outcome") == "failure" and not str(row.get("notes", "")).strip()
    ]
    unknown_tags = sorted({
        str(tag)
        for row in rows
        for tag in row.get("failure_tags", [])
        if tag not in VALID_FAILURE_TAGS
    })
    ok = not (
        missing_failure_labels
        or extra_labels
        or outcome_mismatches
        or unlabeled_failures
        or missing_notes
        or unknown_tags
    )
    return {
        "name": "hard30 manual labels",
        "ok": ok,
        "evidence": str(labels_path),
        "detail": f"{len(rows)} label row(s)",
        "missing_failure_labels": missing_failure_labels,
        "extra_labels": extra_labels,
        "outcome_mismatches": outcome_mismatches,
        "unlabeled_failures": unlabeled_failures,
        "missing_notes": missing_notes,
        "unknown_tags": unknown_tags,
    }


def check_hard30_report_content(run_dir: Path) -> dict[str, Any]:
    labeled_report_path = run_dir / "paper-report-labeled.json"
    label_eval_path = run_dir / "label-eval.json"
    problems = []
    paired_task_n = []
    detector_label_count = 0

    try:
        labeled_report = json.loads(labeled_report_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        labeled_report = {}
        problems.append(f"invalid labeled report: {error}")

    try:
        label_eval = json.loads(label_eval_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        label_eval = {}
        problems.append(f"invalid label eval: {error}")

    if labeled_report:
        detector_eval = labeled_report.get("detector_evaluation") or {}
        detector_label_count = int((detector_eval.get("summary") or {}).get("labels", 0) or 0)
        if detector_label_count <= 0:
            problems.append("paper-report-labeled.json has no detector labels")
        paired_summary = labeled_report.get("paired_task_summary") or {}
        for metric in ("success_delta", "verification_delta", "repeated_tool_call_delta", "token_usage_delta", "failure_score_delta"):
            n = int((paired_summary.get(metric) or {}).get("n", 0) or 0)
            paired_task_n.append(n)
            if n != 30:
                problems.append(f"{metric} paired n is {n}, expected 30")

    if label_eval:
        labels = label_eval.get("labels") or {}
        if not labels:
            problems.append("label-eval.json has no per-label scores")

    return {
        "name": "hard30 report content",
        "ok": not problems,
        "evidence": str(labeled_report_path),
        "detail": f"detector labels={detector_label_count}, paired n={sorted(set(paired_task_n)) if paired_task_n else []}",
        "problems": problems,
    }


def check_paper_draft_content(path: Path = Path("docs/paper_draft.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paper draft content",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paper draft"],
        }

    required_phrases = {
        "artifact availability section": "## 10. Artifact Availability",
        "related-work positioning matrix": "| Work line | Primary question | Typical evidence | CodexTrace difference |",
        "dataset construction table": "| Tier | Tasks | Runs | Baseline | Intervention | Outcome oracle | Primary use |",
        "trace schema table": "| Schema object | Fields | Purpose |",
        "paper schema mapping": "| Paper field | Implementation source | Notes |",
        "step event type field": "`Step.event_type`",
        "step tool name field": "`Step.tool_name`",
        "step file paths field": "`Step.file_paths`",
        "step failure tags field": "`Step.failure_tags`",
        "detector rule mapping": "| Taxonomy label | Implementation finding | Detector signal |",
        "measurement table": "| Metric | Measurement |",
        "metric coverage link": "docs/metric_coverage_audit.md",
        "benchmark trace artifact link": "docs/benchmark_trace_artifact.md",
        "label provenance audit link": "docs/label_provenance_audit.md",
        "label limitations audit link": "docs/label_limitations_audit.md",
        "limitations traceability audit link": "docs/limitations_traceability_audit.md",
        "verification saturation audit link": "docs/verification_saturation_audit.md",
        "paired effects audit link": "docs/paired_effects_audit.md",
        "demo audit link": "docs/demo_audit.md",
        "web artifact audit link": "docs/web_artifact_audit.md",
        "cli surface audit link": "docs/cli_surface_audit.md",
        "ci surface audit link": "docs/ci_surface_audit.md",
        "method pipeline audit link": "docs/method_pipeline_audit.md",
        "rq table consistency audit link": "docs/rq_table_consistency_audit.md",
        "paper conclusion audit link": "docs/paper_conclusion_audit.md",
        "schema field audit link": "docs/schema_field_audit.md",
        "parser event audit link": "docs/parser_event_coverage.md",
        "failure node audit link": "docs/failure_node_traceability.md",
        "contribution block": "Our contributions are:",
        "references section": "## References",
        "time-to-first-test definition": "`time_to_first_test`",
        "gpu-free method note": "No model training, fine-tuning, embedding index, or GPU inference is used",
        "process-vs-semantic limitation": "Trace diagnosis is less suited for proving semantic correctness",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paper draft content",
        "ok": not problems,
        "evidence": str(path),
        "detail": "artifact availability, related-work positioning, dataset table, schema/rule tables, GPU-free note, and semantic-limit caveat",
        "problems": problems,
    }


def check_paper_abstract_audit_content(path: Path = Path("docs/paper_abstract_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paper abstract audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paper abstract audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Checks passed: 18 / 18",
        "verification negative": "verification_negative",
        "hard30 waste": "hard30_repeated_calls",
        "hidden semantic boundary": "hidden_semantic_boundary",
        "semantic oracles": "semantic_oracles",
        "detector evidence tiers": "detector_evidence_tiers",
        "hard30 category diagnosis": "hard30_category_diagnosis",
        "harness proxy checks": "harness_proxy_checks",
        "no overclaim": "no_unqualified_verification_lift",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paper abstract audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper abstract covers supported boundary-result claims and avoids verification-rate overclaim",
        "problems": problems,
    }


def check_paper_contribution_audit_content(path: Path = Path("docs/paper_contribution_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paper contribution audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paper contribution audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Checks passed: 12 / 12",
        "taxonomy": "taxonomy_contribution",
        "benchmark": "benchmark_contribution",
        "codextrace": "codextrace_contribution",
        "empirical boundary": "empirical_boundary_contribution",
        "evidence tiers": "detector_evidence_tiers",
        "category diagnosis": "category_lost_task_diagnosis",
        "harness proxies": "harness_proxy_checks",
        "verification boundary": "no_verification_lift_contribution",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paper contribution audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper contribution claims match supported boundary-result evidence",
        "problems": problems,
    }


def check_paper_conclusion_audit_content(path: Path = Path("docs/paper_conclusion_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paper conclusion audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paper conclusion audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Checks passed: 16 / 16",
        "ordinary verification boundary": "ordinary_verification_boundary",
        "hidden semantic boundary": "hidden_semantic_boundary",
        "detector evidence tiers boundary": "detector_evidence_tiers_boundary",
        "hard-tier test writing boundary": "hard_tier_test_writing_boundary",
        "nullable timing boundary": "nullable_timing_boundary",
        "metric coverage link": "metric_coverage_link",
        "paired effect limitations": "paired_effect_limitations_link",
        "no verification overclaim": "no_verification_lift_overclaim",
        "no hidden correctness overclaim": "no_hidden_correctness_overclaim",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paper conclusion audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper conclusion restates boundary-result claims without unsupported findings",
        "problems": problems,
    }


def check_experiment_protocol_content(path: Path = Path("docs/experiment_protocol.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "experiment protocol content",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing experiment protocol"],
        }

    normalized = " ".join(text.lower().split())
    required_phrases = {
        "rq-to-evidence map": "## RQ-To-Evidence Map",
        "rq1 mapping": "| RQ1 failure modes |",
        "rq2 mapping": "| RQ2 trace-only detection |",
        "rq3 mapping": "| RQ3 intervention effect |",
        "rq4 mapping": "| RQ4 explanatory signals |",
        "verification boundary": "Ordinary and weak-baseline verification rates are saturated",
        "task diagnosis mapping": "docs/hard30_task_diagnosis.md",
        "task repair/regression evidence": "one intervention repair (`HARD-050`), one intervention regression",
        "average turn count metric": "avg_turn_count",
        "time-to-first average metrics": "avg_time_to_first_test",
        "metric coverage command": "scripts/audit_metric_coverage.py",
        "paired effects command": "scripts/audit_paired_effects.py",
    }
    for label, phrase in required_phrases.items():
        if " ".join(phrase.lower().split()) not in normalized:
            problems.append(f"missing {label}")

    return {
        "name": "experiment protocol content",
        "ok": not problems,
        "evidence": str(path),
        "detail": "RQ-to-evidence map with reproduction commands and current evidence boundaries",
        "problems": problems,
    }


def check_hard30_task_diagnosis_content(path: Path = Path("docs/hard30_task_diagnosis.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "hard30 task diagnosis",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing hard30 task diagnosis"],
        }

    required_phrases = {
        "tasks": "Tasks: 30",
        "double failures": "Both failed: 14",
        "repair": "Intervention repaired: 1",
        "regression": "Intervention regressed: 1",
        "token improved": "Token usage improved: 26/30",
        "repeated improved": "Repeated tool calls improved: 26/30",
        "category diagnosis": "Category-Level Diagnosis",
        "dependency friction": "| dependency_friction | 3 | 3 | 0 | 0 |",
        "repair task": "HARD-050",
        "regression task": "HARD-007",
        "interpretation": "dominated by hidden semantic double failures",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "hard30 task diagnosis",
        "ok": not problems,
        "evidence": str(path),
        "detail": "task and category-level hard30 diagnosis for losses, repairs, regressions, and waste deltas",
        "problems": problems,
    }


def check_submission_package_content(path: Path = Path("docs/submission_package.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "submission package map",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing submission package map"],
        }

    required_phrases = {
        "rq map": "## RQ-To-Evidence Map",
        "rq3 row": "| RQ3 | supported |",
        "required boundary": "ordinary verification-rate lift remains unsupported; no-verify lift is an ablation only",
        "unsupported claims": "## Unsupported Claims To Avoid",
        "verification overclaim guard": "Harness intervention increases verification rate.",
        "required reviewer files": "## Required Reviewer Files",
        "self reference": "docs/submission_package.md",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "submission package map",
        "ok": not problems,
        "evidence": str(path),
        "detail": "RQ-to-evidence map, unsupported-claim guard, required boundary, and reviewer file list",
        "problems": problems,
    }


def check_claim_text_guard_content(path: Path = Path("docs/claim_text_guard.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "claim text guard",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing claim text guard"],
        }

    required_phrases = {
        "status": "Status: pass",
        "file count": "Files checked: 7",
        "caveat count": "Required caveats checked: 7",
        "problem count": "Problems: 0",
        "artifact guide target": "docs/artifact_guide.md",
        "submission package target": "docs/submission_package.md",
        "no drift": "No unsupported-claim drift detected.",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "claim text guard",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper-facing entry points are checked for unsupported verification, semantic, and evidence-tier claim drift",
        "problems": problems,
    }


def check_headline_results_content(path: Path = Path("docs/headline_results.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "headline results table",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing headline results table"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "verification lift unsupported": "Ordinary verification-rate lift supported: no",
        "hard30 success": "hard30_success",
        "hard30 repeated calls": "hard30_repeated_tool_calls",
        "hard30 token usage": "hard30_token_usage",
        "v2 verification": "verification_lift_v2_verification",
        "ablation verification": "no_verify_ablation_verification",
        "not ordinary baseline": "not an ordinary baseline",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "headline results table",
        "ok": not problems,
        "evidence": str(path),
        "detail": "compact actual headline table with verification-lift boundary and no-verify ablation caveat",
        "problems": problems,
    }


def check_thesis_revision_decision_content(path: Path = Path("docs/thesis_revision_decision.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "thesis revision decision",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing thesis revision decision"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "decision": "Decision: revise_to_boundary_result_paper",
        "original thesis no": "Ready for original thesis: no",
        "boundary paper yes": "Ready for boundary-result paper: yes",
        "claim revision": "Claim revision required: yes",
        "verification lift unsupported": "Ordinary verification-rate lift supported: no",
        "drop finding": "drop_as_finding",
        "mechanism check": "keep_as_mechanism_check",
        "waste reduction": "waste_reduction",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "thesis revision decision",
        "ok": not problems,
        "evidence": str(path),
        "detail": "explicit decision to revise the original thesis into a boundary-result paper",
        "problems": problems,
    }


def check_validity_threats_content(path: Path = Path("docs/validity_threats.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "validity threats audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing validity threats audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Threats covered: 7 / 7",
        "internal validity": "internal_validity",
        "construct validity": "construct_validity",
        "external validity": "external_validity",
        "conclusion validity": "conclusion_validity",
        "detector validity": "detector_validity",
        "ablation validity": "ablation_validity",
        "reproducibility validity": "reproducibility_validity",
        "verification boundary": "Ordinary verification-rate lift supported: no",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "validity threats audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper validity threats are mapped to evidence, mitigations, and safe wording",
        "problems": problems,
    }


def check_limitations_traceability_audit_content(path: Path = Path("docs/limitations_traceability_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "limitations traceability audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing limitations traceability audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Threats covered: 7 / 7",
        "internal validity": "`internal_validity`",
        "construct validity": "`construct_validity`",
        "ablation validity": "`ablation_validity`",
        "venue caveat": "does not judge whether the prose is sufficient",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "limitations traceability audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper limitations carry validity-threat safe wording",
        "problems": problems,
    }


def check_expected_results_reconciliation_content(path: Path = Path("docs/expected_results_reconciliation.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "expected results reconciliation audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing expected results reconciliation audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "paper files clean": "Paper files clean: 5 / 5",
        "headline phrases": "Headline phrases present: 7 / 7",
        "ordinary lift unsupported": "Ordinary verification-rate lift supported: no",
        "expected sketch caveat": "aspirational expected-results table",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "expected results reconciliation audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper-facing files use stored headline evidence instead of the expected-results sketch",
        "problems": problems,
    }


def check_submission_readiness_plan_audit_content(
    path: Path = Path("docs/submission_readiness_plan_audit.md"),
) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "submission readiness plan audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing submission readiness plan audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Checks passed: 15 / 15",
        "boundary positioning": "submission-ready hard30 artifact",
        "remaining repeatability": "repeat a hard-tier subset to estimate variance",
        "remaining process positives": "collect more natural observable process-failure positives",
        "no original complete overclaim": "no original-goal-complete claim",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "submission readiness plan audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "stronger-submission plan preserves current readiness and remaining evidence gaps",
        "problems": problems,
    }


def check_paper_number_guard_content(path: Path = Path("docs/paper_number_guard.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paper number guard",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paper number guard"],
        }

    required_phrases = {
        "ok": "OK: yes",
        "missing count": "Missing snippets: 0",
        "full30 failure-score check": "full30 failure-score row",
        "hard10 token check": "hard10 token row",
        "verification lift v2 check": "verification-lift-v2 paragraph",
        "verification ablation check": "verification-ablation paragraph",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paper number guard",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper-draft numeric claims match stored aggregate artifacts",
        "problems": problems,
    }


def check_reviewer_path_audit_content(path: Path = Path("docs/reviewer_path_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "reviewer path audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing reviewer path audit"],
        }

    required_phrases = {
        "ok": "OK: yes",
        "missing everywhere": "Missing everywhere: 0",
        "guide coverage": "Missing from artifact guide required set: 0",
        "checklist coverage": "Missing from reproducibility checklist: 0",
        "core path structure": "Core path structure: ok",
        "core path steps": "Core path steps: 10",
        "path structure checks": "Path structure checks failed: 0",
        "entry boundary checks": "Entry boundary checks failed: 0",
        "entry boundary table": "## Entry Boundary Checks",
        "detector evidence tiers boundary": "detector evidence tiers separate real-pilot positives from ablation and fixture coverage",
        "hard-tier test writing boundary": "hard-tier `test_writing` coverage remains seed-only",
        "nullable timing boundary": "nullable timing metrics use present values only rather than converting missing events to zero",
        "required files table": "| Required file | Covered | Present in |",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "reviewer path audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "required reviewer files are discoverable from paper-facing entry points",
        "problems": problems,
    }


def check_artifact_guide_sequence_audit_content(
    path: Path = Path("docs/artifact_guide_sequence_audit.md"),
) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "artifact guide sequence audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing artifact guide sequence audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "step count": "Step count: 10",
        "last step": "Last step: 10",
        "expected last step": "Expected last step: 10",
        "no duplicate numbers": "Duplicate numbers: -",
        "no missing numbers": "Missing numbers: -",
        "required links": "docs/paired_effect_limitations_audit.md",
        "taxonomy evidence tiers": "failure-taxonomy coverage and evidence tiers",
        "tier labels": "real-pilot-positive, ablation-positive, or fixture-only",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "artifact guide sequence audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "artifact-guide core-path numbering is contiguous and includes core evidence links and taxonomy evidence-tier wording",
        "problems": problems,
    }


def check_metric_coverage_audit_content(path: Path = Path("docs/metric_coverage_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "metric coverage audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing metric coverage audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "manifest count": "Manifests checked: 7 / 7",
        "coverage count": "Metrics covered: 11 / 11",
        "coverage cells": "Coverage cells covered: 77 / 77",
        "nullable metrics": "Nullable metrics checked: 2",
        "nullable observations": "Nullable manifest cells with observations:",
        "nullable section": "## Nullable Metrics",
        "present-only semantics": "aggregate averages use present values only",
        "missing semantics": "missing values mean the trace did not expose",
        "time to first edit": "time_to_first_edit",
        "time to first test": "time_to_first_test",
        "turn count": "turn_count",
        "verification ablation manifest": "benchmark/verification-ablation/pilot/full-real/runs.jsonl",
        "summary key": "avg_time_to_first_test",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "metric coverage audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "all experiment-design metrics are checked across paper-facing run manifests, CSV, summary, and Markdown outputs",
        "problems": problems,
    }


def check_benchmark_trace_artifact_content(path: Path = Path("docs/benchmark_trace_artifact.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "benchmark trace artifact audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing benchmark trace artifact audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "task coverage": "Tasks covered: 30 / 30",
        "run coverage": "Run rows covered: 60 / 60",
        "paired tasks": "Paired baseline/intervention tasks: 30 / 30",
        "trace coverage": "Codex JSONL traces covered: 60 / 60",
        "parseable traces": "Parseable traces: 60 / 60",
        "diagnosable traces": "Diagnosable traces: 60 / 60",
        "trace sidecars": "Trace sidecar bundles: 60 / 60",
        "outcome coverage": "Outcome rows with grader results: 60 / 60",
        "label coverage": "Manual label rows: 60 / 60",
        "missing run keys": "Missing run keys: 0",
        "rerun caveat": "does not rerun Codex or hidden graders",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "benchmark trace artifact audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "hard30 task, run, parseable trace, sidecar, outcome, and manual-label records are paired and complete",
        "problems": problems,
    }


def check_label_provenance_audit_content(path: Path = Path("docs/label_provenance_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "label provenance audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing label provenance audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "template label rows": "Template label rows: 60 / 60",
        "manual label rows": "Manual label rows: 60 / 60",
        "failure labels": "Failure rows with labels: 30 / 30",
        "failure notes": "Failure rows with notes: 30 / 30",
        "field coverage": "Label fields covered: 8 / 8",
        "eval match": "Label-eval summary matches paper report: 5 / 5",
        "inter annotator caveat": "does not prove inter-annotator agreement",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "label provenance audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "label templates, manual labels, and evaluation summaries are provenance-consistent",
        "problems": problems,
    }


def check_label_limitations_audit_content(path: Path = Path("docs/label_limitations_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "label limitations audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing label limitations audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage": "Checks passed: 8 / 8",
        "single artifact caveat": "single_artifact_caveat",
        "inter annotator caveat": "no_inter_annotator_claim",
        "provenance caveat": "provenance_inter_annotator_caveat",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "label limitations audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "manual diagnostic labels are paired with paper limitations",
        "problems": problems,
    }


def check_verification_saturation_audit_content(path: Path = Path("docs/verification_saturation_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "verification saturation audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing verification saturation audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "saturated tiers": "Non-ablation tiers saturated: 6 / 6",
        "ordinary lift unsupported": "Ordinary verification-rate lift supported: no",
        "exact lift unsupported": "Ordinary exact success-check verification lift supported: no",
        "ablation positive": "No-verify ablation mechanism positive: yes",
        "mechanism boundary": "mechanism-only, not ordinary baseline",
        "claim closure caveat": "cannot close the ordinary-baseline claim",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "verification saturation audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "stored non-ablation pilots are verification-saturated; no-verify ablation is mechanism-only",
        "problems": problems,
    }


def check_paired_effects_audit_content(path: Path = Path("docs/paired_effects_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paired effects audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paired effects audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "study coverage": "Studies covered: 7 / 7",
        "hard30 paired tasks": "Hard30 paired tasks: 30",
        "repeated delta": "Hard30 repeated tool-call delta: -3.733",
        "token delta": "Hard30 token-usage delta: -98.7k",
        "verification delta": "Hard30 verification delta: 0",
        "bootstrap caveat": "not population-level significance claims",
        "sign test": "Sign p",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paired effects audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "task-paired effect sizes, bootstrap CIs, and sign tests support RQ3 waste deltas",
        "problems": problems,
    }


def check_paired_effect_limitations_audit_content(
    path: Path = Path("docs/paired_effect_limitations_audit.md"),
) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paired effect limitations audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paired effect limitations audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "checks passed": "Checks passed: 13 / 13",
        "population caveat": "not population-level significance claims",
        "pilot evidence": "pilot evidence",
        "stable population caveat": "stable population estimate",
        "overclaim guard": "no statistically significant population effect overclaim",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paired effect limitations audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "task-paired effect sizes are paired with pilot-scale and population-claim limitations",
        "problems": problems,
    }


def check_demo_audit_content(path: Path = Path("docs/demo_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "demo audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing demo audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "finding coverage": "Expected findings covered: 5 / 5",
        "event ids": "Findings with event IDs: 5 / 5",
        "json report": "`json_report` | yes",
        "markdown report": "`markdown_report` | yes",
        "sandbox finding": "`sandbox_or_permission_block` | yes",
        "web ui caveat": "does not start the optional Web UI",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "demo audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "offline demo script emits traceable JSON and Markdown diagnosis reports",
        "problems": problems,
    }


def check_web_artifact_audit_content(path: Path = Path("docs/web_artifact_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "web artifact audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing web artifact audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "event ids": "Findings with matching event IDs: 5 / 5",
        "report checks": "Report checks covered: 5 / 5",
        "source checks": "Source checks covered: 9 / 9",
        "fetch report": "`fetch_report` | yes",
        "highlight source": "`highlighted_class` | yes",
        "build script": "`vite_build_script` | yes",
        "install caveat": "does not install npm dependencies or start the Vite dev server",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "web artifact audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "committed Web fixture matches the current demo diagnosis and highlight path",
        "problems": problems,
    }


def check_cli_surface_audit_content(path: Path = Path("docs/cli_surface_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "cli surface audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing cli surface audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "command coverage": "CLI commands covered: 9 / 9",
        "subcommand coverage": "Parser subcommands present: 9 / 9",
        "doc coverage": "Documentation checks covered: 6 / 6",
        "diagnose": "`diagnose_json`",
        "aggregate": "`research_aggregate`",
        "summary": "`research_summary`",
        "dry run": "`research_run_dry`",
        "live collection caveat": "does not execute live Codex collection",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "cli surface audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "offline CLI entry points regenerate representative trace, diagnosis, and research artifacts",
        "problems": problems,
    }


def check_ci_surface_audit_content(path: Path = Path("docs/ci_surface_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "ci surface audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing ci surface audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "ci coverage": "CI checks covered: 10 / 10",
        "packaging coverage": "Packaging checks covered: 6 / 6",
        "makefile coverage": "Makefile checks covered: 3 / 3",
        "submission readiness": "`submission_readiness`",
        "web build": "`web_build`",
        "console script": "`console_script`",
        "actions caveat": "does not execute GitHub Actions itself",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "ci surface audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "CI, packaging, and local task declarations cover tests, readiness, and Web build gates",
        "problems": problems,
    }


def check_schema_field_audit_content(path: Path = Path("docs/schema_field_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "schema field audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing schema field audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "objective schema coverage": "Objective schema fields checked: 15 / 15",
        "run coverage": "Run fields covered: 4 / 4",
        "step coverage": "Step fields covered: 11 / 11",
        "run task id": "`Run.task_id`",
        "step timestamp": "`Step.timestamp`",
        "step token usage": "`Step.token_usage`",
        "step file paths": "`Step.file_paths`",
        "failure tags": "`Step.failure_tags`",
        "trace event": "TraceEvent",
        "run record": "RunRecord",
        "objective boundary": "not all objective fields are direct `TraceEvent` attributes",
        "trace-level boundary": "not always a per-step field",
        "representational mapping": "schema mapping is representational",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "schema field audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper-facing Run/Step schema fields map to parser, schema, and research outputs",
        "problems": problems,
    }


def check_parser_event_coverage_content(path: Path = Path("docs/parser_event_coverage.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "parser event coverage audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing parser event coverage audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "event kind coverage": "Event kinds covered: 11 / 11",
        "phase coverage": "Phases covered: 7 / 7",
        "source markers": "Parser source markers covered: 11 / 11",
        "mcp tool": "`mcp_tool`",
        "unknown event": "`unknown`",
        "usage check": "`usage_input_tokens` | yes",
        "file paths": "`file_paths` | yes",
        "future caveat": "does not claim compatibility with every future Codex JSONL variant",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "parser event coverage audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "JSONL parser event-kind and phase branches are covered by a synthetic trace audit",
        "problems": problems,
    }


def check_failure_node_traceability_content(path: Path = Path("docs/failure_node_traceability.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "failure node traceability audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing failure node traceability audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "expected findings": "Expected demo findings present: 5 / 5",
        "finding event ids": "Findings with event IDs: 5 / 5",
        "json event ids": "JSON findings with event IDs: 5 / 5",
        "markdown event ids": "Markdown Event IDs lines: 5 / 5",
        "benchmark traces": "Benchmark traces checked: 60",
        "benchmark event ids": "Benchmark findings with event IDs: 4 / 4",
        "benchmark missing event ids": "Benchmark findings missing event IDs: 0",
        "highlighted nodes": "Highlighted event nodes:",
        "web highlight": "`web_highlight_class` | yes",
        "repeated search": "`repeated_search_or_read`",
        "boundary caveat": "does not claim that hidden semantic failures have visible failure nodes",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "failure node traceability audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "diagnosis findings carry event IDs through JSON, Markdown, Web UI highlight paths, and hard30 benchmark process findings",
        "problems": problems,
    }


def check_rq4_signal_audit_content(path: Path = Path("docs/rq4_signal_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "rq4 signal audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing rq4 signal audit"],
        }

    required_phrases = {
        "ready": "Ready for boundary-style RQ4 claim: yes",
        "fixture labels": "Detector-fixture labels with top signals: 6",
        "hidden semantic boundary": "Hidden Semantic Boundary",
        "verification boundary": "Hard30 hidden semantic verification delta: +0.00",
        "unresolved error boundary": "Hard30 hidden semantic unresolved-error delta: +0.00",
        "repetitive exploration": "Hard30 Repetitive Exploration",
        "sandbox permission": "Full30 Sandbox/Permission",
        "recover phase": "phase_recover_events",
        "expected signal checks": "Expected label-signal checks passed: 6 / 6",
        "expected signal table": "Expected Label-Signal Checks",
        "verification gap signal": "verification_gap | failure_score, phase_edit_events, time_to_first_test",
        "boundary interpretation": "hidden semantic failures can look procedurally clean",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "rq4 signal audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "trace signals explain observable process positives and the hidden-semantic boundary",
        "problems": problems,
    }


def check_detector_evaluation_audit_content(path: Path = Path("docs/detector_evaluation_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "detector evaluation audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing detector evaluation audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "controlled coverage": "Controlled process labels covered: 6 / 6",
        "controlled f1": "Controlled detector micro-F1: 1",
        "hard30 repetitive": "Hard30 repetitive_exploration TP: 4",
        "full30 sandbox": "Full30 sandbox_permission_deadlock TP: 1",
        "ablation verification": "Verification-ablation verification_gap TP: 4",
        "hidden semantic": "Hidden semantic false negatives: 36",
        "evidence tier table": "Evidence Tier By Process Label",
        "real-pilot process labels": "Real-pilot-positive process labels: 2 / 6",
        "ablation process labels": "Ablation-positive process labels: 2 / 6",
        "fixture-only process labels": "Fixture-only process labels: 2 / 6",
        "boundary interpretation": "do not detect hidden semantic correctness failures",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "detector evaluation audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "detector precision/recall evidence is consolidated for RQ2 boundary claims",
        "problems": problems,
    }


def check_rule_implementation_audit_content(path: Path = Path("docs/rule_implementation_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "rule implementation audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing rule implementation audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage count": "Rules covered: 6 / 6",
        "context proxy": "Context drift v1 proxy disclosed: yes",
        "real pilot tier count": "Real-pilot-positive rules: 2 / 6",
        "ablation tier count": "Ablation-positive rules: 2 / 6",
        "fixture tier count": "Fixture-only rules: 2 / 6",
        "detector evidence source": "Detector evidence source: `docs/detector_evaluation_audit.json`",
        "real pilot tier": "`real-pilot-positive`",
        "ablation tier": "`ablation-positive`",
        "fixture tier": "`fixture-only`",
        "verification gap": "`verification_gap`",
        "context drift": "`context_drift`",
        "sandbox": "`sandbox_permission_deadlock`",
        "semantic caveat": "not a full semantic task-keyword drift detector",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "rule implementation audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "taxonomy labels are backed by implemented diagnosis rules and paper-label aliases",
        "problems": problems,
    }


def check_failure_taxonomy_audit_content(path: Path = Path("docs/failure_taxonomy_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "failure taxonomy audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing failure taxonomy audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage count": "Labels covered: 6 / 6",
        "fixture f1": "Detector-fixture micro-F1: 1",
        "real pilot evidence tier": "Real-pilot-positive labels: 2 / 6",
        "ablation evidence tier": "Ablation-positive labels: 2 / 6",
        "fixture only evidence tier": "Fixture-only labels: 2 / 6",
        "verification gap": "verification_gap",
        "sandbox deadlock": "sandbox_permission_deadlock",
        "evidence tier table": "Evidence tier",
        "boundary interpretation": "rule-level taxonomy coverage",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "failure taxonomy audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "six target process-failure labels are covered by taxonomy docs, paper mapping, detector fixtures, and evidence-tier counts",
        "problems": problems,
    }


def check_task_category_coverage_content(path: Path = Path("docs/task_category_coverage.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "task category coverage audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing task category coverage audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "seed coverage": "Seed design categories covered: 7 / 7",
        "hard pool coverage": "Hard pool design categories covered: 6 / 7",
        "hard pool missing": "Hard pool missing design categories: `test_writing`",
        "hard family coverage": "Hard pool design-family categories covered: 6 / 7",
        "hard30 family coverage": "Hard30 design-family categories covered: 6 / 7",
        "family mapping": "Hard Category Family Mapping",
        "family boundary": "missing direct or family-level design categories such as `test_writing`",
        "task-count window": "Design task-count window: 30-50",
        "seed tasks": "Seed tasks: 30",
        "seed task-count window": "Seed tasks in design window: yes",
        "hard task-count window": "Hard tasks in design window: yes",
        "hard30 tasks": "Hard30 selected tasks: 30",
        "hard30 task-count window": "Hard30 selected tasks in design window: yes",
        "bug fix": "`bug_fix`",
        "test writing": "`test_writing`",
        "multi-turn change": "`multi_turn_change`",
        "interpretation": "seed benchmark covers all task categories named in the original design",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "task category coverage audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "benchmark manifests cover the task categories named in the experiment design and expose hard-tier category boundaries",
        "problems": problems,
    }


def check_phase_coverage_audit_content(path: Path = Path("docs/phase_coverage_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "phase coverage audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing phase coverage audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "phase coverage": "Phases covered: 7 / 7",
        "rq4 signals": "RQ4 core phase signals: 4 / 4",
        "inspect": "`inspect`",
        "edit": "`edit`",
        "verify": "`verify`",
        "recover": "`recover`",
        "run key": "`phase_verify_events`",
        "interpretation": "all phases must exist in the schema, paper draft, and run-level hard30 rows",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "phase coverage audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "phase segmentation is covered by schema, paper text, run rows, and RQ4 signals",
        "problems": problems,
    }


def check_harness_protocol_audit_content(path: Path = Path("docs/harness_protocol_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "harness protocol audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing harness protocol audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "prompt coverage": "Intervention prompts covered: 4 / 4",
        "rule count": "Harness rules per prompt: 5",
        "protocol coverage": "Protocol rules covered: 5 / 5",
        "inspect first": "inspect_first",
        "minimal edit": "minimal_edit",
        "verification": "post_edit_verification",
        "failure diagnosis": "failure_diagnosis_before_retry",
        "finish evidence": "finish_with_evidence",
        "run proxies": "Run-level proxy checks passed: 6 / 6",
        "proxy table": "Run-Level Proxy Checks",
        "token proxy": "token_waste_proxy",
        "scope caveat": "does not prove that every model run obeyed each instruction",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "harness protocol audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "intervention prompt templates and experiment protocol cover the harness constraints",
        "problems": problems,
    }


def check_related_work_audit_content(path: Path = Path("docs/related_work_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "related work audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing related work audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage count": "Topics covered: 8 / 8",
        "swe bench": "software_engineering_benchmarks",
        "multi-turn degradation": "multi_turn_degradation",
        "coding agents": "coding_agents_and_interfaces",
        "tool-use agents": "tool_use_agents_and_feedback",
        "trajectory diagnosis": "trace_based_agent_diagnosis",
        "alignment caveat": "not a full literature review",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "related work audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "related-work notes and paper draft cover the required positioning axes",
        "problems": problems,
    }


def check_bibliography_audit_content(path: Path = Path("docs/bibliography_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "bibliography audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing bibliography audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "references section": "Paper has References section: yes",
        "coverage count": "References covered: 12 / 12",
        "swe bench": "swe_bench",
        "multi-turn degradation": "llms_get_lost",
        "tool use": "toolformer",
        "codex cli": "codex_cli_repo",
        "trajectory diagnosis": "agentrx",
        "scope caveat": "does not replace venue-specific citation formatting",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "bibliography audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper references are discoverable from both the draft and related-work notes",
        "problems": problems,
    }


def check_paper_structure_audit_content(path: Path = Path("docs/paper_structure_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "paper structure audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing paper structure audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage count": "Sections covered: 11 / 11",
        "rq results": "rq_results",
        "references": "references",
        "boundary framing": "boundary_result_framing",
        "artifact conclusion": "artifact_and_conclusion",
        "scope caveat": "does not judge prose quality",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "paper structure audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper draft covers required sections, RQ blocks, and boundary-result framing",
        "problems": problems,
    }


def check_method_pipeline_audit_content(path: Path = Path("docs/method_pipeline_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "method pipeline audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing method pipeline audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "stage coverage": "Pipeline stages covered: 7 / 7",
        "trace input stage": "codex_jsonl_trace_input",
        "real trace fixture": "demo/real-codex-run.jsonl",
        "cli coverage": "CLI method commands covered: 4 / 4",
        "smoke coverage": "Smoke checks covered: 6 / 6",
        "parser stage": "`jsonl_event_parser`",
        "detector stage": "`failure_pattern_detector`",
        "comparison stage": "`baseline_vs_intervention_comparison`",
        "aggregate smoke": "`aggregate_baseline_intervention`",
        "live collection caveat": "does not execute live Codex collection",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "method pipeline audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper method pipeline maps to source code and offline CLI smoke outputs",
        "problems": problems,
    }


def check_rq_table_consistency_audit_content(path: Path = Path("docs/rq_table_consistency_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "rq table consistency audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing rq table consistency audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "rq coverage": "RQs covered: 4 / 4",
        "table coverage": "Table checks covered: 10 / 10",
        "rq1 distribution": "`hidden_semantic_distribution`",
        "rq2 boundary": "`hidden_semantic_detector_boundary`",
        "rq3 waste": "`hard30_waste_reduction`",
        "rq4 unresolved": "`unresolved_error_boundary`",
        "drift caveat": "does not add new statistical evidence",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "rq table consistency audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "paper RQ result tables match generated hard30 paper-report artifacts",
        "problems": problems,
    }


def check_reproducibility_audit_content(path: Path = Path("docs/reproducibility_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "reproducibility audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing reproducibility audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "coverage count": "Commands covered: 53 / 53",
        "semantic coverage count": "Semantic phrases covered: 3 / 3",
        "balanced fences": "Markdown fences balanced: yes",
        "submission gate": "submission_readiness_gate",
        "scope caveat": "does not execute the full real Codex collection commands",
        "nullable timing": "nullable_timing_metrics",
        "rule evidence tiers": "rule_evidence_tiers",
        "task design family mapping": "task_design_family_mapping",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "reproducibility audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "reproducibility checklist contains required commands and balanced Markdown fences",
        "problems": problems,
    }


def check_goal_completion_audit_content(path: Path = Path("docs/goal_completion_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "goal completion audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing goal completion audit"],
        }

    required_phrases = {
        "original incomplete": "Original goal complete: no",
        "boundary ready": "Boundary-result paper ready: yes",
        "do not complete": "Should mark active goal complete: no",
        "verification blocker": "verification_lift",
        "next decision": "Revise the thesis to a boundary-result paper",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "goal completion audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "original goal remains incomplete while boundary-result paper is ready",
        "problems": problems,
    }


def check_verification_lift_next_experiment_content(path: Path = Path("docs/verification_lift_next_experiment.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "verification-lift next experiment audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing verification-lift next experiment audit"],
        }

    required_phrases = {
        "original claim still open": "Original verification-lift claim closed: no",
        "claim revision required": "Claim revision required: yes",
        "no additional ordinary experiment": "Additional ordinary-baseline experiment required: no",
        "ablation boundary": "No-verify ablation cannot close the ordinary-baseline claim",
        "v2 scaffold": "## Planned Ordinary-Baseline V2 Scaffold",
        "v2 ready": "Ready: yes",
        "ordinary baseline gate": "ordinary_baseline",
        "saturation gate": "non_saturated_baseline_or_depth_metric",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "verification-lift next experiment audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "records ordinary-baseline verification-lift claim closure and thesis-revision status",
        "problems": problems,
    }


def check_verification_ablation_plan_audit_content(path: Path = Path("docs/verification_ablation_plan_audit.md")) -> dict[str, Any]:
    problems = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "name": "verification-ablation plan audit",
            "ok": False,
            "evidence": str(path),
            "problems": ["missing verification-ablation plan audit"],
        }

    required_phrases = {
        "ready": "Ready: yes",
        "task count": "Task count: 4",
        "materialized fixtures": "Materialized fixtures: 4",
    }
    for label, phrase in required_phrases.items():
        if phrase not in text:
            problems.append(f"missing {label}")

    return {
        "name": "verification-ablation plan audit",
        "ok": not problems,
        "evidence": str(path),
        "detail": "no-verify ablation task, prompt, and fixture scaffold is ready for mechanism-check evidence",
        "problems": problems,
    }


def build_report(selection_dir: Path, run_dir: Path) -> dict[str, Any]:
    checks = [
        check_hard30_selection(selection_dir),
        check_hard30_real_runs(run_dir, selection_dir),
        check_hard30_outputs(run_dir),
        check_manual_labels(run_dir),
        check_hard30_report_content(run_dir),
        check_hard30_task_diagnosis_content(),
        check_submission_package_content(),
        check_claim_text_guard_content(),
        check_headline_results_content(),
        check_thesis_revision_decision_content(),
        check_validity_threats_content(),
        check_limitations_traceability_audit_content(),
        check_expected_results_reconciliation_content(),
        check_submission_readiness_plan_audit_content(),
        check_paper_number_guard_content(),
        check_reviewer_path_audit_content(),
        check_artifact_guide_sequence_audit_content(),
        check_benchmark_trace_artifact_content(),
        check_label_provenance_audit_content(),
        check_label_limitations_audit_content(),
        check_verification_saturation_audit_content(),
        check_metric_coverage_audit_content(),
        check_paired_effects_audit_content(),
        check_paired_effect_limitations_audit_content(),
        check_demo_audit_content(),
        check_web_artifact_audit_content(),
        check_cli_surface_audit_content(),
        check_ci_surface_audit_content(),
        check_schema_field_audit_content(),
        check_parser_event_coverage_content(),
        check_failure_node_traceability_content(),
        check_detector_evaluation_audit_content(),
        check_rule_implementation_audit_content(),
        check_rq4_signal_audit_content(),
        check_phase_coverage_audit_content(),
        check_task_category_coverage_content(),
        check_harness_protocol_audit_content(),
        check_failure_taxonomy_audit_content(),
        check_related_work_audit_content(),
        check_bibliography_audit_content(),
        check_paper_abstract_audit_content(),
        check_paper_contribution_audit_content(),
        check_paper_conclusion_audit_content(),
        check_paper_structure_audit_content(),
        check_method_pipeline_audit_content(),
        check_rq_table_consistency_audit_content(),
        check_reproducibility_audit_content(),
        check_goal_completion_audit_content(),
        check_verification_lift_next_experiment_content(),
        check_verification_ablation_plan_audit_content(),
        check_paper_draft_content(),
        check_experiment_protocol_content(),
        check_exists(Path("docs/reproducibility_checklist.md"), "reproducibility checklist"),
    ]
    blocking = [check for check in checks if not check["ok"]]
    next_actions = build_next_actions(checks, run_dir)
    return {
        "ready": not blocking,
        "checks": checks,
        "blocking": [check["name"] for check in blocking],
        "next_actions": next_actions,
        "positioning": (
            "submission-ready hard30 artifact"
            if not blocking
            else "pilot artifact; collect/finalize/label hard30 before stronger submission"
        ),
    }


def build_next_actions(checks: list[dict[str, Any]], run_dir: Path) -> list[dict[str, str]]:
    by_name = {check["name"]: check for check in checks}
    actions = []
    if not by_name["hard30 real runs"]["ok"]:
        actions.append({
            "name": "collect hard30 five-task ramp",
            "command": (
                "PYTHONPATH=. python3 scripts/run_hard30_shards.py "
                f"--run-dir {run_dir} --limit 5 --max-parallel 5 --timeout-seconds 600 --skip-complete"
            ),
        })
        actions.append({
            "name": "collect remaining hard30 real traces",
            "command": (
                "PYTHONPATH=. python3 scripts/run_hard30_shards.py "
                f"--run-dir {run_dir} --max-parallel 15 --timeout-seconds 600 --skip-complete"
            ),
        })
        actions.append({
            "name": "merge completed hard30 shards",
            "command": f"PYTHONPATH=. python3 scripts/merge_hard30_shards.py --run-dir {run_dir}",
        })
    if not by_name["hard30 finalized outputs"]["ok"]:
        actions.append({
            "name": "preflight hard30 manifest",
            "command": (
                "PYTHONPATH=. python3 scripts/finalize_hard30_pilot.py "
                f"--run-dir {run_dir} --preflight-only --preflight-json {run_dir / 'preflight.json'}"
            ),
        })
        actions.append({
            "name": "finalize hard30 reports",
            "command": f"PYTHONPATH=. python3 scripts/finalize_hard30_pilot.py --run-dir {run_dir}",
        })
    if not by_name["hard30 manual labels"]["ok"]:
        actions.append({
            "name": "label hard30 failures",
            "command": f"edit {run_dir / 'manual-labels.jsonl'} from {run_dir / 'labels.jsonl'}",
        })
        actions.append({
            "name": "audit hard30 manual labels",
            "command": f"PYTHONPATH=. python3 scripts/audit_manual_labels.py --run-dir {run_dir}",
        })
        actions.append({
            "name": "evaluate hard30 labels",
            "command": (
                "PYTHONPATH=. python3 -m codex_trace.cli research evaluate-labels "
                f"{run_dir / 'runs.jsonl'} {run_dir / 'manual-labels.jsonl'} "
                f"--json-output {run_dir / 'label-eval.json'} --markdown-output {run_dir / 'label-eval.md'}"
            ),
        })
    return actions


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# CodexTrace Submission Readiness",
        "",
        f"Ready: {'yes' if report['ready'] else 'no'}",
        f"Positioning: {report['positioning']}",
        "",
        "| Check | Status | Evidence | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for check in report["checks"]:
        status = "pass" if check["ok"] else "missing"
        detail = check.get("detail", "")
        if check.get("missing"):
            detail = "missing: " + ", ".join(check["missing"])
        if check.get("unlabeled_failures"):
            detail = "unlabeled failures: " + ", ".join(check["unlabeled_failures"])
        if check.get("missing_notes"):
            detail = "missing notes: " + ", ".join(check["missing_notes"])
        if check.get("unknown_tags"):
            detail = "unknown tags: " + ", ".join(check["unknown_tags"])
        if check.get("missing_failure_labels"):
            detail = "missing failure labels: " + ", ".join(check["missing_failure_labels"])
        if check.get("extra_labels"):
            detail = "extra labels: " + ", ".join(check["extra_labels"])
        if check.get("outcome_mismatches"):
            detail = "outcome mismatches: " + ", ".join(check["outcome_mismatches"])
        if check.get("problems"):
            detail = "; ".join(check["problems"])
        lines.append(f"| {check['name']} | {status} | `{check['evidence']}` | {detail} |")
    if report["blocking"]:
        lines.extend(["", "## Blocking Items", ""])
        lines.extend(f"- {name}" for name in report["blocking"])
    if report["next_actions"]:
        lines.extend(["", "## Next Actions", ""])
        for action in report["next_actions"]:
            lines.extend([f"### {action['name']}", "", "```bash", action["command"], "```", ""])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether the CodexTrace hard30 artifact is submission-ready.")
    parser.add_argument("--selection-dir", type=Path, default=DEFAULT_HARD30_SELECTION_DIR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_HARD30_RUN_DIR)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    report = build_report(args.selection_dir, args.run_dir)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_report(report)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
