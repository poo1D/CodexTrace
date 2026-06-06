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
const { retry } = await loadModule('src/retry.mjs');
const slept = [];
const attempts = [];
const value = await retry(async (attempt) => {
  attempts.push(attempt);
  if (attempt < 3) throw Object.assign(new Error('retryable'), { code: 'E_TEMP' });
  return 'done';
}, {
  maxAttempts: 4,
  shouldRetry: (error) => error.code === 'E_TEMP',
  sleep: async (delayMs) => slept.push(delayMs),
  delays: [5, 10, 20],
});
assert.equal(value, 'done');
assert.deepEqual(attempts, [1, 2, 3]);
assert.deepEqual(slept, [5, 10]);
await assert.rejects(
  retry(async () => { throw Object.assign(new Error('no'), { code: 'E_NO' }); }, {
    maxAttempts: 3,
    shouldRetry: (error) => error.code === 'E_TEMP',
    sleep: async () => {},
  }),
  /no/
);
