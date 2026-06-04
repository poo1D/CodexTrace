.PHONY: test diagnose web-build

test:
	pytest

diagnose:
	codex-trace diagnose demo/failing-codex-trace.jsonl

web-build:
	cd web && npm install && npm run build
