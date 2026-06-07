# sliding-limiter

`SlidingLimiter(limit, window_seconds, clock=None)` decides
whether a user may perform another action.

Public API:

- `allow(user_id, now=None)` returns `True` when the request is
  accepted and `False` when it is rate-limited.
- If `now` is omitted, the limiter must call the injected
  `clock` exactly once for that decision.
- The rolling window is per user.
- Events at exactly `now - window_seconds` are expired.
- Rejected requests must not be recorded.
