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

const { UndoableQueue } = await loadModule('src/index.mjs');

function snapshot(queue) {
  return queue.toArray();
}

const itemA = {
  id: 'a',
  priority: 2,
  source: 'api',
  audit: { createdBy: 'Ada', tags: ['hot'] },
};
const itemB = {
  id: 'b',
  priority: 1,
  source: 'worker',
  audit: { createdBy: 'Grace', tags: ['cold'] },
};

const queue = new UndoableQueue([itemA, itemB]);
const removed = queue.dequeue();
removed.priority = 99;
removed.audit.tags.push('mutated');
assert.equal(queue.undo(), true);
assert.deepEqual(snapshot(queue), [
  {
    id: 'a',
    priority: 2,
    source: 'api',
    audit: { createdBy: 'Ada', tags: ['hot'] },
  },
  {
    id: 'b',
    priority: 1,
    source: 'worker',
    audit: { createdBy: 'Grace', tags: ['cold'] },
  },
]);

const peeked = queue.peek();
peeked.audit.createdBy = 'mutated';
const listed = queue.toArray();
listed[1].audit.tags.push('leaked');
assert.deepEqual(snapshot(queue), [
  {
    id: 'a',
    priority: 2,
    source: 'api',
    audit: { createdBy: 'Ada', tags: ['hot'] },
  },
  {
    id: 'b',
    priority: 1,
    source: 'worker',
    audit: { createdBy: 'Grace', tags: ['cold'] },
  },
]);

queue.clear();
assert.equal(queue.size, 0);
assert.equal(queue.undo(), true);
assert.deepEqual(snapshot(queue).map(item => item.id), ['a', 'b']);
assert.equal(queue.redo(), true);
assert.equal(queue.size, 0);

const ordered = new UndoableQueue();
ordered.enqueue({ id: 'first', meta: { n: 1 } });
ordered.enqueue({ id: 'second', meta: { n: 2 } });
ordered.enqueue({ id: 'third', meta: { n: 3 } });
assert.equal(ordered.dequeue().id, 'first');
ordered.undo();
ordered.redo();
assert.deepEqual(ordered.toArray().map(item => item.id), ['second', 'third']);
