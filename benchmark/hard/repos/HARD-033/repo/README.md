# log-redactor

Redact credentials before logs are persisted.

Public API:

- `redact_text(text)`
- `redact_event(event)`

Sensitive fields include `token`, `apiKey`, `password`, and
`authorization`, matched case-insensitively. Redaction should
replace credential values with `[REDACTED]` while preserving useful
non-sensitive context. `redact_event` must return a redacted copy
and must not mutate the input event.
