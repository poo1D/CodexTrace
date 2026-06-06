import assert from 'node:assert/strict';
import { test } from 'node:test';
import { parseQuery } from '../src/urlParser.mjs';

test('preserves repeated keys', () => {
  assert.deepEqual(parseQuery('?tag=a&tag=b'), { tag: ['a', 'b'] });
});
