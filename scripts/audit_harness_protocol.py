from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


INTERVENTION_PROMPTS = (
    Path("benchmark/prompts/intervention.txt"),
    Path("benchmark/verification-lift/prompts/intervention.txt"),
    Path("benchmark/verification-lift-v2/prompts/intervention.txt"),
    Path("benchmark/verification-ablation/prompts/intervention.txt"),
)
DEFAULT_PROTOCOL = Path("docs/experiment_protocol.md")
DEFAULT_HARD30_REPORT = Path("benchmark/hard/pilot/hard30-real/paper-report-labeled.json")

REQUIRED_RULES = (
    {
        "id": "inspect_first",
        "prompt_any": ("Inspect first", "Inspect the smallest relevant files"),
        "protocol_phrase": "inspect first",
    },
    {
        "id": "minimal_edit",
        "prompt_any": ("intended minimal edit", "minimal edit that satisfies"),
        "protocol_phrase": "minimal edit",
    },
    {
        "id": "post_edit_verification",
        "prompt_any": ("Run a focused verification command after the edit", "Run the visible success check after editing"),
        "protocol_phrase": "run post-edit verification",
    },
    {
        "id": "failure_diagnosis_before_retry",
        "prompt_any": ("diagnose the cause before retrying", "diagnose the failure before retrying"),
        "protocol_phrase": "diagnose before retrying failed commands",
    },
    {
        "id": "finish_with_evidence",
        "prompt_any": ("Finish only after citing concrete evidence", "Finish only after citing the final verification command"),
        "protocol_phrase": "finish only with evidence",
    },
)


def _check_any(text: str, phrases: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(phrase.lower() in normalized for phrase in phrases)


def build_harness_protocol_audit(
    intervention_prompts: tuple[Path, ...] = INTERVENTION_PROMPTS,
    protocol_path: Path = DEFAULT_PROTOCOL,
    hard30_report_path: Path = DEFAULT_HARD30_REPORT,
) -> dict[str, Any]:
    protocol_text = protocol_path.read_text(encoding="utf-8")
    hard30_report = json.loads(hard30_report_path.read_text(encoding="utf-8"))
    prompt_rows = []
    for prompt_path in intervention_prompts:
        text = prompt_path.read_text(encoding="utf-8")
        rule_rows = []
        for rule in REQUIRED_RULES:
            rule_rows.append({
                "id": rule["id"],
                "covered": _check_any(text, rule["prompt_any"]),
                "accepted_phrases": list(rule["prompt_any"]),
            })
        prompt_rows.append({
            "path": str(prompt_path),
            "rule_count": len(rule_rows),
            "covered_rule_count": sum(1 for row in rule_rows if row["covered"]),
            "covered": all(row["covered"] for row in rule_rows),
            "rules": rule_rows,
        })

    protocol_rules = []
    protocol_lower = protocol_text.lower()
    for rule in REQUIRED_RULES:
        protocol_rules.append({
            "id": rule["id"],
            "phrase": rule["protocol_phrase"],
            "covered": rule["protocol_phrase"].lower() in protocol_lower,
        })

    run_proxy_checks = _run_proxy_checks(hard30_report)
    return {
        "summary": {
            "ready": (
                all(row["covered"] for row in prompt_rows)
                and all(row["covered"] for row in protocol_rules)
                and all(row["passed"] for row in run_proxy_checks)
            ),
            "prompt_count": len(prompt_rows),
            "covered_prompt_count": sum(1 for row in prompt_rows if row["covered"]),
            "rule_count": len(REQUIRED_RULES),
            "protocol_rule_count": sum(1 for row in protocol_rules if row["covered"]),
            "protocol_path": str(protocol_path),
            "run_proxy_count": len(run_proxy_checks),
            "run_proxy_passed": sum(1 for row in run_proxy_checks if row["passed"]),
            "hard30_report_path": str(hard30_report_path),
        },
        "prompts": prompt_rows,
        "protocol_rules": protocol_rules,
        "run_proxy_checks": run_proxy_checks,
    }


def render_harness_protocol_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Harness Protocol Audit",
        "",
        "This generated audit checks that intervention prompt templates preserve the harness constraints named in the experiment design.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Intervention prompts covered: {summary['covered_prompt_count']} / {summary['prompt_count']}",
        f"- Harness rules per prompt: {summary['rule_count']}",
        f"- Protocol rules covered: {summary['protocol_rule_count']} / {summary['rule_count']}",
        f"- Run-level proxy checks passed: {summary['run_proxy_passed']} / {summary['run_proxy_count']}",
        f"- Experiment protocol: `{summary['protocol_path']}`",
        f"- Hard30 report: `{summary['hard30_report_path']}`",
        "",
        "## Prompt Coverage",
        "",
        "| Prompt | Covered rules | Ready |",
        "| --- | ---: | --- |",
    ]
    for prompt in result["prompts"]:
        lines.append(
            f"| `{prompt['path']}` | {prompt['covered_rule_count']} / {prompt['rule_count']} | {'yes' if prompt['covered'] else 'no'} |"
        )
    lines.extend([
        "",
        "## Rule Coverage",
        "",
        "| Rule | Protocol covered |",
        "| --- | --- |",
    ])
    for row in result["protocol_rules"]:
        lines.append(f"| `{row['id']}` | {'yes' if row['covered'] else 'no'} |")
    lines.extend([
        "",
        "## Run-Level Proxy Checks",
        "",
        "| Constraint proxy | Baseline | Intervention | Delta | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ])
    for row in result["run_proxy_checks"]:
        lines.append(
            f"| `{row['id']}` | {_fmt(row['baseline'])} | {_fmt(row['intervention'])} | "
            f"{_fmt(row['delta'])} | {'pass' if row['passed'] else 'fail'} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit verifies prompt-template and protocol coverage of the harness constraints, then links those constraints to hard30 aggregate trace-metric proxies. It does not prove that every model run obeyed each instruction.",
    ])
    return "\n".join(lines) + "\n"


def _run_proxy_checks(report: dict[str, Any]) -> list[dict[str, Any]]:
    baseline = report["aggregate"]["summary"]["baseline"]
    intervention = report["aggregate"]["summary"]["intervention"]
    return [
        _metric_check("post_edit_verification_proxy", baseline, intervention, "success_check_verification_rate", "ge"),
        _metric_check("verification_rate_proxy", baseline, intervention, "verification_rate", "ge"),
        _metric_check("minimal_edit_proxy", baseline, intervention, "avg_edit_events", "le"),
        _metric_check("repetitive_exploration_proxy", baseline, intervention, "avg_repeated_tool_calls", "le"),
        _metric_check("token_waste_proxy", baseline, intervention, "avg_token_usage", "le"),
        _metric_check("failed_command_proxy", baseline, intervention, "avg_command_failures", "le"),
    ]


def _metric_check(
    check_id: str,
    baseline: dict[str, Any],
    intervention: dict[str, Any],
    metric: str,
    direction: str,
) -> dict[str, Any]:
    base_value = float(baseline[metric])
    intervention_value = float(intervention[metric])
    delta = intervention_value - base_value
    passed = intervention_value >= base_value if direction == "ge" else intervention_value <= base_value
    return {
        "id": check_id,
        "metric": metric,
        "baseline": base_value,
        "intervention": intervention_value,
        "delta": delta,
        "passed": passed,
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value / 1000:.1f}k"
        return f"{value:.4g}"
    return str(value)


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_harness_protocol_markdown(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit harness intervention protocol coverage.")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--hard30-report", type=Path, default=DEFAULT_HARD30_REPORT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_harness_protocol_audit(protocol_path=args.protocol, hard30_report_path=args.hard30_report)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_harness_protocol_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
