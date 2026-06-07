# validation-pipeline

`validateRegistration(input)` returns `{ valid, errors, value }`.

Validation order is `email`, `password`, `roles`.

Rules:

- `email` is required and must contain `@`.
- `password` is required and must be at least 8 characters.
- `roles` must be a non-empty array.
- Valid output normalizes email by trimming and lowercasing it.
- Invalid output keeps `value` as `null` and reports all errors in validation order.
