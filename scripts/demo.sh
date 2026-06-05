#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TRACE="${1:-demo/failing-codex-trace.jsonl}"
REPORT_JSON="demo/demo-report.json"
REPORT_MD="demo/demo-report.md"
WEB_REPORT="web/public/report.json"

if [[ -x ".venv/bin/python" ]]; then
  CODEX_TRACE=(".venv/bin/python" -m codex_trace.cli)
else
  CODEX_TRACE=(python3 -m codex_trace.cli)
fi

echo "== CodexTrace demo =="
echo "Input trace: $TRACE"
echo

echo "1. Generate JSON diagnosis"
PYTHONPATH=. "${CODEX_TRACE[@]}" diagnose "$TRACE" --format json -o "$REPORT_JSON"

echo "2. Generate Markdown diagnosis"
PYTHONPATH=. "${CODEX_TRACE[@]}" diagnose "$TRACE" --format markdown -o "$REPORT_MD"

echo "3. Feed the Web UI"
cp "$REPORT_JSON" "$WEB_REPORT"

echo
echo "Demo artifacts:"
echo "- $REPORT_JSON"
echo "- $REPORT_MD"
echo "- $WEB_REPORT"
echo
echo "Preview CLI report:"
sed -n '1,80p' "$REPORT_MD"
echo
echo "Run the visual replay:"
echo "  cd web && npm install && npm run dev"
