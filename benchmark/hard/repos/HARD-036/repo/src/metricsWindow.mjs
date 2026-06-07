export function summarizeWindow(events, now, windowMs) {
  const recent = events.filter(
    (event) => event.timestamp > now - windowMs && event.timestamp <= now,
  );
  const count = recent.length;
  if (count === 0) {
    return {
      count: 0,
      averageLatency: 0,
      p95Latency: 0,
      errorRate: 0,
    };
  }

  const totalLatency = recent.reduce((sum, event) => sum + event.latencyMs, 0);
  const failures = recent.filter((event) => event.ok === false).length;

  return {
    count,
    averageLatency: totalLatency / count,
    p95Latency: Math.max(...recent.map((event) => event.latencyMs)),
    errorRate: failures / count,
  };
}
