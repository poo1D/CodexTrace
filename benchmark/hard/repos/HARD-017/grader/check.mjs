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
const { BatchQueue } = await loadModule('src/batchQueue.mjs');

const events = [];
const queue = new BatchQueue(async item => {
  events.push(`start:${item.id}`);
  if (item.fail) {
    throw new Error(`bad:${item.id}`);
  }
  await Promise.resolve();
  events.push(`done:${item.id}`);
  return item.id.toUpperCase();
});

queue.push({ id: 'a' });
queue.push({ id: 'b', fail: true });
queue.push({ id: 'c' });
assert.equal(queue.cancel(item => item.id === 'c'), 1);
assert.equal(queue.size(), 2);

const first = await queue.flush();
assert.deepEqual(first.map(result => result.status), ['fulfilled', 'rejected']);
assert.equal(first[0].value, 'A');
assert.match(first[1].reason.message, /bad:b/);
assert.deepEqual(events, ['start:a', 'done:a', 'start:b']);
assert.equal(queue.size(), 0);

queue.push({ id: 'd' });
queue.push({ id: 'e' });
assert.equal(queue.cancel(item => item.id === 'missing'), 0);
assert.deepEqual(await queue.flush(), [
  { status: 'fulfilled', value: 'D' },
  { status: 'fulfilled', value: 'E' },
]);
assert.deepEqual(await queue.flush(), []);
