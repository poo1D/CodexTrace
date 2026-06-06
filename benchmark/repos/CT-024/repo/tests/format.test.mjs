import assert from 'node:assert/strict';
import { test } from 'node:test';
import { formatUser } from '../src/format.mjs';

test('formats fallback user', () => {
  assert.equal(formatUser({ name: '' }), 'Anonymous');
});
