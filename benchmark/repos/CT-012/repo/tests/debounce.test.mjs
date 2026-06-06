import assert from 'node:assert/strict';
import { test } from 'node:test';
import { debounce } from '../src/debounce.mjs';

test('debounced function waits before trailing call', async () => {
  let count = 0;
  const fn = debounce(() => { count += 1; }, 5);
  fn();
  assert.equal(count, 0);
  await new Promise((resolve) => setTimeout(resolve, 10));
  assert.equal(count, 1);
});
