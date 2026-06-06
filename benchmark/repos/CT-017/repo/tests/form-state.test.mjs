import assert from 'node:assert/strict';
import { test } from 'node:test';
import { validateForm } from '../src/formState.mjs';

test('keeps validation messages', () => {
  assert.deepEqual(validateForm({ name: '', email: 'bad' }), {
    name: 'Name is required',
    email: 'Email is invalid',
  });
});
