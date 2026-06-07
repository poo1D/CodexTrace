import assert from 'node:assert/strict';
import { test } from 'node:test';
import { transition } from '../src/stateMachine.mjs';

test('submits and records history', () => {
  const state = { status: 'draft', history: [] };
  assert.deepEqual(transition(state, 'submit', { by: 'Ada' }), {
    status: 'submitted',
    history: [{ from: 'draft', to: 'submitted', event: 'submit', by: 'Ada' }],
  });
});

test('approves submitted orders', () => {
  const state = { status: 'submitted', history: [] };
  assert.equal(transition(state, 'approve').status, 'approved');
});

test('cancels submitted orders with a reason', () => {
  const state = { status: 'submitted', history: [] };
  assert.deepEqual(transition(state, 'cancel', { by: 'Grace', reason: 'duplicate' }), {
    status: 'canceled',
    history: [{ from: 'submitted', to: 'canceled', event: 'cancel', by: 'Grace', reason: 'duplicate' }],
  });
});

test('invalid transitions preserve values', () => {
  const state = { status: 'draft', history: [] };
  assert.deepEqual(transition(state, 'ship'), state);
});
