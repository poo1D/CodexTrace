.PHONY: test diagnose demo research-demo web-build

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

web-build:
	cd web && npm install && npm run build
