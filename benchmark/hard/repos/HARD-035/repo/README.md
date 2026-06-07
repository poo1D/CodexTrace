# retry-policy

`plan_retries(response, attempts, base_delay=1, max_delay=None)`
returns retry delays in seconds.

Existing behavior:

- Exponential backoff starts at `base_delay`.
- `attempts=3` with `base_delay=1` returns `[1, 2, 4]`.

Required behavior:

- Retry only status `408`, `409`, `425`, `429`, and `5xx`.
- Non-retryable statuses return `[]`.
- `Retry-After` may be seconds or an HTTP-date.
- `max_delay` caps every planned delay.
- The response dictionary must not be mutated.
