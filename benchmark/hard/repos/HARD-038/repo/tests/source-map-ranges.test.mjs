import assert from 'node:assert/strict';
import test from 'node:test';
import { mapRange } from '../src/sourceMapRanges.mjs';

test('maps exact generated range endpoints', () => {
  const map = {
    mappings: [
      {
        generated: { line: 1, column: 0 },
        original: { source: 'src/app.ts', line: 10, column: 4 },
      },
      {
        generated: { line: 1, column: 12 },
        original: { source: 'src/app.ts', line: 10, column: 16 },
      },
    ],
  };

  assert.deepEqual(
    mapRange(map, { line: 1, column: 0 }, { line: 1, column: 12 }),
    {
      source: 'src/app.ts',
      start: { line: 10, column: 5 },
      end: { line: 10, column: 17 },
    },
  );
});

test('returns null when exact mapping is missing', () => {
  const map = {
    mappings: [
      {
        generated: { line: 1, column: 0 },
        original: { source: 'src/app.ts', line: 1, column: 0 },
      },
    ],
  };

  assert.equal(mapRange(map, { line: 1, column: 1 }, { line: 1, column: 2 }), null);
});
