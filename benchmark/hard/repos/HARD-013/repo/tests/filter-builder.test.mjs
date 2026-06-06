import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildFilter } from '../src/filterBuilder.mjs';

test('builds and/or groups while preserving leaf filters', () => {
  assert.equal(
    buildFilter({
      op: 'and',
      filters: [
        { op: 'eq', field: 'status', value: 'open' },
        { op: 'or', filters: [
          { op: 'range', field: 'age', min: 18, max: 30 },
          { op: 'contains', field: 'name', value: "O'Neil" },
        ] },
      ],
    }),
    "(status = 'open' AND (age BETWEEN 18 AND 30 OR name CONTAINS 'O''Neil'))"
  );
});
