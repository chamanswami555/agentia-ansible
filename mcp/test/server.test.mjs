// MIT License. See LICENSE in the repository root.
// Smoke tests: the server lists its tools over stdio and summarizes evidence folders.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { promises as fs } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { listEvidence, releaseStatus, playbookPath, runPlaybook, deploymentStatus } from '../server.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SERVER = path.join(HERE, '..', 'server.mjs');

async function tempEvidence() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'agentia-evidence-'));
  const folder = path.join(root, '2026-10-12T10-00-00');
  await fs.mkdir(folder);
  await fs.writeFile(path.join(folder, 'deployment.json'), JSON.stringify({ deploy_mode: 'story', deploy_jobs: [{ name: 'JE-018', status: 'Successful' }], promotions: [{ status: 'In Progress' }] }));
  await fs.writeFile(path.join(folder, 'smoke-tests.json'), JSON.stringify({ tests: { total: 12, passed: 12, failed: 0 } }));
  return root;
}

test('playbookPath rejects unknown names', () => {
  assert.throws(() => playbookPath('rm_rf'), /unknown playbook/);
  assert.match(playbookPath('release_window'), /release_window\.yml$/);
});

test('listEvidence and releaseStatus read evidence folders', async () => {
  const root = await tempEvidence();
  const folders = await listEvidence(root);
  assert.equal(folders.length, 1);
  assert.deepEqual(folders[0].files, ['deployment.json', 'smoke-tests.json']);
  const status = await releaseStatus(root);
  assert.equal(status.found, true);
  assert.equal(status.deployment_status, 'Successful');
  assert.equal(status.smoke_tests.failed, 0);
  const missing = await releaseStatus(path.join(root, 'nothing-here'));
  assert.equal(missing.found, false);
});

test('server answers initialize and tools/list over stdio', async () => {
  const child = spawn(process.execPath, [SERVER], { stdio: ['pipe', 'pipe', 'pipe'] });
  const lines = [];
  let buffer = '';
  child.stdout.on('data', (d) => {
    buffer += d;
    let idx;
    while ((idx = buffer.indexOf('\n')) >= 0) {
      const line = buffer.slice(0, idx).trim();
      buffer = buffer.slice(idx + 1);
      if (line) lines.push(JSON.parse(line));
    }
  });
  const send = (msg) => child.stdin.write(`${JSON.stringify(msg)}\n`);
  send({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'test', version: '0' } } });
  send({ jsonrpc: '2.0', method: 'notifications/initialized' });
  send({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline && !lines.some((m) => m.id === 2)) await new Promise((r) => setTimeout(r, 100));
  child.kill();
  const init = lines.find((m) => m.id === 1);
  assert.equal(init.result.serverInfo.name, 'agentia-ansible');
  const tools = lines.find((m) => m.id === 2).result.tools.map((t) => t.name).sort();
  assert.deepEqual(tools, ['list_evidence', 'list_playbooks', 'release_status', 'run_playbook', 'run_release_playbook']);
});

test('deploymentStatus reads story-mode and promotion-mode evidence', () => {
  assert.equal(deploymentStatus({ deploy_jobs: [{ status: 'Successful' }, { status: 'Successful' }] }), 'Successful');
  assert.equal(deploymentStatus({ deploy_jobs: [{ status: 'Successful' }, { status: 'Error' }] }), 'Error');
  assert.equal(deploymentStatus({ promotion_after: { status: 'Completed' } }), 'Completed');
  assert.equal(deploymentStatus({}), 'unknown');
});

// The whole release window against the fake CLI: proves the demo path reaches a deployment job
// (a fake that answers "In Progress" for ever, or a skipped stage, would fail this).
test('release window runs end to end in demo mode and reports a successful deployment', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'agentia-mcp-demo-'));
  const evidenceDir = path.join(root, 'run');
  const result = await runPlaybook('release_window',
    { story_ids: ['US-0042'], deploy_mode: 'story', approve: true, poll_interval: 1, wait_timeout: 60, repo_dir: root, evidence_dir: evidenceDir },
    { demo: true });
  assert.equal(result.ok, true, result.output);
  assert.match(result.recap, /failed=0/);
  const status = await releaseStatus(root, 'run');
  assert.equal(status.deployment_status, 'Successful');
  assert.ok(status.files['validations.json'].deploy_jobs.length === 1, 'validation deployment job recorded');
});

test('release window without approve stops at the gate and deploys nothing', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'agentia-mcp-gate-'));
  const result = await runPlaybook('release_window',
    { story_ids: ['US-0042'], poll_interval: 1, wait_timeout: 60, repo_dir: root, evidence_dir: path.join(root, 'run') },
    { demo: true });
  assert.equal(result.ok, false);
  assert.match(result.output, /Deployment not approved/);
  assert.doesNotMatch(result.output, /Promote and deploy each story.*\n.*changed/);
  const files = await fs.readdir(path.join(root, 'run'));
  assert.ok(!files.includes('deployment.json'), 'no deployment evidence without approval');
});
