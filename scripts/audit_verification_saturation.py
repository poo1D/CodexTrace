from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


NON_ABLATION_TIERS = (
    ("full30", Path("benchmark/pilot/full30-real/aggregate.json"), "ordinary seed pilot"),
    ("hard10", Path("benchmark/hard/pilot/hard10-real/aggregate.json"), "hard-tier pilot"),
    ("hard30", Path("benchmark/hard/pilot/hard30-real/aggregate.json"), "submission hard-tier pilot"),
    ("process-stress", Path("benchmark/process-stress/pilot/full-real/aggregate.json"), "observable-process stress pilot"),
    ("verification-lift", Path("benchmark/verification-lift/pilot/full-real/aggregate.json"), "weak optional-verification pilot"),
    ("verification-lift-v2", Path("benchmark/verification-lift-v2/pilot/full-real/aggregate.json"), "ordinary-baseline retest"),
)
ABLATION_TIER = ("verification-ablation", Path("benchmark/verification-ablation/pilot/full-real/aggregate.json"))


def build_verification_saturation_audit(
    non_ablation_tiers: tuple[tuple[str, Path, str], ...] = NON_ABLATION_TIERS,
    ablation_tier: tuple[str, Path] = ABLATION_TIER,
) -> dict[str, Any]:
    rows = []
    for tier, path, description in non_ablation_tiers:
        aggregate = _read_json(path)
        row = _verification_row(tier, path, aggregate, description)
        row["saturated"] = (
            row["baseline_verification_rate"] == 1
            and row["intervention_verification_rate"] == 1
            and row["baseline_success_check_verification_rate"] == 1
            and row["intervention_success_check_verification_rate"] == 1
            and row["verification_delta"] == 0
            and row["success_check_verification_delta"] == 0
        )
        rows.append(row)

    ablation_name, ablation_path = ablation_tier
    ablation = _verification_row(ablation_name, ablation_path, _read_json(ablation_path), "no-verify mechanism ablation")
    ablation["saturated"] = False
    ablation["mechanism_positive"] = (
        ablation["baseline_verification_rate"] == 0
        and ablation["intervention_verification_rate"] == 1
        and ablation["baseline_success_check_verification_rate"] == 0
        and ablation["intervention_success_check_verification_rate"] == 1
        and ablation["verification_delta"] == 1
        and ablation["success_check_verification_delta"] == 1
    )

    return {
        "summary": {
            "ready": all(row["saturated"] for row in rows) and ablation["mechanism_positive"],
            "non_ablation_tier_count": len(rows),
            "saturated_non_ablation_tier_count": sum(1 for row in rows if row["saturated"]),
            "ablation_mechanism_positive": ablation["mechanism_positive"],
            "ordinary_verification_lift_supported": any(row["verification_delta"] > 0 for row in rows),
            "ordinary_exact_verification_lift_supported": any(row["success_check_verification_delta"] > 0 for row in rows),
            "claim_boundary": "ordinary and weak-baseline pilots are saturated; no-verify ablation is mechanism-only",
        },
        "non_ablation_tiers": rows,
        "ablation": ablation,
    }


def render_verification_saturation_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    ablation = result["ablation"]
    lines = [
        "# Verification Saturation Audit",
        "",
        "This generated audit checks whether stored non-ablation Codex pilots leave any rate headroom for an ordinary verification-rate-lift claim.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Non-ablation tiers saturated: {summary['saturated_non_ablation_tier_count']} / {summary['non_ablation_tier_count']}",
        f"- Ordinary verification-rate lift supported: {'yes' if summary['ordinary_verification_lift_supported'] else 'no'}",
        f"- Ordinary exact success-check verification lift supported: {'yes' if summary['ordinary_exact_verification_lift_supported'] else 'no'}",
        f"- No-verify ablation mechanism positive: {'yes' if summary['ablation_mechanism_positive'] else 'no'}",
        f"- Claim boundary: {summary['claim_boundary']}",
        "",
        "## Non-Ablation Tiers",
        "",
        "| Tier | Runs | Baseline broad | Intervention broad | Broad delta | Baseline exact | Intervention exact | Exact delta | Saturated |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["non_ablation_tiers"]:
        lines.append(
            f"| {row['tier']} | {row['runs']} | {row['baseline_verification_rate']:.2f} | "
            f"{row['intervention_verification_rate']:.2f} | {row['verification_delta']:.2f} | "
            f"{row['baseline_success_check_verification_rate']:.2f} | "
            f"{row['intervention_success_check_verification_rate']:.2f} | "
            f"{row['success_check_verification_delta']:.2f} | {'yes' if row['saturated'] else 'no'} |"
        )

    lines.extend([
        "",
        "## Mechanism Ablation",
        "",
        "| Tier | Runs | Baseline broad | Intervention broad | Broad delta | Baseline exact | Intervention exact | Exact delta | Interpretation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        (
            f"| {ablation['tier']} | {ablation['runs']} | {ablation['baseline_verification_rate']:.2f} | "
            f"{ablation['intervention_verification_rate']:.2f} | {ablation['verification_delta']:.2f} | "
            f"{ablation['baseline_success_check_verification_rate']:.2f} | "
            f"{ablation['intervention_success_check_verification_rate']:.2f} | "
            f"{ablation['success_check_verification_delta']:.2f} | mechanism-only, not ordinary baseline |"
        ),
        "",
        "Interpretation: the stored ordinary and weak-baseline pilots do not support a verification-rate-lift finding because broad and exact visible-success-check verification are already saturated. The no-verify ablation shows harness control over verification behavior but cannot close the ordinary-baseline claim.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_verification_saturation_markdown(result), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verification_row(tier: str, path: Path, aggregate: dict[str, Any], description: str) -> dict[str, Any]:
    baseline = aggregate["summary"]["baseline"]
    intervention = aggregate["summary"]["intervention"]
    deltas = aggregate["deltas"]
    return {
        "tier": tier,
        "description": description,
        "path": str(path),
        "runs": int(baseline["n"]) + int(intervention["n"]),
        "baseline_verification_rate": float(baseline["verification_rate"]),
        "intervention_verification_rate": float(intervention["verification_rate"]),
        "verification_delta": float(deltas["verification_rate"]),
        "baseline_success_check_verification_rate": float(baseline["success_check_verification_rate"]),
        "intervention_success_check_verification_rate": float(intervention["success_check_verification_rate"]),
        "success_check_verification_delta": float(deltas["success_check_verification_rate"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit verification-rate saturation across stored CodexTrace pilots.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_verification_saturation_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_verification_saturation_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
