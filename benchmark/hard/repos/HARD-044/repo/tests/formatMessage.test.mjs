import assert from 'node:assert/strict';
import test from 'node:test';
import { FormatError, formatMessage } from '../src/formatMessage.mjs';

test('interpolates named values', () => {
  assert.equal(
    formatMessage('Hello {name}, status {status}.', { name: 'Ada', status: 'ready' }),
    'Hello Ada, status ready.',
  );
});

test('throws FormatError for missing values', () => {
  assert.throws(
    () => formatMessage('Hello {name}.', {}),
    FormatError,
  );
});
