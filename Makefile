.PHONY: test diagnose demo research-demo smoke-dry-run web-build

PYTHON ?= python3
CODEX_TRACE = PYTHONPATH=. $(PYTHON) -m codex_trace.cli

test:
	$(PYTHON) -m pytest

diagnose:
	$(CODEX_TRACE) diagnose demo/failing-codex-trace.jsonl

demo:
	./scripts/demo.sh

research-demo:
	$(CODEX_TRACE) research aggregate benchmark/runs.example.jsonl \
		--json-output reports/example-aggregate.json \
		--markdown-output reports/example-aggregate.md \
		--csv-output reports/example-runs.csv

smoke-dry-run:
	$(CODEX_TRACE) research run \
		--tasks benchmark/smoke/tasks.jsonl \
		--output-dir runs/smoke-dry \
		--dry-run

web-build:
	cd web && npm install && npm run build
