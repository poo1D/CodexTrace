import assert from 'node:assert/strict';
import { test } from 'node:test';
import { isEnabled } from '../src/flags.mjs';

test('deny list disables enabled flag', () => {
  assert.equal(isEnabled({ beta: { enabled: true, deny: ['u1'] } }, 'beta', { id: 'u1' }), false);
});
