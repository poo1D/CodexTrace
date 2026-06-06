import assert from 'node:assert/strict';
import { test } from 'node:test';
import { reducer } from '../src/todoStore.mjs';

test('toggle preserves metadata', () => {
  const state = { todos: [{ id: 'a', title: 'Ship', completed: false, priority: 'high' }] };
  const next = reducer(state, { type: 'toggle', id: 'a' });
  assert.equal(next.todos[0].priority, 'high');
  assert.equal(next.todos[0].completed, true);
});
