import assert from 'node:assert/strict';
import { test } from 'node:test';
import { sortRows } from '../src/tableSort.mjs';

test('sorts rows by key', () => {
  assert.deepEqual(sortRows([{ n: 2 }, { n: 1 }], 'n'), [{ n: 1 }, { n: 2 }]);
});
