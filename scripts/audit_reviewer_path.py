from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_SUBMISSION_PACKAGE = Path("docs/submission_package.json")
DEFAULT_README = Path("README.md")
DEFAULT_ARTIFACT_GUIDE = Path("docs/artifact_guide.md")
DEFAULT_REPRO_CHECKLIST = Path("docs/reproducibility_checklist.md")


def build_reviewer_path_audit(
    submission_package_path: Path = DEFAULT_SUBMISSION_PACKAGE,
    readme_path: Path = DEFAULT_README,
    artifact_guide_path: Path = DEFAULT_ARTIFACT_GUIDE,
    reproducibility_checklist_path: Path = DEFAULT_REPRO_CHECKLIST,
) -> dict[str, Any]:
    package = json.loads(submission_package_path.read_text(encoding="utf-8"))
    required_files = list(package["required_files"])
    texts = {
        "README.md": readme_path.read_text(encoding="utf-8"),
        "docs/artifact_guide.md": artifact_guide_path.read_text(encoding="utf-8"),
        "docs/reproducibility_checklist.md": reproducibility_checklist_path.read_text(encoding="utf-8"),
    }
    coverage = []
    for required in required_files:
        present_in = sorted(name for name, text in texts.items() if required in text)
        coverage.append({
            "path": required,
            "present_in": present_in,
            "covered": bool(present_in),
        })

    missing = [row for row in coverage if not row["covered"]]
    guide_required = {
        "docs/submission_package.md",
        "docs/paper_claim_audit.md",
        "docs/claim_text_guard.md",
        "docs/paper_number_guard.md",
        "docs/reproducibility_checklist.md",
    }
    guide_missing = sorted(
        path for path in guide_required
        if "docs/artifact_guide.md" not in _present_in(coverage, path)
    )
    checklist_missing = sorted(
        row["path"] for row in coverage
        if "docs/reproducibility_checklist.md" not in row["present_in"]
        and row["path"] != "docs/reproducibility_checklist.md"
        and row["path"] != "README.md"
    )
    return {
        "ok": not missing and not guide_missing and not checklist_missing,
        "summary": {
            "required_files": len(required_files),
            "missing": len(missing),
            "guide_missing": len(guide_missing),
            "checklist_missing": len(checklist_missing),
        },
        "coverage": coverage,
        "missing": missing,
        "guide_missing": guide_missing,
        "checklist_missing": checklist_missing,
    }


def _present_in(coverage: list[dict[str, Any]], path: str) -> list[str]:
    for row in coverage:
        if row["path"] == path:
            return list(row["present_in"])
    return []


def render_reviewer_path_audit_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Reviewer Path Audit",
        "",
        "This generated guard checks that required reviewer files are discoverable from the paper-facing entry points.",
        "",
        f"OK: {'yes' if result['ok'] else 'no'}",
        f"Required files: {result['summary']['required_files']}",
        f"Missing everywhere: {result['summary']['missing']}",
        f"Missing from artifact guide required set: {result['summary']['guide_missing']}",
        f"Missing from reproducibility checklist: {result['summary']['checklist_missing']}",
        "",
        "| Required file | Covered | Present in |",
        "| --- | --- | --- |",
    ]
    for row in result["coverage"]:
        present_in = ", ".join(f"`{path}`" for path in row["present_in"]) or "-"
        lines.append(f"| `{row['path']}` | {'yes' if row['covered'] else 'no'} | {present_in} |")
    if result["guide_missing"]:
        lines.extend(["", "## Missing From Artifact Guide", ""])
        lines.extend(f"- `{path}`" for path in result["guide_missing"])
    if result["checklist_missing"]:
        lines.extend(["", "## Missing From Reproducibility Checklist", ""])
        lines.extend(f"- `{path}`" for path in result["checklist_missing"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit reviewer-path coverage for required paper artifacts.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_reviewer_path_audit()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_reviewer_path_audit_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
