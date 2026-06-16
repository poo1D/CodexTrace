from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_TASKS = Path("benchmark/hard/pilot/hard30-selection/tasks.jsonl")
DEFAULT_RUNS = Path("benchmark/hard/pilot/hard30-real/runs.jsonl")
DEFAULT_LABELS = Path("benchmark/hard/pilot/hard30-real/manual-labels.jsonl")
DEFAULT_DELTAS = Path("benchmark/hard/pilot/hard30-real/paired-task-deltas.csv")


def build_task_diagnosis(
    tasks_path: Path = DEFAULT_TASKS,
    runs_path: Path = DEFAULT_RUNS,
    labels_path: Path = DEFAULT_LABELS,
    deltas_path: Path = DEFAULT_DELTAS,
) -> dict[str, Any]:
    tasks = {row["task_id"]: row for row in _read_jsonl(tasks_path)}
    runs_by_task: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in _read_jsonl(runs_path):
        runs_by_task[row["task_id"]][row["prompt_type"]] = row

    labels_by_task: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in _read_jsonl(labels_path):
        labels_by_task[row["task_id"]][row["prompt_type"]] = row

    deltas = {row["task_id"]: row for row in _read_csv(deltas_path)}
    rows = []
    category_counts: Counter[str] = Counter()
    failure_pattern_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()
    rows_by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for task_id in sorted(tasks):
        task = tasks[task_id]
        prompt_runs = runs_by_task[task_id]
        prompt_labels = labels_by_task[task_id]
        delta = deltas[task_id]
        baseline_outcome = _outcome(prompt_runs, "baseline")
        intervention_outcome = _outcome(prompt_runs, "intervention")
        category = task.get("category", "unknown")
        failure_pattern = _failure_pattern(baseline_outcome, intervention_outcome)
        tags = sorted({
            tag
            for label in prompt_labels.values()
            for tag in label.get("failure_tags", [])
        })
        for tag in tags:
            label_counts[tag] += 1
        category_counts[category] += 1
        failure_pattern_counts[failure_pattern] += 1
        rows.append({
            "task_id": task_id,
            "category": category,
            "repo_hint": task.get("repo_hint", ""),
            "baseline_outcome": baseline_outcome,
            "intervention_outcome": intervention_outcome,
            "failure_pattern": failure_pattern,
            "failure_tags": tags,
            "success_delta": _to_int(delta["success_delta"]),
            "repeated_tool_call_delta": _to_int(delta["repeated_tool_call_delta"]),
            "token_usage_delta": _to_int(delta["token_usage_delta"]),
            "failure_score_delta": _to_int(delta["failure_score_delta"]),
        })
        rows[-1]["paired_lostness_score"] = _paired_lostness_score(rows[-1])
        rows_by_category[category].append(rows[-1])

    double_failures = [row for row in rows if row["failure_pattern"] == "both_failed"]
    intervention_repairs = [row for row in rows if row["failure_pattern"] == "intervention_repaired"]
    intervention_regressions = [row for row in rows if row["failure_pattern"] == "intervention_regressed"]
    stable_successes = [row for row in rows if row["failure_pattern"] == "both_succeeded"]

    return {
        "summary": {
            "task_count": len(rows),
            "category_counts": dict(sorted(category_counts.items())),
            "failure_pattern_counts": dict(sorted(failure_pattern_counts.items())),
            "label_counts": dict(sorted(label_counts.items())),
            "double_failure_count": len(double_failures),
            "intervention_repair_count": len(intervention_repairs),
            "intervention_regression_count": len(intervention_regressions),
            "stable_success_count": len(stable_successes),
            "token_improved_count": sum(1 for row in rows if row["token_usage_delta"] < 0),
            "repeated_call_improved_count": sum(1 for row in rows if row["repeated_tool_call_delta"] < 0),
        },
        "category_diagnosis": _category_diagnosis(rows_by_category),
        "double_failures": double_failures,
        "intervention_repairs": intervention_repairs,
        "intervention_regressions": intervention_regressions,
        "top_waste_reductions": sorted(rows, key=lambda row: row["token_usage_delta"])[:5],
        "top_waste_regressions": sorted(rows, key=lambda row: row["token_usage_delta"], reverse=True)[:5],
        "top_repeated_call_reductions": sorted(rows, key=lambda row: row["repeated_tool_call_delta"])[:5],
        "top_lostness_tasks": sorted(rows, key=lambda row: row["paired_lostness_score"], reverse=True)[:5],
        "tasks": rows,
    }


def render_task_diagnosis_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Hard30 Task Diagnosis",
        "",
        "This generated audit answers which hard30 tasks are easiest for the agent to get lost in, and where the intervention reduces or worsens process waste.",
        "",
        "## Summary",
        "",
        f"- Tasks: {summary['task_count']}",
        f"- Both failed: {summary['double_failure_count']}",
        f"- Intervention repaired: {summary['intervention_repair_count']}",
        f"- Intervention regressed: {summary['intervention_regression_count']}",
        f"- Both succeeded: {summary['stable_success_count']}",
        f"- Token usage improved: {summary['token_improved_count']}/{summary['task_count']}",
        f"- Repeated tool calls improved: {summary['repeated_call_improved_count']}/{summary['task_count']}",
        "",
        "## Failure Patterns",
        "",
        "| Pattern | Count |",
        "| --- | ---: |",
    ]
    for pattern, count in summary["failure_pattern_counts"].items():
        lines.append(f"| {pattern} | {count} |")

    lines.extend([
        "",
        "## Category-Level Diagnosis",
        "",
        "| Category | Tasks | Both failed | Repairs | Regressions | Token improved | Repeated-call improved | Avg token delta | Avg repeated-call delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in result["category_diagnosis"]:
        lines.append(
            f"| {row['category']} | {row['task_count']} | {row['double_failure_count']} | "
            f"{row['intervention_repair_count']} | {row['intervention_regression_count']} | "
            f"{row['token_improved_count']} | {row['repeated_call_improved_count']} | "
            f"{_fmt(row['avg_token_usage_delta'])} | {_fmt(row['avg_repeated_tool_call_delta'])} |"
        )

    lines.extend([
        "",
        "## Double-Failure Tasks",
        "",
        "| Task | Category | Repo | Tags | Repeated-call delta | Token delta |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ])
    for row in result["double_failures"]:
        lines.append(_task_row(row))

    lines.extend([
        "",
        "## Intervention Repairs And Regressions",
        "",
        "| Task | Pattern | Category | Repo | Repeated-call delta | Token delta |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ])
    for row in result["intervention_repairs"] + result["intervention_regressions"]:
        lines.append(_pattern_row(row))

    lines.extend([
        "",
        "## Top Lostness Ranking",
        "",
        "The paired lostness score combines outcome persistence, manual failure tags, and paired waste reductions. Higher scores mark tasks where the agent most visibly got lost in the paired traces, especially when the intervention removed substantial token or repeated-call waste without fully repairing the outcome.",
        "",
        "| Task | Pattern | Category | Tags | Lostness score | Repeated-call delta | Token delta |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ])
    for row in result["top_lostness_tasks"]:
        lines.append(_lostness_row(row))

    lines.extend([
        "",
        "## Largest Waste Reductions",
        "",
        "| Task | Pattern | Category | Repo | Repeated-call delta | Token delta | Failure-score delta |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ])
    for row in result["top_waste_reductions"]:
        lines.append(_waste_row(row))

    lines.extend([
        "",
        "## Largest Waste Regressions",
        "",
        "| Task | Pattern | Category | Repo | Repeated-call delta | Token delta | Failure-score delta |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ])
    for row in result["top_waste_regressions"]:
        lines.append(_waste_row(row))

    lines.extend([
        "",
        "Interpretation: the current hard30 artifact is dominated by hidden semantic double failures, while the intervention's clearest task-level effect is lower token and repeated-call waste on most paired tasks. `HARD-050` is the one hard30 repair, and `HARD-007` is the one hard30 outcome regression.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_task_diagnosis_markdown(result), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _outcome(runs: dict[str, dict[str, Any]], prompt_type: str) -> str:
    return runs.get(prompt_type, {}).get("outcome", "unknown")


def _failure_pattern(baseline_outcome: str, intervention_outcome: str) -> str:
    if baseline_outcome == "failure" and intervention_outcome == "failure":
        return "both_failed"
    if baseline_outcome == "success" and intervention_outcome == "success":
        return "both_succeeded"
    if baseline_outcome == "failure" and intervention_outcome == "success":
        return "intervention_repaired"
    if baseline_outcome == "success" and intervention_outcome == "failure":
        return "intervention_regressed"
    return "unknown"


def _to_int(value: str) -> int:
    return int(float(value))


def _task_row(row: dict[str, Any]) -> str:
    tags = ", ".join(row["failure_tags"]) if row["failure_tags"] else "-"
    return (
        f"| {row['task_id']} | {row['category']} | {row['repo_hint']} | {tags} | "
        f"{row['repeated_tool_call_delta']} | {row['token_usage_delta']} |"
    )


def _pattern_row(row: dict[str, Any]) -> str:
    return (
        f"| {row['task_id']} | {row['failure_pattern']} | {row['category']} | {row['repo_hint']} | "
        f"{row['repeated_tool_call_delta']} | {row['token_usage_delta']} |"
    )


def _waste_row(row: dict[str, Any]) -> str:
    return (
        f"| {row['task_id']} | {row['failure_pattern']} | {row['category']} | {row['repo_hint']} | "
        f"{row['repeated_tool_call_delta']} | {row['token_usage_delta']} | {row['failure_score_delta']} |"
    )


def _lostness_row(row: dict[str, Any]) -> str:
    tags = ", ".join(row["failure_tags"]) if row["failure_tags"] else "-"
    return (
        f"| {row['task_id']} | {row['failure_pattern']} | {row['category']} | {tags} | "
        f"{_fmt(row['paired_lostness_score'])} | {row['repeated_tool_call_delta']} | {row['token_usage_delta']} |"
    )


def _paired_lostness_score(row: dict[str, Any]) -> float:
    """Transparent task-level index for ranking where paired hard30 traces got lost."""
    score = 0.0
    if row["failure_pattern"] == "both_failed":
        score += 100.0
    elif row["failure_pattern"] == "intervention_regressed":
        score += 80.0
    elif row["failure_pattern"] == "intervention_repaired":
        score += 50.0

    tags = set(row["failure_tags"])
    if "hidden_semantic_edge_case" in tags:
        score += 40.0
    if "repetitive_exploration" in tags:
        score += 30.0
    if "sandbox_permission_deadlock" in tags:
        score += 30.0
    if "unrecovered_tool_error" in tags:
        score += 20.0
    if "verification_gap" in tags or "premature_completion" in tags:
        score += 20.0
    if "context_drift" in tags:
        score += 20.0

    # Negative deltas mean the intervention spent fewer resources than baseline;
    # large reductions are evidence that the baseline trace had more process waste.
    score += max(0, -row["repeated_tool_call_delta"]) * 2.0
    score += max(0, -row["token_usage_delta"]) / 10000.0
    score += max(0, -row["failure_score_delta"])
    return round(score, 2)


def _category_diagnosis(rows_by_category: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    output = []
    for category, rows in sorted(rows_by_category.items()):
        output.append({
            "category": category,
            "task_count": len(rows),
            "double_failure_count": sum(1 for row in rows if row["failure_pattern"] == "both_failed"),
            "intervention_repair_count": sum(1 for row in rows if row["failure_pattern"] == "intervention_repaired"),
            "intervention_regression_count": sum(1 for row in rows if row["failure_pattern"] == "intervention_regressed"),
            "token_improved_count": sum(1 for row in rows if row["token_usage_delta"] < 0),
            "repeated_call_improved_count": sum(1 for row in rows if row["repeated_tool_call_delta"] < 0),
            "avg_token_usage_delta": sum(row["token_usage_delta"] for row in rows) / len(rows),
            "avg_repeated_tool_call_delta": sum(row["repeated_tool_call_delta"] for row in rows) / len(rows),
        })
    return output


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value / 1000:.1f}k"
        return f"{value:.4g}"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a task-level hard30 diagnosis audit.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--deltas", type=Path, default=DEFAULT_DELTAS)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_task_diagnosis(args.tasks, args.runs, args.labels, args.deltas)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_task_diagnosis_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
