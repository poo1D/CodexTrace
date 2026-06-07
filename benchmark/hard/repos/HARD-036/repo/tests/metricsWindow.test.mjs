import assert from 'node:assert/strict';
import test from 'node:test';
import { summarizeWindow } from '../src/metricsWindow.mjs';

test('returns zeroes for an empty window', () => {
  assert.deepEqual(summarizeWindow([], 1_000, 100), {
    count: 0,
    averageLatency: 0,
    p95Latency: 0,
    errorRate: 0,
  });
});

test('summarizes recent events', () => {
  const events = [
    { timestamp: 920, latencyMs: 100, ok: true },
    { timestamp: 950, latencyMs: 200, ok: false },
    { timestamp: 990, latencyMs: 300, ok: true },
    { timestamp: 1_100, latencyMs: 900, ok: false },
    { timestamp: 500, latencyMs: 50, ok: true },
  ];

  assert.deepEqual(summarizeWindow(events, 1_000, 100), {
    count: 3,
    averageLatency: 200,
    p95Latency: 300,
    errorRate: 1 / 3,
  });
});

test('ignores future events', () => {
  const events = [
    { timestamp: 1_000, latencyMs: 125, ok: true },
    { timestamp: 1_001, latencyMs: 999, ok: false },
  ];

  assert.deepEqual(summarizeWindow(events, 1_000, 10), {
    count: 1,
    averageLatency: 125,
    p95Latency: 125,
    errorRate: 0,
  });
});
