import assert from 'node:assert/strict'
import {chmodSync, mkdtempSync, readFileSync, writeFileSync} from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import {test} from 'node:test'
import {fileURLToPath} from 'node:url'

import AnsibleRun from '../commands/ansible/run.js'
import AnsibleScaffold from '../commands/ansible/scaffold.js'

// The commands run in-process, with a stand-in for the host the Agentia CLI injects.
const here = path.dirname(fileURLToPath(import.meta.url)) // dist/lib
const pluginRoot = path.resolve(here, '..', '..')
const repoRoot = path.resolve(pluginRoot, '..')
const fakeAgentia = path.join(repoRoot, 'tools', 'fake-agentia', 'agentia')
const hostApi = JSON.parse(readFileSync(path.join(pluginRoot, 'package.json'), 'utf8')).agentia.hostApi as number
;(globalThis as Record<symbol, unknown>)[Symbol.for('copado.agentia.pluginHost')] = {
  apiVersion: hostApi,
  runWithTransaction: async (_options: unknown, action: () => Promise<unknown>) => action(),
  getTransactionId: () => 'test-transaction',
  auth: {status: () => ({cicd: {configured: false}})},
  format: {table: () => ''},
  work: {getWorkItem: async () => ({name: 'US-0042'})},
}
process.env.AGENTIA_FAKE_FIXTURES = path.join(repoRoot, 'collection', 'tests', 'fixtures', 'agentia')

const tmp = () => mkdtempSync(path.join(os.tmpdir(), 'agentia-plugin-'))

const fakePlaybookBin = (dir: string, script: string) => {
  const bin = path.join(dir, 'ansible-playbook')
  writeFileSync(bin, `#!/bin/sh\n${script}\n`)
  chmodSync(bin, 0o755)
  return bin
}

test('scaffold writes a story-mode playbook for the given stories', async () => {
  const dir = tmp()
  const out = path.join(dir, 'release-window.yml')
  await AnsibleScaffold.run(['--stories', 'US-0042,US-0043', '--repo-dir', dir, '--out', out, '--skip-auth-check'], pluginRoot)
  const text = readFileSync(out, 'utf8')
  assert.match(text, /story_ids: \["US-0042", "US-0043"\]/)
  assert.match(text, /deploy_mode: "story"/)
  assert.match(text, /evidence_root:/)
})

test('scaffold takes the active story from the host when no stories are given', async () => {
  const dir = tmp()
  const out = path.join(dir, 'release-window.yml')
  await AnsibleScaffold.run(['--repo-dir', dir, '--out', out, '--skip-auth-check'], pluginRoot)
  assert.match(readFileSync(out, 'utf8'), /story_ids: \["US-0042"\]/)
})

test('scaffold rejects a promotion id that is not 18 characters', async () => {
  const dir = tmp()
  await assert.rejects(
    AnsibleScaffold.run(['--stories', 'US-0042', '--promotion', 'abc', '--repo-dir', dir, '--out', path.join(dir, 'x.yml'), '--skip-auth-check'], pluginRoot),
    /18-character/,
  )
})

test('scaffold in promotion mode reads the promotion through the CLI', async () => {
  const dir = tmp()
  const out = path.join(dir, 'release-window.yml')
  await AnsibleScaffold.run(['--stories', 'US-0042', '--promotion', 'a0B000000000001EAA', '--repo-dir', dir, '--out', out, '--skip-auth-check', '--agentia-bin', fakeAgentia], pluginRoot)
  const text = readFileSync(out, 'utf8')
  assert.match(text, /deploy_mode: "promotion"/)
  assert.match(text, /promotion_id: "a0B000000000001EAA"/)
})

test('run refuses a playbook that does not exist', async () => {
  await assert.rejects(AnsibleRun.run(['--playbook', '/nonexistent/release-window.yml'], pluginRoot), /Playbook not found/)
})

test('run refuses extra variables that are not JSON', async () => {
  const dir = tmp()
  const playbook = path.join(dir, 'release-window.yml')
  writeFileSync(playbook, '---\n- hosts: localhost\n  tasks: []\n')
  await assert.rejects(AnsibleRun.run(['--playbook', playbook, '--extra-vars', 'not json'], pluginRoot), /JSON object/)
})

test('run reports the recap of a successful playbook', async () => {
  const dir = tmp()
  const playbook = path.join(dir, 'release-window.yml')
  writeFileSync(playbook, '---\n- hosts: localhost\n  tasks: []\n')
  const bin = fakePlaybookBin(dir, 'echo "localhost : ok=3 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0"')
  const result = (await AnsibleRun.run(['--playbook', playbook, '--approve', '--ansible-playbook-bin', bin], pluginRoot)) as {ok: boolean; recap: {ok: number; failed: number}; stoppedAtApproval: boolean}
  assert.equal(result.ok, true)
  assert.deepEqual([result.recap.ok, result.recap.failed], [3, 0])
  assert.equal(result.stoppedAtApproval, false)
})

test('run names a stop at the approval gate and a missing collection', async () => {
  const dir = tmp()
  const playbook = path.join(dir, 'release-window.yml')
  writeFileSync(playbook, '---\n- hosts: localhost\n  tasks: []\n')
  const bin = fakePlaybookBin(dir, 'echo "fatal: Deployment not approved. Interactive runs answer yes"; echo "localhost : ok=5 changed=0 unreachable=0 failed=1 skipped=0 rescued=0 ignored=0"; exit 2')
  const result = (await AnsibleRun.run(['--playbook', playbook, '--ansible-playbook-bin', bin], pluginRoot)) as {ok: boolean; stoppedAtApproval: boolean; hint?: string}
  assert.equal(result.ok, false)
  assert.equal(result.stoppedAtApproval, true)
  const bin2 = fakePlaybookBin(dir, 'echo "ERROR! Unable to retrieve file contents"; echo "Could not find or access \'/x/chamanswami555.agentia.release_window\'"; exit 1')
  const missing = (await AnsibleRun.run(['--playbook', playbook, '--ansible-playbook-bin', bin2], pluginRoot)) as {ok: boolean; hint?: string}
  assert.equal(missing.ok, false)
  assert.match(missing.hint ?? '', /collections-path/)
  process.exitCode = 0 // the command sets it for callers; the test runner must not inherit it
})
