import assert from 'node:assert/strict';
import { test } from 'node:test';
import { reducer } from '../src/editorReducer.mjs';

test('new edit clears redo', () => {
  const state = { text: 'b', past: ['a'], future: ['c'] };
  assert.deepEqual(reducer(state, { type: 'edit', text: 'x' }).future, []);
});
