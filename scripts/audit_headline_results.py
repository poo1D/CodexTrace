from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_RESULTS_SUMMARY = Path("docs/results_summary.json")


def build_headline_results(results_summary_path: Path = DEFAULT_RESULTS_SUMMARY) -> dict[str, Any]:
    data = json.loads(results_summary_path.read_text(encoding="utf-8"))

    rows = [
        _row(data, "hard10_success", "Hard10 success rate", "hard10", "success_rate", "pilot-qualified success lift"),
        _row(data, "hard30_success", "Hard30 success rate", "hard30", "success_rate", "flat hard30 success"),
        _row(data, "hard30_verification", "Hard30 verification rate", "hard30", "verification_rate", "saturated; no ordinary verification lift"),
        _row(data, "hard30_repeated_tool_calls", "Hard30 repeated tool calls", "hard30", "avg_repeated_tool_calls", "supported waste reduction"),
        _row(data, "hard30_unresolved_error_rate", "Hard30 unresolved error rate", "hard30", "unresolved_error_rate", "no unresolved-error movement"),
        _row(data, "hard30_token_usage", "Hard30 token usage", "hard30", "avg_token_usage", "supported waste reduction"),
        _row(data, "verification_lift_v2_verification", "Verification-lift-v2 verification", "verification_lift_v2", "verification_rate", "ordinary-baseline retest is saturated"),
        _row(data, "verification_lift_v2_exact_verification", "Verification-lift-v2 exact verification", "verification_lift_v2", "success_check_verification_rate", "exact visible success-check verification is saturated"),
        _row(data, "no_verify_ablation_verification", "No-verify ablation verification", "verification_ablation", "verification_rate", "mechanism check only; not an ordinary baseline"),
        _row(data, "no_verify_ablation_exact_verification", "No-verify ablation exact verification", "verification_ablation", "success_check_verification_rate", "mechanism check only; not an ordinary baseline"),
    ]
    by_id = {row["id"]: row for row in rows}
    summary = {
        "ready": (
            by_id["hard30_repeated_tool_calls"]["delta"] < 0
            and by_id["hard30_token_usage"]["delta"] < 0
            and by_id["hard30_verification"]["delta"] == 0
            and by_id["verification_lift_v2_verification"]["delta"] == 0
            and by_id["verification_lift_v2_exact_verification"]["delta"] == 0
            and by_id["no_verify_ablation_verification"]["delta"] > 0
            and by_id["no_verify_ablation_exact_verification"]["delta"] > 0
        ),
        "ordinary_verification_rate_lift_supported": False,
        "waste_reduction_supported": True,
        "no_verify_ablation_lift_observed": True,
        "source": str(results_summary_path),
        "boundary": "ordinary verification-rate lift is unsupported; no-verify ablation is a mechanism check only, not an ordinary baseline",
    }
    return {"summary": summary, "rows": rows}


def render_headline_results_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Headline Results Table",
        "",
        "This generated table replaces the original expected-results sketch with the current stored evidence.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Ordinary verification-rate lift supported: {'yes' if summary['ordinary_verification_rate_lift_supported'] else 'no'}",
        f"- Waste reduction supported: {'yes' if summary['waste_reduction_supported'] else 'no'}",
        f"- No-verify ablation lift observed: {'yes' if summary['no_verify_ablation_lift_observed'] else 'no'}",
        f"- Boundary: {summary['boundary']}",
        f"- Source: `{summary['source']}`",
        "",
        "## Table",
        "",
        "| Metric | Baseline | Intervention | Delta | Interpretation |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in result["rows"]:
        lines.append(
            f"| `{row['id']}` | {_format_value(row)} | {_format_value(row, 'intervention')} | {_format_delta(row)} | {row['interpretation']} |"
        )
    lines.extend([
        "",
        "Interpretation: the hard30 and ordinary-baseline verification-lift-v2 pilots support waste reduction, not an ordinary verification-rate lift. The no-verify ablation demonstrates harness control over verification behavior under an artificial baseline condition, so it should not be reported as ordinary-baseline evidence.",
    ])
    return "\n".join(lines) + "\n"


def _row(data: dict[str, Any], row_id: str, label: str, pilot: str, metric: str, interpretation: str) -> dict[str, Any]:
    baseline = data[pilot]["summary"]["baseline"][metric]
    intervention = data[pilot]["summary"]["intervention"][metric]
    return {
        "id": row_id,
        "label": label,
        "pilot": pilot,
        "metric": metric,
        "baseline": baseline,
        "intervention": intervention,
        "delta": round(intervention - baseline, 4),
        "interpretation": interpretation,
    }


def _format_value(row: dict[str, Any], key: str = "baseline") -> str:
    value = row[key]
    if row["metric"] == "avg_token_usage":
        return f"{value / 1000:.1f}k"
    if row["metric"].endswith("_rate"):
        return f"{value:.2f}"
    return f"{value:.2f}"


def _format_delta(row: dict[str, Any]) -> str:
    value = row["delta"]
    if row["metric"] == "avg_token_usage":
        return f"{value / 1000:+.1f}k"
    if row["metric"].endswith("_rate"):
        return f"{value:+.2f}"
    return f"{value:+.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the compact headline-results table from stored CodexTrace summaries.")
    parser.add_argument("--results-summary", type=Path, default=DEFAULT_RESULTS_SUMMARY)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_headline_results(args.results_summary)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_headline_results_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
