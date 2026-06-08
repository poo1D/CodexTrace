#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TRACE="demo/failing-codex-trace.jsonl"
OUTPUT_DIR="${CODEXTRACE_DEMO_DIR:-/tmp/codextrace-demo}"
UPDATE_UI=0
WEB_REPORT="web/public/report.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      if [[ $# -lt 2 ]]; then
        echo "error: --output-dir requires a directory" >&2
        exit 2
      fi
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --update-ui)
      UPDATE_UI=1
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [TRACE] [--output-dir DIR] [--update-ui]"
      exit 0
      ;;
    *)
      TRACE="$1"
      shift
      ;;
  esac
done

mkdir -p "$OUTPUT_DIR"
REPORT_JSON="$OUTPUT_DIR/demo-report.json"
REPORT_MD="$OUTPUT_DIR/demo-report.md"

if [[ -x ".venv/bin/python" ]]; then
  CODEX_TRACE=(".venv/bin/python" -m codex_trace.cli)
else
  CODEX_TRACE=(python3 -m codex_trace.cli)
fi

echo "== CodexTrace demo =="
echo "Input trace: $TRACE"
echo "Output dir: $OUTPUT_DIR"
echo

echo "1. Generate JSON diagnosis"
PYTHONPATH=. "${CODEX_TRACE[@]}" diagnose "$TRACE" --format json -o "$REPORT_JSON"

echo "2. Generate Markdown diagnosis"
PYTHONPATH=. "${CODEX_TRACE[@]}" diagnose "$TRACE" --format markdown -o "$REPORT_MD"

if [[ "$UPDATE_UI" -eq 1 ]]; then
  echo "3. Feed the Web UI"
  cp "$REPORT_JSON" "$WEB_REPORT"
else
  echo "3. Skip Web UI fixture update"
fi

echo
echo "Demo artifacts:"
echo "- $REPORT_JSON"
echo "- $REPORT_MD"
if [[ "$UPDATE_UI" -eq 1 ]]; then
  echo "- $WEB_REPORT"
fi
echo
echo "Preview CLI report:"
sed -n '1,80p' "$REPORT_MD"
echo
echo "Run the visual replay:"
echo "  $0 $TRACE --update-ui"
echo "  cd web && npm install && npm run dev"
echo "  open the printed Vite URL, usually http://localhost:5173"
