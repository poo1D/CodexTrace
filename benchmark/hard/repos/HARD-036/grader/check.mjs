import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const root = process.cwd();

function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, encoding: 'utf8' });
  if (result.status !== 0) {
    process.stdout.write(result.stdout || '');
    process.stdout.write(result.stderr || '');
    process.exit(result.status || 1);
  }
}

async function loadModule(relPath) {
  return import(pathToFileURL(path.join(root, relPath)).href + `?v=${Date.now()}`);
}


run('npm', ['test']);
const { summarizeWindow } = await loadModule('src/metricsWindow.mjs');

const now = 10_000;
const windowMs = 1_000;
const events = [
  { timestamp: 9_500, latencyMs: 18, ok: true },
  { timestamp: 9_000, latencyMs: 12, ok: false },
  { timestamp: 9_100, latencyMs: 1, ok: true },
  { timestamp: 9_200, latencyMs: 2, ok: true },
  { timestamp: 9_300, latencyMs: 3, ok: true },
  { timestamp: 9_400, latencyMs: 4, ok: true },
  { timestamp: 9_600, latencyMs: 5, ok: true },
  { timestamp: 9_700, latencyMs: 6, ok: false },
  { timestamp: 9_800, latencyMs: 7, ok: true },
  { timestamp: 9_900, latencyMs: 8, ok: true },
  { timestamp: 10_000, latencyMs: 9, ok: true },
  { timestamp: 9_050, latencyMs: 10, ok: true },
  { timestamp: 9_150, latencyMs: 11, ok: true },
  { timestamp: 9_250, latencyMs: 13, ok: true },
  { timestamp: 9_350, latencyMs: 14, ok: true },
  { timestamp: 9_450, latencyMs: 15, ok: true },
  { timestamp: 9_550, latencyMs: 16, ok: true },
  { timestamp: 9_650, latencyMs: 17, ok: false },
  { timestamp: 9_750, latencyMs: 19, ok: true },
  { timestamp: 9_850, latencyMs: 20, ok: true },
  { timestamp: 10_001, latencyMs: 5_000, ok: false },
  { timestamp: 8_999, latencyMs: 7_000, ok: false },
];
const before = JSON.stringify(events);
const result = summarizeWindow(events, now, windowMs);
assert.equal(JSON.stringify(events), before);
assert.deepEqual(result, {
  count: 20,
  averageLatency: 10.5,
  p95Latency: 19,
  errorRate: 3 / 20,
});

assert.deepEqual(summarizeWindow(events, 20_000, 10), {
  count: 0,
  averageLatency: 0,
  p95Latency: 0,
  errorRate: 0,
});

assert.deepEqual(
  summarizeWindow([{ timestamp: 100, latencyMs: 33, ok: false }], 100, 0),
  {
    count: 1,
    averageLatency: 33,
    p95Latency: 33,
    errorRate: 1,
  },
);
