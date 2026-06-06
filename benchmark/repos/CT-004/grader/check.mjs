import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

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
const { reducer } = await loadModule('src/todoStore.mjs');
const state = { todos: [{ id: 'x', title: 'One', completed: true, tags: ['work'], due: 'today' }] };
const next = reducer(state, { type: 'toggle', id: 'x' });
assert.deepEqual(next.todos[0].tags, ['work']);
assert.equal(next.todos[0].due, 'today');
assert.equal(next.todos[0].completed, false);
