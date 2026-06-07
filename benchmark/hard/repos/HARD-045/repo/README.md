# stream-window-join

`WindowJoiner(tolerance_ms)` joins left and right events when
their timestamps are within the tolerance.

Event shape:

```python
{"id": "left-1", "time": 1000, "value": "L"}
```

Public API:

- `add_left(event)` returns newly emitted join pairs.
- `add_right(event)` returns newly emitted join pairs.
- `advance_watermark(time_ms)` evicts safely expired buffered events.
- `snapshot()` returns buffered state and counters.

Duplicate event ids are ignored. Events older than the current
watermark are late: count them, but do not emit joins.
