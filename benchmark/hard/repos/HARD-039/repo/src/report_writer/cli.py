import argparse
import json
import sys
from pathlib import Path

from .render import render_json, render_text


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", choices=["json", "text"], required=True)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    report = json.loads(input_path.read_text(encoding="utf-8"))
    if report.get("title") == "RAISE":
        raise RuntimeError("cannot render report")

    if args.format == "json":
        content = render_json(report)
    else:
        content = render_text(report)

    output_path = Path(args.output)
    output_path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
