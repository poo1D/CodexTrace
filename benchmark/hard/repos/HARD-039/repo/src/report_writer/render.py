import json


def render_json(report):
    return json.dumps(report) + "\n"


def render_text(report):
    lines = [report["title"], ""]
    for section in report.get("sections", []):
        lines.append(section["name"])
        lines.append(section["body"])
        lines.append("")
    lines.append("Metrics")
    for key, value in report.get("metrics", {}).items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines) + "\n"
