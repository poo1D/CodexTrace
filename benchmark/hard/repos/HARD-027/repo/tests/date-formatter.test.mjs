import assert from 'node:assert/strict';
import { test } from 'node:test';
import { DateFormatError, formatDate } from '../src/dateFormatter.mjs';

test('formats a UTC ISO timestamp with numeric tokens', () => {
  assert.equal(
    formatDate('2026-02-03T04:05:06Z', 'YYYY-MM-DD HH:mm:ss'),
    '2026-02-03 04:05:06'
  );
});

test('zero-pads single-digit fields', () => {
  assert.equal(
    formatDate(new Date(Date.UTC(2026, 0, 2, 3, 4, 5)), 'YYYY/MM/DD HH:mm:ss'),
    '2026/01/02 03:04:05'
  );
});

test('applies a fixed timezone offset and prints Z', () => {
  assert.equal(
    formatDate('2026-01-01T23:30:00Z', 'YYYY-MM-DD HH:mm Z', {
      timeZoneOffsetMinutes: 330,
    }),
    '2026-01-02 05:00 +05:30'
  );
});

test('rejects invalid dates with DateFormatError', () => {
  assert.throws(
    () => formatDate('not-a-date', 'YYYY-MM-DD'),
    error => error instanceof DateFormatError && /invalid/i.test(error.message)
  );
});
