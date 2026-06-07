# webhook-replay-guard

`verify_event(envelope, keys, store, now)` accepts a signed
webhook event or raises `WebhookError`.

Envelope fields:

- `tenant`: tenant id
- `event_id`: unique id from the webhook sender
- `timestamp`: integer Unix timestamp
- `body`: raw request body text
- `signature`: header text like `t=1700000000,v1=<hex>`

The `keys` mapping stores one active signing key per tenant, or
a list of active keys during rotation. The HMAC message is the
exact raw body text prefixed by the timestamp and a dot:

```text
<timestamp>.<raw body text>
```

Requirements:

- use HMAC-SHA256 and constant-time comparison
- reject timestamps outside `REPLAY_WINDOW_SECONDS`
- accept rotated keys
- reject replayed `(tenant, event_id)` pairs
- allow different tenants to reuse the same event id
- prune expired seen ids from the mutable `store`
- do not mutate `envelope` or `keys`
