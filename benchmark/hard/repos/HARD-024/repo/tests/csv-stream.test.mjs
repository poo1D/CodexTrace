import assert from 'node:assert/strict';
import { test } from 'node:test';
import { CsvParseError, CsvStreamParser, parseCsvStream } from '../src/csvStream.mjs';

test('emits complete unquoted rows incrementally', () => {
  const parser = new CsvStreamParser();
  assert.deepEqual(parser.write('name,age\nAda,'), [['name', 'age']]);
  assert.deepEqual(parser.write('37\nGrace,44'), [['Ada', '37']]);
  assert.deepEqual(parser.end(), [['Grace', '44']]);
});

test('parses quoted comma and escaped quote', async () => {
  assert.deepEqual(
    await parseCsvStream(['name,note\nAda,"ships, fast"\nGrace,"said ""hi"""\n']),
    [
      ['name', 'note'],
      ['Ada', 'ships, fast'],
      ['Grace', 'said "hi"'],
    ]
  );
});

test('rejects ragged rows with CsvParseError', async () => {
  await assert.rejects(
    parseCsvStream(['a,b\n1,2,3\n']),
    error => error instanceof CsvParseError && /ragged|column/i.test(error.message)
  );
});
