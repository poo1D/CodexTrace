import assert from 'node:assert/strict';
import { test } from 'node:test';
import { parseDate } from '../src/dateParser.mjs';

test('rejects invalid dates', () => {
  assert.throws(() => parseDate('not-a-date'), /invalid/i);
});
