from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARD_TASKS = ROOT / "benchmark" / "hard" / "tasks.jsonl"
OUT = ROOT / "benchmark" / "hard" / "pilot" / "hard30-selection"

SELECTED_TASK_IDS = [
    "HARD-001",
    "HARD-002",
    "HARD-003",
    "HARD-004",
    "HARD-005",
    "HARD-006",
    "HARD-007",
    "HARD-008",
    "HARD-009",
    "HARD-010",
    "HARD-011",
    "HARD-012",
    "HARD-013",
    "HARD-015",
    "HARD-020",
    "HARD-023",
    "HARD-024",
    "HARD-025",
    "HARD-027",
    "HARD-031",
    "HARD-032",
    "HARD-033",
    "HARD-035",
    "HARD-038",
    "HARD-039",
    "HARD-040",
    "HARD-043",
    "HARD-045",
    "HARD-047",
    "HARD-050",
]


def load_rows() -> list[dict]:
    return [json.loads(line) for line in HARD_TASKS.read_text(encoding="utf-8").splitlines() if line.strip()]


def render_table(rows: list[dict]) -> str:
    lines = [
        "| ID | Category | Repo hint |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['task_id']} | {row['category']} | {row['repo_hint']} |")
    return "\n".join(lines)


def materialize() -> None:
    all_rows = load_rows()
    by_id = {row["task_id"]: row for row in all_rows}
    missing = [task_id for task_id in SELECTED_TASK_IDS if task_id not in by_id]
    if missing:
        raise SystemExit(f"Missing selected hard task ids: {missing}")
    if len(SELECTED_TASK_IDS) != len(set(SELECTED_TASK_IDS)):
        raise SystemExit("Duplicate selected hard task ids")

    selected_rows = []
    for task_id in SELECTED_TASK_IDS:
        row = dict(by_id[task_id])
        row["fixture_path"] = f"../../repos/{task_id}/repo"
        row["grader_path"] = f"../../repos/{task_id}/grader"
        selected_rows.append(row)
    category_counts = dict(sorted(Counter(row["category"] for row in selected_rows).items()))
    public_checks = dict(sorted(Counter(row["public_success_check"] for row in selected_rows).items()))

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "task_ids.txt").write_text("\n".join(SELECTED_TASK_IDS) + "\n", encoding="utf-8")
    (OUT / "tasks.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in selected_rows),
        encoding="utf-8",
    )
    manifest = {
        "name": "hard30-selection",
        "source_tasks": "benchmark/hard/tasks.jsonl",
        "task_count": len(selected_rows),
        "selected_task_ids": SELECTED_TASK_IDS,
        "category_counts": category_counts,
        "public_success_check_counts": public_checks,
        "expected_prompt_conditions": ["baseline", "intervention"],
        "expected_run_records": len(selected_rows) * 2,
        "selection_policy": [
            "Keep HARD-001 through HARD-010 so the existing hard10 pilot remains a prefix.",
            "Add 20 tasks from HARD-011 through HARD-050 to cover all hard-tier categories.",
            "Prefer tasks with observable process-failure pressure and hidden semantic oracles.",
            "Keep Python/TypeScript and unittest/npm checks mixed for tool-use diversity.",
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readme = f"""# Hard30 Pilot Selection

This directory fixes the 30-task hard-tier pilot used for the next real
baseline/intervention collection pass.

The selection keeps `HARD-001` through `HARD-010` as the evaluated hard10
prefix, then adds 20 tasks from the expanded hard tier to cover every hard
category and several intended process-failure pressures.

Expected real run count: 30 tasks x 2 prompt conditions = 60 runs.

## Category Counts

{json.dumps(category_counts, indent=2, sort_keys=True)}

## Selected Tasks

{render_table(selected_rows)}

## Dry-Run Command

```bash
PYTHONPATH=. python3 -m codex_trace.cli research run \\
  --tasks benchmark/hard/pilot/hard30-selection/tasks.jsonl \\
  --output-dir /tmp/codextrace-hard30-dry \\
  --dry-run
```
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    materialize()
