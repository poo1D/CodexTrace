import assert from 'node:assert/strict';
import { test } from 'node:test';
import { validateRegistration } from '../src/validationPipeline.mjs';

test('normalizes valid registrations', () => {
  const result = validateRegistration({
    email: '  ADA@EXAMPLE.COM  ',
    password: 'correct horse',
    roles: ['admin'],
  });

  assert.equal(result.valid, true);
  assert.deepEqual(result.errors, []);
  assert.deepEqual(result.value, {
    email: 'ada@example.com',
    password: 'correct horse',
    roles: ['admin'],
  });
});

test('reports an invalid email', () => {
  const result = validateRegistration({
    email: 'ada.example.com',
    password: 'correct horse',
    roles: ['admin'],
  });

  assert.equal(result.valid, false);
  assert.equal(result.errors[0].field, 'email');
  assert.equal(result.errors[0].code, 'invalid_email');
  assert.equal(result.value, null);
});

test('reports a weak password', () => {
  const result = validateRegistration({
    email: 'ada@example.com',
    password: 'short',
    roles: ['admin'],
  });

  assert.equal(result.valid, false);
  assert.equal(result.errors[0].field, 'password');
  assert.equal(result.errors[0].code, 'weak_password');
});
