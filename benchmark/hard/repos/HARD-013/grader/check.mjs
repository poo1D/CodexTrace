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
const { buildFilter } = await loadModule('src/filterBuilder.mjs');
assert.equal(
  buildFilter({ op: 'not', filter: { op: 'eq', field: 'archived', value: true } }),
  "NOT (archived = true)"
);
assert.equal(
  buildFilter({
    op: 'not',
    filter: {
      op: 'or',
      filters: [
        { op: 'eq', field: 'status', value: 'closed' },
        { op: 'contains', field: 'title', value: 'wip' },
      ],
    },
  }),
  "NOT ((status = 'closed' OR title CONTAINS 'wip'))"
);
assert.equal(
  buildFilter({
    op: 'and',
    filters: [
      { op: 'eq', field: 'priority', value: 'high' },
      { op: 'not', filter: { op: 'range', field: 'age', min: 0, max: 7 } },
    ],
  }),
  "(priority = 'high' AND NOT (age BETWEEN 0 AND 7))"
);
assert.equal(buildFilter({ op: 'eq', field: 'active', value: false }), 'active = false');
assert.throws(() => buildFilter({ op: 'and', filters: [] }), /empty|filter/i);
