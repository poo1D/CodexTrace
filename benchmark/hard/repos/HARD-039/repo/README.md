# cli-report-writer

The CLI reads a JSON report input and writes either JSON or text.

Usage:

```bash
python3 -m report_writer.cli --input fixtures/report.json --output out/report.json --format json
python3 -m report_writer.cli --input fixtures/report.json --output out/report.txt --format text
```

Requirements:

- Work from the repository root or any nested current directory.
- Resolve relative input paths against the repository root.
- Create parent directories for the output path.
- JSON output must use sorted keys and end with a newline.
- Text output must use the documented section order.
- Writes must be atomic: a rendering failure must leave existing
  output unchanged and remove temporary siblings.
