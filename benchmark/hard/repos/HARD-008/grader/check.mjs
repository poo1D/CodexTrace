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
const { reducer } = await loadModule('src/editorReducer.mjs');
const start = { text: 'a', past: [], future: [] };
const b = reducer(start, { type: 'edit', text: 'b' });
const c = reducer(b, { type: 'edit', text: 'c' });
const back = reducer(c, { type: 'undo' });
assert.deepEqual(back, { text: 'b', past: ['a'], future: ['c'] });
assert.deepEqual(reducer(back, { type: 'redo' }), { text: 'c', past: ['a', 'b'], future: [] });
assert.deepEqual(c, { text: 'c', past: ['a', 'b'], future: [] }, 'state must not be mutated');
assert.strictEqual(reducer(start, { type: 'unknown' }), start);
