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
    ("hard10", Path("benchmark/hard/pilot/hard10-real/aggregate.json"), "early hard-tier pilot"),
    ("hard30", Path("benchmark/hard/pilot/hard30-real/aggregate.json"), "paper-facing hard-tier pilot"),
    ("process-stress", Path("benchmark/process-stress/pilot/full-real/aggregate.json"), "observable-process stress pilot"),
    ("verification-lift", Path("benchmark/verification-lift/pilot/full-real/aggregate.json"), "weak optional-verification pilot"),
    ("verification-lift-v2", Path("benchmark/verification-lift-v2/pilot/full-real/aggregate.json"), "ordinary-baseline retest"),
)
ABLATION_TIER = ("verification-ablation", Path("benchmark/verification-ablation/pilot/full-real/aggregate.json"))


def build_verification_behavior_audit(
    non_ablation_tiers: tuple[tuple[str, Path, str], ...] = NON_ABLATION_TIERS,
    ablation_tier: tuple[str, Path] = ABLATION_TIER,
) -> dict[str, Any]:
    rows = []
    for tier, path, description in non_ablation_tiers:
        row = _behavior_row(tier, path, _read_json(path), description)
        row["rate_saturated"] = (
            row["baseline_verification_rate"] == 1
            and row["intervention_verification_rate"] == 1
            and row["baseline_exact_verification_rate"] == 1
            and row["intervention_exact_verification_rate"] == 1
            and row["verification_delta"] == 0
            and row["exact_verification_delta"] == 0
        )
        row["earlier_verification"] = row["time_to_first_test_delta"] < 0
        row["leaner_verify_phase"] = row["verify_events_delta"] < 0
        rows.append(row)

    ablation_name, ablation_path = ablation_tier
    ablation = _behavior_row(ablation_name, ablation_path, _read_json(ablation_path), "no-verify mechanism ablation")
    ablation["mechanism_positive"] = (
        ablation["baseline_verification_rate"] == 0
        and ablation["intervention_verification_rate"] == 1
        and ablation["baseline_exact_verification_rate"] == 0
        and ablation["intervention_exact_verification_rate"] == 1
    )

    saturated_count = sum(1 for row in rows if row["rate_saturated"])
    earlier_count = sum(1 for row in rows if row["earlier_verification"])
    leaner_count = sum(1 for row in rows if row["leaner_verify_phase"])
    return {
        "summary": {
            "ready": (
                saturated_count == len(rows)
                and earlier_count == len(rows)
                and leaner_count == len(rows)
                and ablation["mechanism_positive"]
            ),
            "non_ablation_tier_count": len(rows),
            "saturated_non_ablation_tier_count": saturated_count,
            "earlier_verification_count": earlier_count,
            "leaner_verify_phase_count": leaner_count,
            "ablation_mechanism_positive": ablation["mechanism_positive"],
            "interpretation": (
                "ordinary verification rates are saturated; intervention changes verification timing and process cost, "
                "not the rate or depth of verification"
            ),
        },
        "non_ablation_tiers": rows,
        "ablation": ablation,
        "claim_boundaries": _claim_boundaries(rows, ablation),
    }


def render_verification_behavior_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Verification Behavior Audit",
        "",
        "This generated audit separates verification-rate lift from verification behavior under saturated ordinary pilots.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Non-ablation tiers saturated: {summary['saturated_non_ablation_tier_count']} / {summary['non_ablation_tier_count']}",
        f"- Non-ablation tiers with earlier verification: {summary['earlier_verification_count']} / {summary['non_ablation_tier_count']}",
        f"- Non-ablation tiers with leaner verify phase: {summary['leaner_verify_phase_count']} / {summary['non_ablation_tier_count']}",
        f"- No-verify ablation mechanism positive: {'yes' if summary['ablation_mechanism_positive'] else 'no'}",
        f"- Interpretation: {summary['interpretation']}",
        "",
        "## Non-Ablation Verification Behavior",
        "",
        "| Tier | Baseline broad | Intervention broad | Baseline exact | Intervention exact | Time to first test delta | Verify-event delta | Interpretation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["non_ablation_tiers"]:
        lines.append(
            f"| {row['tier']} | {row['baseline_verification_rate']:.2f} | "
            f"{row['intervention_verification_rate']:.2f} | {row['baseline_exact_verification_rate']:.2f} | "
            f"{row['intervention_exact_verification_rate']:.2f} | {_fmt(row['time_to_first_test_delta'])} | "
            f"{_fmt(row['verify_events_delta'])} | saturated rate; earlier and leaner verification path |"
        )

    ablation = result["ablation"]
    lines.extend([
        "",
        "## Mechanism Ablation",
        "",
        "| Tier | Baseline broad | Intervention broad | Baseline exact | Intervention exact | Interpretation |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
        (
            f"| {ablation['tier']} | {ablation['baseline_verification_rate']:.2f} | "
            f"{ablation['intervention_verification_rate']:.2f} | {ablation['baseline_exact_verification_rate']:.2f} | "
            f"{ablation['intervention_exact_verification_rate']:.2f} | mechanism-only evidence that the harness can force verification under an artificial no-verify baseline |"
        ),
        "",
        "## Claim Boundary Verdicts",
        "",
        "| Claim | Verdict | Evidence | Safe wording |",
        "| --- | --- | --- | --- |",
    ])
    for row in result["claim_boundaries"]:
        lines.append(
            f"| {row['claim']} | `{row['verdict']}` | {row['evidence']} | {row['safe_wording']} |"
        )

    lines.extend([
        "",
        "Interpretation: this audit preserves the negative verification-rate result while giving RQ3 a process-level verification-behavior measurement. In the stored ordinary pilots, intervention reaches verification earlier and with fewer verify-phase events; this is leaner verification, not deeper verification.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_verification_behavior_markdown(result), encoding="utf-8")


def _claim_boundaries(rows: list[dict[str, Any]], ablation: dict[str, Any]) -> list[dict[str, str]]:
    tier_count = len(rows)
    saturated = sum(1 for row in rows if row["rate_saturated"])
    earlier = sum(1 for row in rows if row["earlier_verification"])
    leaner = sum(1 for row in rows if row["leaner_verify_phase"])
    return [
        {
            "claim": "Harness intervention improves ordinary-baseline verification rate.",
            "verdict": "unsupported",
            "evidence": f"{saturated}/{tier_count} non-ablation tiers are already saturated at broad and exact verification.",
            "safe_wording": "Report verification-rate saturation, not ordinary verification-rate lift.",
        },
        {
            "claim": "Harness intervention reaches verification earlier under saturated ordinary pilots.",
            "verdict": "supported",
            "evidence": f"{earlier}/{tier_count} non-ablation tiers have lower average time_to_first_test.",
            "safe_wording": "Describe earlier verification as a process-behavior effect under saturated rates.",
        },
        {
            "claim": "Harness intervention makes ordinary-pilot verification deeper.",
            "verdict": "contradicted",
            "evidence": f"{leaner}/{tier_count} non-ablation tiers have fewer verify-phase events under intervention.",
            "safe_wording": "Use leaner verification path, not deeper verification.",
        },
        {
            "claim": "No-verify ablation shows harness control over verification behavior.",
            "verdict": "mechanism-check-only",
            "evidence": (
                "No-verify ablation broad/exact verification changes "
                f"{ablation['baseline_verification_rate']:.2f}->{ablation['intervention_verification_rate']:.2f}."
            ),
            "safe_wording": "Use only as an artificial-baseline mechanism check.",
        },
    ]


def _behavior_row(tier: str, path: Path, aggregate: dict[str, Any], description: str) -> dict[str, Any]:
    baseline = aggregate["summary"]["baseline"]
    intervention = aggregate["summary"]["intervention"]
    deltas = aggregate["deltas"]
    return {
        "tier": tier,
        "description": description,
        "path": str(path),
        "baseline_verification_rate": float(baseline["verification_rate"]),
        "intervention_verification_rate": float(intervention["verification_rate"]),
        "verification_delta": float(deltas["verification_rate"]),
        "baseline_exact_verification_rate": float(baseline["success_check_verification_rate"]),
        "intervention_exact_verification_rate": float(intervention["success_check_verification_rate"]),
        "exact_verification_delta": float(deltas["success_check_verification_rate"]),
        "baseline_time_to_first_test": float(baseline["avg_time_to_first_test"]),
        "intervention_time_to_first_test": float(intervention["avg_time_to_first_test"]),
        "time_to_first_test_delta": float(deltas["avg_time_to_first_test"]),
        "baseline_verify_events": float(baseline["avg_verify_events"]),
        "intervention_verify_events": float(intervention["avg_verify_events"]),
        "verify_events_delta": float(deltas["avg_verify_events"]),
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(value: float) -> str:
    return f"{value:+.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit verification behavior under saturated CodexTrace pilots.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_verification_behavior_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_verification_behavior_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
