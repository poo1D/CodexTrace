import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const root = process.cwd();

function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, encoding: 'utf8' });
  if (result.status !== 0) {
    process.stdout.write(result.stdout || '');
    process.stdout.write(result.stderr || '');
    process.exit(result.status || 1);
  }
}

async function loadModule(relPath) {
  return import(pathToFileURL(path.join(root, relPath)).href + `?v=${Date.now()}`);
}


run('npm', ['test']);

const { CsvParseError, CsvStreamParser, parseCsvStream } = await loadModule('src/csvStream.mjs');

const parser = new CsvStreamParser();
assert.deepEqual(parser.write('name,note\nAda,"hello'), [['name', 'note']]);
assert.deepEqual(parser.write(', wor'), []);
assert.deepEqual(parser.write('ld"\n'), [['Ada', 'hello, world']]);
assert.deepEqual(parser.end(), []);

assert.deepEqual(
  await parseCsvStream(['id,note\n1,"a ""quo', 'te"" here"\n']),
  [
    ['id', 'note'],
    ['1', 'a "quote" here'],
  ]
);

assert.deepEqual(
  await parseCsvStream(['id,body\n1,"line one', '\nline two"\n2,done\n']),
  [
    ['id', 'body'],
    ['1', 'line one\nline two'],
    ['2', 'done'],
  ]
);

assert.deepEqual(
  await parseCsvStream(['a,b\r', '\n"x\r\ny",z']),
  [
    ['a', 'b'],
    ['x\r\ny', 'z'],
  ]
);

await assert.rejects(
  parseCsvStream(['a,b\n1,"unterminated']),
  error => error instanceof CsvParseError && /quote|unterminated/i.test(error.message)
);

await assert.rejects(
  parseCsvStream(['a,b\n1,"ok" trailing\n']),
  error => error instanceof CsvParseError && /quote|trailing|invalid/i.test(error.message)
);

const incremental = new CsvStreamParser();
assert.deepEqual(incremental.write('a,b\n1,"still'), [['a', 'b']]);
assert.deepEqual(incremental.write(' open'), []);
assert.deepEqual(incremental.write('"\n2,done\n'), [['1', 'still open'], ['2', 'done']]);
assert.deepEqual(incremental.end(), []);
