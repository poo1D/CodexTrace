# metrics-window

`summarizeWindow(events, now, windowMs)` returns rolling
service metrics for events inside a time window.

Each event has:

- `timestamp`: epoch milliseconds
- `latencyMs`: request latency
- `ok`: whether the request succeeded

Required output:

- `count`: number of events in the window
- `averageLatency`: arithmetic mean latency
- `p95Latency`: nearest-rank 95th percentile latency
- `errorRate`: failed events divided by count

The window includes timestamps from `now - windowMs` through
`now`, inclusive. Future events are excluded. Empty windows
return zeroes.
