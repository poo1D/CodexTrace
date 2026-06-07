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

const { validateRegistration } = await loadModule('src/validationPipeline.mjs');

const invalidAll = validateRegistration({
  email: 'ada.example.com',
  password: 'short',
  roles: [],
});
assert.equal(invalidAll.valid, false);
assert.equal(invalidAll.value, null);
assert.deepEqual(
  invalidAll.errors.map(error => [error.field, error.code]),
  [
    ['email', 'invalid_email'],
    ['password', 'weak_password'],
    ['roles', 'missing_roles'],
  ],
  'validation should accumulate every error in stable field order'
);

const missingAll = validateRegistration({});
assert.deepEqual(
  missingAll.errors.map(error => error.field),
  ['email', 'password', 'roles']
);

const source = Object.freeze({
  email: '  GRACE@EXAMPLE.COM  ',
  password: 'long-enough',
  roles: Object.freeze(['editor']),
});
const valid = validateRegistration(source);
assert.equal(valid.valid, true);
assert.deepEqual(valid.value, {
  email: 'grace@example.com',
  password: 'long-enough',
  roles: ['editor'],
});
assert.notStrictEqual(valid.value.roles, source.roles, 'roles should be copied');
assert.deepEqual(source, {
  email: '  GRACE@EXAMPLE.COM  ',
  password: 'long-enough',
  roles: ['editor'],
});

const mixed = validateRegistration({
  email: 'linus@example.com',
  password: 'tiny',
  roles: [],
});
assert.deepEqual(
  mixed.errors.map(error => error.field),
  ['password', 'roles'],
  'later validators should still run when an earlier one passes'
);
