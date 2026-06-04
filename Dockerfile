FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY codex_trace ./codex_trace
COPY demo ./demo
RUN pip install --no-cache-dir .

ENTRYPOINT ["codex-trace"]
CMD ["diagnose", "demo/failing-codex-trace.jsonl"]
