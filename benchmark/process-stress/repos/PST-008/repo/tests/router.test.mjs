import assert from 'node:assert/strict';
import { test } from 'node:test';
import { matchRoute } from '../src/router.mjs';

test('normalizes one trailing slash', () => {
  assert.deepEqual(matchRoute([{ path: '/users' }], '/users/'), { path: '/users' });
});
