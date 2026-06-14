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
) -> dict[str, Any]:
    protocol_text = protocol_path.read_text(encoding="utf-8")
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

    return {
        "summary": {
            "ready": all(row["covered"] for row in prompt_rows) and all(row["covered"] for row in protocol_rules),
            "prompt_count": len(prompt_rows),
            "covered_prompt_count": sum(1 for row in prompt_rows if row["covered"]),
            "rule_count": len(REQUIRED_RULES),
            "protocol_rule_count": sum(1 for row in protocol_rules if row["covered"]),
            "protocol_path": str(protocol_path),
        },
        "prompts": prompt_rows,
        "protocol_rules": protocol_rules,
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
        f"- Experiment protocol: `{summary['protocol_path']}`",
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
        "Interpretation: this audit verifies prompt-template and protocol coverage of the harness constraints. It does not prove that every model run obeyed each instruction; run-level behavior is measured separately through trace metrics and labels.",
    ])
    return "\n".join(lines) + "\n"


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
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_harness_protocol_audit(protocol_path=args.protocol)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_harness_protocol_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
