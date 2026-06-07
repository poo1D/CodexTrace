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

const { transition } = await loadModule('src/stateMachine.mjs');

const draft = Object.freeze({ status: 'draft', history: Object.freeze([]) });
const submitted = transition(draft, 'submit', { by: 'Ada' });
assert.notStrictEqual(submitted, draft, 'valid transitions must create a new state');
assert.equal(submitted.status, 'submitted');
assert.deepEqual(draft, { status: 'draft', history: [] }, 'input state must not be mutated');

const approved = transition(submitted, 'approve', { by: 'Linus' });
const shipped = transition(approved, 'ship', { by: 'Grace' });
const delivered = transition(shipped, 'deliver', { by: 'Margaret' });
assert.equal(delivered.status, 'delivered');
assert.deepEqual(
  delivered.history.map(entry => [entry.from, entry.to, entry.event]),
  [
    ['draft', 'submitted', 'submit'],
    ['submitted', 'approved', 'approve'],
    ['approved', 'shipped', 'ship'],
    ['shipped', 'delivered', 'deliver'],
  ]
);

const submittedForCancel = { status: 'submitted', history: [] };
const canceled = transition(submittedForCancel, 'cancel', { by: 'Ada', reason: 'duplicate' });
assert.equal(canceled.status, 'canceled');
assert.deepEqual(canceled.history[0], {
  from: 'submitted',
  to: 'canceled',
  event: 'cancel',
  by: 'Ada',
  reason: 'duplicate',
});

const invalidDraft = { status: 'draft', history: [] };
assert.strictEqual(transition(invalidDraft, 'ship'), invalidDraft);
assert.strictEqual(transition(invalidDraft, 'unknown-event'), invalidDraft);

const deliveredState = { status: 'delivered', history: [] };
assert.strictEqual(transition(deliveredState, 'cancel'), deliveredState);

const source = await (await import('node:fs/promises')).readFile('src/stateMachine.mjs', 'utf8');
assert.match(
  source,
  /TRANSITIONS|transitionMap|allowedTransitions|createTransition|canTransition/,
  'refactor should introduce a reusable transition table or helper'
);
