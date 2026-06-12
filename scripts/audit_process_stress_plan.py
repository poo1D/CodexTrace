from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_TASKS = Path("benchmark/process-stress/tasks.jsonl")
DEFAULT_README = Path("benchmark/process-stress/README.md")
TARGET_TAGS = (
    "verification_gap",
    "unrecovered_tool_error",
    "repetitive_exploration",
    "context_drift",
    "premature_completion",
    "sandbox_permission_deadlock",
)


def audit_process_stress_plan(tasks_path: Path = DEFAULT_TASKS, readme_path: Path = DEFAULT_README) -> dict[str, Any]:
    rows = _load_jsonl(tasks_path)
    tag_counts: Counter[str] = Counter()
    task_ids = []
    problems = []
    materialized_count = 0
    benchmark_dir = tasks_path.parent

    for row in rows:
        task_id = str(row.get("task_id", ""))
        task_ids.append(task_id)
        for field in ("category", "instruction", "public_success_check", "success_check", "fixture_path", "grader_path", "repo_hint"):
            if not row.get(field):
                problems.append(f"{task_id or '<missing>'} missing {field}")
        tags = row.get("target_failure_tags", [])
        if not isinstance(tags, list) or not tags:
            problems.append(f"{task_id or '<missing>'} missing target_failure_tags")
            continue
        unknown = sorted(str(tag) for tag in tags if tag not in TARGET_TAGS)
        if unknown:
            problems.append(f"{task_id} has unknown target tag(s): {', '.join(unknown)}")
        tag_counts.update(str(tag) for tag in tags)
        fixture_path = benchmark_dir / str(row.get("fixture_path", ""))
        grader_path = benchmark_dir / str(row.get("grader_path", ""))
        if fixture_path.exists() and grader_path.exists():
            materialized_count += 1
        else:
            problems.append(f"{task_id or '<missing>'} fixture or grader is not materialized")

    expected_ids = [f"PST-{index:03d}" for index in range(1, 13)]
    if task_ids != expected_ids:
        problems.append(f"task ids are {task_ids}, expected {expected_ids}")
    if len(set(task_ids)) != len(task_ids):
        problems.append("task ids are not unique")

    missing_tag_coverage = [tag for tag in TARGET_TAGS if tag_counts[tag] < 2]
    if missing_tag_coverage:
        problems.append("target tags below 2-task coverage: " + ", ".join(missing_tag_coverage))

    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    for phrase in ("process-label recall", "verification rate", "token usage"):
        if phrase not in readme_text:
            problems.append(f"README missing acceptance phrase: {phrase}")

    return {
        "ok": not problems,
        "task_count": len(rows),
        "materialized_count": materialized_count,
        "tag_counts": {tag: tag_counts[tag] for tag in TARGET_TAGS},
        "problems": problems,
        "tasks_path": str(tasks_path),
        "readme_path": str(readme_path),
    }


def render_process_stress_plan_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Process-Stress Plan Audit",
        "",
        f"Ready: {'yes' if result['ok'] else 'no'}",
        f"Task count: {result['task_count']}",
        f"Materialized fixtures: {result['materialized_count']}",
        "",
        "## Target Tag Coverage",
        "",
        "| Tag | Materialized tasks |",
        "| --- | ---: |",
    ]
    for tag, count in result["tag_counts"].items():
        lines.append(f"| {tag} | {count} |")
    if result["problems"]:
        lines.extend(["", "## Problems", ""])
        for problem in result["problems"]:
            lines.append(f"- {problem}")
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_process_stress_plan_markdown(result), encoding="utf-8")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the planned process-stress benchmark slice.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = audit_process_stress_plan(args.tasks, args.readme)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_process_stress_plan_markdown(result), end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
