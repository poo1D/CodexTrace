from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_SEED_TASKS = Path("benchmark/tasks.jsonl")
DEFAULT_HARD_TASKS = Path("benchmark/hard/tasks.jsonl")
DEFAULT_HARD30_TASKS = Path("benchmark/hard/pilot/hard30-selection/tasks.jsonl")

REQUIRED_DESIGN_CATEGORIES = (
    "bug_fix",
    "feature",
    "test_writing",
    "refactor",
    "ci_failure",
    "error_localization",
    "multi_turn_change",
)
HARD_CATEGORY_FAMILIES = {
    "bug_fix": ("bug_fix", "error_recovery", "stateful_regression"),
    "feature": ("feature", "data_migration"),
    "test_writing": ("test_writing",),
    "refactor": ("refactor",),
    "ci_failure": ("ci_failure", "dependency_friction"),
    "error_localization": ("error_localization", "multi_turn_tool_debug"),
    "multi_turn_change": ("multi_turn_change",),
}


def _load_category_counts(path: Path) -> dict[str, Any]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    counts = Counter(str(row.get("category", "")) for row in rows)
    missing_category = [str(row.get("task_id", "<missing>")) for row in rows if not row.get("category")]
    return {
        "path": str(path),
        "task_count": len(rows),
        "category_counts": dict(sorted(counts.items())),
        "missing_category": missing_category,
    }


def build_task_category_coverage_audit(
    seed_tasks_path: Path = DEFAULT_SEED_TASKS,
    hard_tasks_path: Path = DEFAULT_HARD_TASKS,
    hard30_tasks_path: Path = DEFAULT_HARD30_TASKS,
) -> dict[str, Any]:
    seed = _load_category_counts(seed_tasks_path)
    hard = _load_category_counts(hard_tasks_path)
    hard30 = _load_category_counts(hard30_tasks_path)

    seed_categories = set(seed["category_counts"])
    hard_categories = set(hard["category_counts"])
    hard30_categories = set(hard30["category_counts"])
    required = set(REQUIRED_DESIGN_CATEGORIES)

    rows = []
    for category in REQUIRED_DESIGN_CATEGORIES:
        hard_family_categories = HARD_CATEGORY_FAMILIES[category]
        hard_family_count = sum(hard["category_counts"].get(candidate, 0) for candidate in hard_family_categories)
        hard30_family_count = sum(hard30["category_counts"].get(candidate, 0) for candidate in hard_family_categories)
        rows.append({
            "category": category,
            "hard_family_categories": list(hard_family_categories),
            "seed_count": seed["category_counts"].get(category, 0),
            "hard_count": hard["category_counts"].get(category, 0),
            "hard30_count": hard30["category_counts"].get(category, 0),
            "hard_family_count": hard_family_count,
            "hard30_family_count": hard30_family_count,
            "seed_covered": category in seed_categories,
            "hard_covered": category in hard_categories,
            "hard30_covered": category in hard30_categories,
            "hard_family_covered": hard_family_count > 0,
            "hard30_family_covered": hard30_family_count > 0,
        })

    all_missing_category = (
        seed["missing_category"]
        + hard["missing_category"]
        + hard30["missing_category"]
    )
    seed_design_ready = not (required - seed_categories) and not seed["missing_category"]
    hard30_minimum_ready = (
        hard30["task_count"] == 30
        and len(hard30_categories) >= 7
        and not hard30["missing_category"]
    )
    hard_family_covered = {
        row["category"]
        for row in rows
        if row["hard_family_covered"]
    }
    hard30_family_covered = {
        row["category"]
        for row in rows
        if row["hard30_family_covered"]
    }
    return {
        "summary": {
            "ready": seed_design_ready and hard30_minimum_ready and not all_missing_category,
            "required_design_categories": len(REQUIRED_DESIGN_CATEGORIES),
            "seed_required_categories_covered": len(required & seed_categories),
            "hard_required_categories_covered": len(required & hard_categories),
            "hard_missing_required_categories": sorted(required - hard_categories),
            "hard_family_categories_covered": len(hard_family_covered),
            "hard_family_missing_required_categories": sorted(required - hard_family_covered),
            "hard30_family_categories_covered": len(hard30_family_covered),
            "hard30_family_missing_required_categories": sorted(required - hard30_family_covered),
            "hard30_category_count": len(hard30_categories),
            "seed_task_count": seed["task_count"],
            "hard_task_count": hard["task_count"],
            "hard30_task_count": hard30["task_count"],
            "seed_design_ready": seed_design_ready,
            "hard30_minimum_ready": hard30_minimum_ready,
            "missing_category_rows": len(all_missing_category),
        },
        "required_categories": rows,
        "tiers": {
            "seed": seed,
            "hard": hard,
            "hard30": hard30,
        },
    }


def render_task_category_coverage_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Task Category Coverage Audit",
        "",
        "This generated audit checks that benchmark task manifests cover the task categories named in the experiment design.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Seed design categories covered: {summary['seed_required_categories_covered']} / {summary['required_design_categories']}",
        f"- Hard pool design categories covered: {summary['hard_required_categories_covered']} / {summary['required_design_categories']}",
        f"- Hard pool missing design categories: {_fmt_list(summary['hard_missing_required_categories'])}",
        f"- Hard pool design-family categories covered: {summary['hard_family_categories_covered']} / {summary['required_design_categories']}",
        f"- Hard pool missing design-family categories: {_fmt_list(summary['hard_family_missing_required_categories'])}",
        f"- Hard30 design-family categories covered: {summary['hard30_family_categories_covered']} / {summary['required_design_categories']}",
        f"- Hard30 missing design-family categories: {_fmt_list(summary['hard30_family_missing_required_categories'])}",
        f"- Seed tasks: {summary['seed_task_count']}",
        f"- Hard tasks: {summary['hard_task_count']}",
        f"- Hard30 selected tasks: {summary['hard30_task_count']}",
        f"- Hard30 distinct categories: {summary['hard30_category_count']}",
        f"- Missing category rows: {summary['missing_category_rows']}",
        "",
        "## Required Design Categories",
        "",
        "| Category | Seed | Hard pool | Hard30 selection | Hard family | Hard30 family |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["required_categories"]:
        lines.append(
            f"| `{row['category']}` | {row['seed_count']} | {row['hard_count']} | "
            f"{row['hard30_count']} | {row['hard_family_count']} | {row['hard30_family_count']} |"
        )
    lines.extend([
        "",
        "## Hard Category Family Mapping",
        "",
        "Hard-tier categories refine the original design categories. Family counts aggregate those refinements back to the design-level task types; direct category counts are still reported separately so missing categories such as `test_writing` remain visible.",
        "",
        "| Design category | Hard-tier categories counted in family |",
        "| --- | --- |",
    ])
    for category in REQUIRED_DESIGN_CATEGORIES:
        family = ", ".join(f"`{value}`" for value in HARD_CATEGORY_FAMILIES[category])
        lines.append(f"| `{category}` | {family} |")
    lines.extend([
        "",
        "## Tier Category Counts",
        "",
    ])
    for tier_name, tier in result["tiers"].items():
        counts = ", ".join(
            f"`{category}`={count}"
            for category, count in tier["category_counts"].items()
        )
        lines.append(f"- `{tier_name}`: {counts}")
    lines.extend([
        "",
        "Interpretation: the seed benchmark covers all task categories named in the original design. The hard pool and hard30 paper-facing tier are selected for hidden-grader difficulty and broad category diversity; they are not required to preserve every seed category one-for-one, and missing direct or family-level design categories such as `test_writing` must be treated as coverage boundaries.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_task_category_coverage_markdown(result), encoding="utf-8")


def _fmt_list(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "-"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit task-category coverage for CodexTrace benchmark manifests.")
    parser.add_argument("--seed-tasks", type=Path, default=DEFAULT_SEED_TASKS)
    parser.add_argument("--hard-tasks", type=Path, default=DEFAULT_HARD_TASKS)
    parser.add_argument("--hard30-tasks", type=Path, default=DEFAULT_HARD30_TASKS)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_task_category_coverage_audit(args.seed_tasks, args.hard_tasks, args.hard30_tasks)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_task_category_coverage_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
