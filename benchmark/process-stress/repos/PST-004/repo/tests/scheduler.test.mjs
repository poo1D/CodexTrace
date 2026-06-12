import assert from 'node:assert/strict';
import { test } from 'node:test';
import { runSequential } from '../src/scheduler.mjs';

test('runs tasks sequentially', async () => {
  const events = [];
  const result = await runSequential([
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 5));
      events.push('a');
      return 1;
    },
    async () => {
      events.push('b');
      return 2;
    },
  ]);
  assert.deepEqual(events, ['a', 'b']);
  assert.deepEqual(result, [1, 2]);
});
