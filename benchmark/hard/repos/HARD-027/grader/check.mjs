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

const fs = await import('node:fs/promises');
const { DateFormatError, formatDate } = await loadModule('src/dateFormatter.mjs');

assert.equal(
  formatDate('2026-06-07T16:08:09Z', 'ddd, MMM DD, YYYY [at] HH:mm:ss Z'),
  'Sun, Jun 07, 2026 at 16:08:09 +00:00'
);

assert.equal(
  formatDate('2026-03-01T01:15:00Z', 'YYYY-MM-DD HH:mm Z', {
    timeZoneOffsetMinutes: -300,
  }),
  '2026-02-28 20:15 -05:00'
);

assert.equal(
  formatDate(1777777777000, 'YYYY-MM-DD HH:mm:ss'),
  '2026-05-02 22:49:37'
);

const original = new Date(Date.UTC(2026, 11, 31, 23, 59, 58));
assert.equal(formatDate(original, 'YYYY-MM-DD HH:mm:ss'), '2026-12-31 23:59:58');
assert.equal(original.getUTCFullYear(), 2026, 'input Date must not be mutated');

assert.throws(
  () => formatDate(new Date('bad'), 'YYYY-MM-DD'),
  error => error instanceof DateFormatError && /invalid date/i.test(error.message)
);

const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8'));
assert.deepEqual(pkg.dependencies ?? {}, {}, 'fixture solution must not add runtime dependencies');
assert.deepEqual(pkg.devDependencies ?? {}, {}, 'fixture solution must not add dev dependencies');

const source = await fs.readFile(path.join(root, 'src/dateFormatter.mjs'), 'utf8');
assert.ok(
  !/from\s+['"](date-fns|moment|luxon|dayjs)['"]|require\(['"](date-fns|moment|luxon|dayjs)['"]\)/.test(source),
  'solution must not import external date libraries'
);
