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
    "labels.jsonl",
    "paper-report.json",
    "paper-report.md",
)


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
    labels_path = run_dir / "manual-labels.jsonl"
    if not labels_path.exists():
        return {
            "name": "hard30 manual labels",
            "ok": False,
            "evidence": str(labels_path),
            "detail": "missing manual-labels.jsonl",
        }
    rows = [json.loads(line) for line in labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    unlabeled_failures = [
        f"{row.get('task_id')}/{row.get('prompt_type')}"
        for row in rows
        if row.get("outcome") == "failure" and not row.get("failure_tags")
    ]
    return {
        "name": "hard30 manual labels",
        "ok": not unlabeled_failures,
        "evidence": str(labels_path),
        "detail": f"{len(rows)} label row(s)",
        "unlabeled_failures": unlabeled_failures,
    }


def build_report(selection_dir: Path, run_dir: Path) -> dict[str, Any]:
    checks = [
        check_hard30_selection(selection_dir),
        check_hard30_real_runs(run_dir, selection_dir),
        check_hard30_outputs(run_dir),
        check_manual_labels(run_dir),
        check_exists(Path("docs/paper_draft.md"), "paper draft"),
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
            "name": "collect hard30 real traces",
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
