import assert from 'node:assert/strict';
import { test } from 'node:test';
import { parseTable } from '../src/markdownTable.mjs';

test('ignores alignment row', () => {
  assert.deepEqual(parseTable('| A | B |\n|---|---|\n| 1 | 2 |'), [['A', 'B'], ['1', '2']]);
});
