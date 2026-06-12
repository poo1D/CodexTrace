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
        "detector rule mapping": "| Taxonomy label | Implementation finding | Detector signal |",
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


def build_report(selection_dir: Path, run_dir: Path) -> dict[str, Any]:
    checks = [
        check_hard30_selection(selection_dir),
        check_hard30_real_runs(run_dir, selection_dir),
        check_hard30_outputs(run_dir),
        check_manual_labels(run_dir),
        check_hard30_report_content(run_dir),
        check_exists(Path("docs/hard30_task_diagnosis.md"), "hard30 task diagnosis"),
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
