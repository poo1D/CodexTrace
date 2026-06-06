import assert from 'node:assert/strict';
import { test } from 'node:test';
import { errorForStatus } from '../src/apiClient.mjs';

test('maps not found separately', () => {
  assert.equal(errorForStatus(404), 'not_found');
});
