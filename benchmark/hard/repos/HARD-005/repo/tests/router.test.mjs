import assert from 'node:assert/strict';
import { test } from 'node:test';
import { matchRoute } from '../src/router.mjs';

test('matches named params', () => {
  assert.deepEqual(matchRoute('/users/:id', '/users/42'), { matched: true, params: { id: '42' } });
});
