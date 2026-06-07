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
const { RangeSet, RangeSetError } = await loadModule('src/range-set.mjs');

const base = new RangeSet([[1, 3]]);
const expanded = base.add(4, 6);
assert.deepEqual(base.toArray(), [[1, 3]]);
assert.deepEqual(expanded.toArray(), [[1, 6]]);
assert.equal(expanded.contains(5), true);
assert.equal(expanded.contains(7), false);

const split = expanded.remove(3, 4);
assert.deepEqual(expanded.toArray(), [[1, 6]]);
assert.deepEqual(split.toArray(), [[1, 2], [5, 6]]);

const negative = new RangeSet([[-5, -3], [0, 0]]).add(-2, -1);
assert.deepEqual(negative.toArray(), [[-5, -1], [0, 0]]);

const left = new RangeSet([[10, 12]]);
const right = new RangeSet([[1, 2], [3, 5]]);
const combined = left.union(right);
assert.deepEqual(left.toArray(), [[10, 12]]);
assert.deepEqual(right.toArray(), [[1, 5]]);
assert.deepEqual(combined.toArray(), [[1, 5], [10, 12]]);

assert.throws(() => new RangeSet([[3, 1]]), RangeSetError);
assert.throws(() => new RangeSet().add(1.5, 2), RangeSetError);
assert.throws(() => new RangeSet().remove(5, 4), RangeSetError);
