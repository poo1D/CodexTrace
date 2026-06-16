from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_VALIDITY = Path("docs/validity_threats.json")
DEFAULT_PAPER = Path("docs/paper_draft.md")


def build_limitations_traceability_audit(
    validity_path: Path = DEFAULT_VALIDITY,
    paper_path: Path = DEFAULT_PAPER,
) -> dict[str, Any]:
    validity = json.loads(validity_path.read_text(encoding="utf-8"))
    paper = paper_path.read_text(encoding="utf-8")
    section = _extract_section(paper, "## 9. Threats To Validity", "## 10. Artifact Availability")
    normalized = _normalize(section)

    rows = []
    for threat in validity["threats"]:
        threat_id = str(threat["id"])
        paper_language = str(threat["paper_language"])
        row = {
            "id": threat_id,
            "id_present": _normalize(threat_id) in normalized,
            "paper_language_present": _normalize(paper_language) in normalized,
            "paper_language": paper_language,
        }
        row["covered"] = row["id_present"] and row["paper_language_present"]
        rows.append(row)

    return {
        "summary": {
            "ready": all(row["covered"] for row in rows),
            "threat_count": len(rows),
            "covered_threat_count": sum(1 for row in rows if row["covered"]),
            "validity_path": str(validity_path),
            "paper_path": str(paper_path),
        },
        "threats": rows,
    }


def render_limitations_traceability_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Limitations Traceability Audit",
        "",
        "This generated audit checks that the paper draft's Threats To Validity section carries the safe paper-language claims from the generated validity-threat map.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Threats covered: {summary['covered_threat_count']} / {summary['threat_count']}",
        f"- Validity map: `{summary['validity_path']}`",
        f"- Paper draft: `{summary['paper_path']}`",
        "",
        "## Threat Coverage",
        "",
        "| Threat | ID | Paper language present | Paper language | Covered |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result["threats"]:
        lines.append(
            f"| `{row['id']}` | {'yes' if row['id_present'] else 'no'} | "
            f"{'yes' if row['paper_language_present'] else 'no'} | {row['paper_language']} | "
            f"{'yes' if row['covered'] else 'no'} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit links reviewer-facing validity caveats back into the paper draft. It does not judge whether the prose is sufficient for a particular venue.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_limitations_traceability_markdown(result), encoding="utf-8")


def _extract_section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


def _normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper limitations traceability against the validity-threat map.")
    parser.add_argument("--validity", type=Path, default=DEFAULT_VALIDITY)
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_limitations_traceability_audit(args.validity, args.paper)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_limitations_traceability_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
