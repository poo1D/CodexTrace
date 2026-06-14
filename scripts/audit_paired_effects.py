from __future__ import annotations

import argparse
import json
import random
import sys
from math import comb
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.research import aggregate_runs


DEFAULT_STUDIES = (
    ("full30", Path("benchmark/pilot/full30-real/runs.jsonl")),
    ("hard10", Path("benchmark/hard/pilot/hard10-real/runs.jsonl")),
    ("hard30", Path("benchmark/hard/pilot/hard30-real/runs.jsonl")),
    ("process_stress", Path("benchmark/process-stress/pilot/full-real/runs.jsonl")),
    ("verification_lift", Path("benchmark/verification-lift/pilot/full-real/runs.jsonl")),
    ("verification_lift_v2", Path("benchmark/verification-lift-v2/pilot/full-real/runs.jsonl")),
    ("verification_ablation", Path("benchmark/verification-ablation/pilot/full-real/runs.jsonl")),
)
METRICS = {
    "success_delta": {"field": "success", "direction": 1, "label": "success"},
    "verification_delta": {"field": "verification_rate", "direction": 1, "label": "verification"},
    "success_check_verification_delta": {
        "field": "success_check_verification_rate",
        "direction": 1,
        "label": "success-check verification",
    },
    "unresolved_error_delta": {"field": "unresolved_error", "direction": -1, "label": "unresolved errors"},
    "repeated_tool_call_delta": {
        "field": "repeated_tool_call_count",
        "direction": -1,
        "label": "repeated tool calls",
    },
    "retry_delta": {"field": "retry_count", "direction": -1, "label": "retries"},
    "command_failure_delta": {
        "field": "command_failure_count",
        "direction": -1,
        "label": "command failures",
    },
    "turn_delta": {"field": "turn_count", "direction": -1, "label": "turns"},
    "token_usage_delta": {"field": "token_usage", "direction": -1, "label": "token usage"},
    "failure_score_delta": {"field": "failure_score", "direction": -1, "label": "failure score"},
}
BOOTSTRAP_SAMPLES = 2000
BOOTSTRAP_SEED = 20260614


def build_paired_effects_audit(
    studies: tuple[tuple[str, Path], ...] = DEFAULT_STUDIES,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    study_rows = []
    metric_rows = []
    for study_name, manifest_path in studies:
        paired_rows = _paired_rows(aggregate_runs(manifest_path)["runs"])
        metrics = [
            _metric_effect(study_name, metric, paired_rows, bootstrap_samples, seed)
            for metric in METRICS
        ]
        by_metric = {row["metric"]: row for row in metrics}
        study_rows.append({
            "study": study_name,
            "manifest": str(manifest_path),
            "paired_task_count": len(paired_rows),
            "success_avg_delta": by_metric["success_delta"]["avg_delta"],
            "verification_avg_delta": by_metric["verification_delta"]["avg_delta"],
            "repeated_tool_call_avg_delta": by_metric["repeated_tool_call_delta"]["avg_delta"],
            "token_usage_avg_delta": by_metric["token_usage_delta"]["avg_delta"],
            "repeated_tool_call_improved": by_metric["repeated_tool_call_delta"]["improved"],
            "token_usage_improved": by_metric["token_usage_delta"]["improved"],
        })
        metric_rows.extend(metrics)

    hard30 = _metric_lookup(metric_rows, "hard30")
    ready = (
        len(study_rows) == len(studies)
        and hard30["success_delta"]["n"] == 30
        and hard30["repeated_tool_call_delta"]["avg_delta"] < 0
        and hard30["repeated_tool_call_delta"]["ci_high"] < 0
        and hard30["token_usage_delta"]["avg_delta"] < 0
        and hard30["token_usage_delta"]["ci_high"] < 0
        and hard30["verification_delta"]["avg_delta"] == 0
    )
    return {
        "summary": {
            "ready": ready,
            "study_count": len(study_rows),
            "metric_count": len(METRICS),
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_seed": seed,
            "hard30_paired_tasks": hard30["success_delta"]["n"],
            "hard30_repeated_tool_call_avg_delta": hard30["repeated_tool_call_delta"]["avg_delta"],
            "hard30_repeated_tool_call_ci": [
                hard30["repeated_tool_call_delta"]["ci_low"],
                hard30["repeated_tool_call_delta"]["ci_high"],
            ],
            "hard30_token_usage_avg_delta": hard30["token_usage_delta"]["avg_delta"],
            "hard30_token_usage_ci": [
                hard30["token_usage_delta"]["ci_low"],
                hard30["token_usage_delta"]["ci_high"],
            ],
            "hard30_verification_avg_delta": hard30["verification_delta"]["avg_delta"],
        },
        "studies": study_rows,
        "metrics": metric_rows,
    }


def render_paired_effects_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    hard30 = _metric_lookup(result["metrics"], "hard30")
    lines = [
        "# Paired Effects Audit",
        "",
        "This generated audit computes task-paired baseline-to-intervention effects for the stored CodexTrace pilots. Deltas are intervention minus baseline; positive is better for success and verification, while negative is better for waste/error metrics.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Studies covered: {summary['study_count']} / {summary['study_count']}",
        f"- Metrics per study: {summary['metric_count']}",
        f"- Bootstrap samples: {summary['bootstrap_samples']}",
        f"- Bootstrap seed: {summary['bootstrap_seed']}",
        f"- Hard30 paired tasks: {summary['hard30_paired_tasks']}",
        f"- Hard30 repeated tool-call delta: {_fmt(summary['hard30_repeated_tool_call_avg_delta'])} "
        f"[{_fmt(summary['hard30_repeated_tool_call_ci'][0])}, {_fmt(summary['hard30_repeated_tool_call_ci'][1])}]",
        f"- Hard30 token-usage delta: {_fmt(summary['hard30_token_usage_avg_delta'])} "
        f"[{_fmt(summary['hard30_token_usage_ci'][0])}, {_fmt(summary['hard30_token_usage_ci'][1])}]",
        f"- Hard30 verification delta: {_fmt(summary['hard30_verification_avg_delta'])}",
        "",
        "## Hard30 Paired Metrics",
        "",
        "| Metric | N | Improved | Regressed | Unchanged | Avg delta | 95% bootstrap CI | Sign p |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for metric in (
        "success_delta",
        "verification_delta",
        "success_check_verification_delta",
        "unresolved_error_delta",
        "repeated_tool_call_delta",
        "retry_delta",
        "command_failure_delta",
        "turn_delta",
        "token_usage_delta",
        "failure_score_delta",
    ):
        lines.append(_metric_row(hard30[metric]))

    lines.extend([
        "",
        "## Study-Level Waste Deltas",
        "",
        "| Study | Paired tasks | Success delta | Verification delta | Repeated call delta | Token delta | Repeated improved | Token improved |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in result["studies"]:
        lines.append(
            f"| {row['study']} | {row['paired_task_count']} | {_fmt(row['success_avg_delta'])} | "
            f"{_fmt(row['verification_avg_delta'])} | {_fmt(row['repeated_tool_call_avg_delta'])} | "
            f"{_fmt(row['token_usage_avg_delta'])} | {row['repeated_tool_call_improved']} | {row['token_usage_improved']} |"
        )

    lines.extend([
        "",
        "Interpretation: this audit supports the RQ3 waste-reduction claim with paired task evidence. Bootstrap intervals describe the current task sample only; they are not population-level significance claims.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_paired_effects_markdown(result), encoding="utf-8")


def _paired_rows(run_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task: dict[str, dict[str, dict[str, Any]]] = {}
    for row in run_rows:
        by_task.setdefault(str(row["task_id"]), {})[str(row["prompt_type"])] = row

    paired = []
    for task_id, prompts in sorted(by_task.items()):
        baseline = prompts.get("baseline")
        intervention = prompts.get("intervention")
        if not baseline or not intervention:
            continue
        row = {"task_id": task_id}
        for metric, config in METRICS.items():
            field = config["field"]
            row[metric] = float(intervention[field]) - float(baseline[field])
        paired.append(row)
    return paired


def _metric_effect(
    study: str,
    metric: str,
    paired_rows: list[dict[str, Any]],
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    config = METRICS[metric]
    direction = int(config["direction"])
    values = [float(row[metric]) for row in paired_rows]
    improved = sum(value * direction > 0 for value in values)
    regressed = sum(value * direction < 0 for value in values)
    unchanged = sum(value == 0 for value in values)
    ci_low, ci_high = _bootstrap_mean_ci(values, bootstrap_samples, seed + _stable_offset(study, metric))
    return {
        "study": study,
        "metric": metric,
        "label": config["label"],
        "direction": direction,
        "n": len(values),
        "improved": improved,
        "regressed": regressed,
        "unchanged": unchanged,
        "avg_delta": round(mean(values), 4) if values else 0,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "sign_test_p": _two_sided_sign_test_p(improved, regressed),
    }


def _bootstrap_mean_ci(values: list[float], samples: int, seed: int) -> tuple[float, float]:
    if not values:
        return 0, 0
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(samples):
        means.append(mean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    low_index = int(0.025 * (samples - 1))
    high_index = int(0.975 * (samples - 1))
    return round(means[low_index], 4), round(means[high_index], 4)


def _two_sided_sign_test_p(improved: int, regressed: int) -> float | None:
    n = improved + regressed
    if n == 0:
        return None
    observed = min(improved, regressed)
    probability = 2 * sum(comb(n, k) for k in range(observed + 1)) / (2 ** n)
    return round(min(1.0, probability), 6)


def _metric_lookup(rows: list[dict[str, Any]], study: str) -> dict[str, dict[str, Any]]:
    return {row["metric"]: row for row in rows if row["study"] == study}


def _metric_row(row: dict[str, Any]) -> str:
    p_value = "-" if row["sign_test_p"] is None else _fmt(row["sign_test_p"])
    return (
        f"| {row['metric']} | {row['n']} | {row['improved']} | {row['regressed']} | {row['unchanged']} | "
        f"{_fmt(row['avg_delta'])} | [{_fmt(row['ci_low'])}, {_fmt(row['ci_high'])}] | {p_value} |"
    )


def _stable_offset(*parts: str) -> int:
    return sum((index + 1) * ord(char) for index, char in enumerate("::".join(parts)))


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value / 1000:.1f}k"
        return f"{value:.4g}"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paired baseline-to-intervention effects.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    args = parser.parse_args()

    result = build_paired_effects_audit(bootstrap_samples=args.bootstrap_samples, seed=args.seed)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_paired_effects_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
