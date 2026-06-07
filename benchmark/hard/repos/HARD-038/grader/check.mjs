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
const { SourceMapError, mapRange } = await loadModule('src/sourceMapRanges.mjs');

const map = {
  mappings: [
    {
      generated: { line: 1, column: 0 },
      original: { source: 'src/app.ts', line: 10, column: 4 },
    },
    {
      generated: { line: 1, column: 8 },
      original: { source: 'src/app.ts', line: 10, column: 12 },
    },
    {
      generated: { line: 2, column: 0 },
      original: { source: 'src/app.ts', line: 11, column: 0 },
    },
    {
      generated: { line: 2, column: 5 },
      original: { source: 'src/app.ts', line: 11, column: 5 },
    },
  ],
};

assert.deepEqual(
  mapRange(map, { line: 1, column: 10 }, { line: 2, column: 7 }),
  {
    source: 'src/app.ts',
    start: { line: 10, column: 14 },
    end: { line: 11, column: 7 },
  },
);

assert.deepEqual(
  mapRange(map, { line: 1, column: 0 }, { line: 1, column: 8 }),
  {
    source: 'src/app.ts',
    start: { line: 10, column: 4 },
    end: { line: 10, column: 12 },
  },
);

assert.deepEqual(
  mapRange({ mappings: [...map.mappings].reverse() }, { line: 2, column: 6 }, { line: 2, column: 9 }),
  {
    source: 'src/app.ts',
    start: { line: 11, column: 6 },
    end: { line: 11, column: 9 },
  },
);

assert.throws(
  () => mapRange({ mappings: [{ generated: { line: 1 }, original: { source: 'x', line: 1, column: 0 } }] }, { line: 1, column: 0 }, { line: 1, column: 1 }),
  (error) => error instanceof SourceMapError &&
    error.message.includes('mapping[0]') &&
    error.message.includes('generated.column'),
);
