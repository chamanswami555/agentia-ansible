#!/usr/bin/env node
// Manual live check: drive the MCP server over stdio against a real Copado org in Ansible check
// mode (nothing is submitted or deployed), then read the evidence summary.
// Usage: node mcp/live-check.mjs <story id> <git clone of the Salesforce project>
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const [story, repoDir] = process.argv.slice(2);
if (!story || !repoDir) { console.error('usage: node mcp/live-check.mjs <story id> <repo dir>'); process.exit(2); }
const SERVER = path.join(path.dirname(fileURLToPath(import.meta.url)), 'server.mjs');
const evidenceRoot = path.join(repoDir, 'evidence');
const child = spawn(process.execPath, [SERVER], { stdio: ['pipe', 'pipe', 'inherit'], env: { ...process.env, AGENTIA_EVIDENCE_ROOT: evidenceRoot } });
const answers = new Map();
let buffer = '';
child.stdout.on('data', (d) => {
  buffer += d;
  let idx;
  while ((idx = buffer.indexOf('\n')) >= 0) {
    const line = buffer.slice(0, idx).trim();
    buffer = buffer.slice(idx + 1);
    if (line) { const msg = JSON.parse(line); if (msg.id !== undefined) answers.set(msg.id, msg); }
  }
});
const send = (msg) => child.stdin.write(`${JSON.stringify(msg)}\n`);
const call = async (id, method, params, timeoutMs) => {
  send({ jsonrpc: '2.0', id, method, params });
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline && !answers.has(id)) await new Promise((r) => setTimeout(r, 200));
  if (!answers.has(id)) throw new Error(`no answer for ${method} within ${timeoutMs} ms`);
  return answers.get(id);
};
const text = (msg) => JSON.parse(msg.result.content[0].text);

await call(1, 'initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'live-check', version: '0' } }, 10000);
send({ jsonrpc: '2.0', method: 'notifications/initialized' });
const run = text(await call(2, 'tools/call', { name: 'run_release_playbook', arguments: { story_ids: [story], repo_dir: repoDir, check: true } }, 600000));
console.log('run:', { ok: run.ok, exitCode: run.exitCode, recap: run.recap, evidence_dir: run.evidence_dir });
if (!run.ok) console.log(run.output.slice(-3000));
const status = text(await call(3, 'tools/call', { name: 'release_status', arguments: {} }, 10000));
console.log('status:', { found: status.found, folder: status.folder, files: Object.keys(status.files || {}), deployment_status: status.deployment_status });
child.kill();
process.exit(run.ok ? 0 : 1);
