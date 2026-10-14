#!/usr/bin/env node
// MIT License. See LICENSE in the repository root.
// MCP server: AI agents trigger Copado releases through governed Ansible playbooks instead
// of raw commands. Tools run ansible-playbook on the chamanswami555.agentia collection and
// read the evidence folders the playbooks write.
//
// Environment:
//   AGENTIA_ANSIBLE_ROOT   repository root (default: parent of this file)
//   ANSIBLE_PLAYBOOK_BIN   ansible-playbook executable (default: <root>/.venv/bin/ansible-playbook)
//   AGENTIA_EVIDENCE_ROOT  where evidence folders live (default: <root>/var/evidence)
//   AGENTIA_MCP_DEMO       "1" runs playbooks against the fake Agentia CLI (offline demo)
import { spawn } from 'node:child_process';
import os from 'node:os';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = process.env.AGENTIA_ANSIBLE_ROOT || path.resolve(HERE, '..');
const PLAYBOOK_BIN = process.env.ANSIBLE_PLAYBOOK_BIN || path.join(ROOT, '.venv', 'bin', 'ansible-playbook');
const EVIDENCE_ROOT = process.env.AGENTIA_EVIDENCE_ROOT || path.join(ROOT, 'var', 'evidence');
const PLAYBOOKS = {
  release_window: 'Validate stories, merge, run smoke tests, deploy after approval, write evidence',
  nightly_validate: 'Validate every story in flight and run the smoke suite without deploying',
  remediate_failed_job: 'Read a failed job, ask Copado AI for a diagnosis, write an incident file, optionally resume',
};
const OUTPUT_LIMIT = 12000;

export function playbookPath(name) {
  if (!Object.hasOwn(PLAYBOOKS, name)) throw new Error(`unknown playbook: ${name}`);
  return path.join(ROOT, 'collection', 'playbooks', `${name}.yml`);
}

export function buildEnv(demo) {
  const env = { ...process.env, ANSIBLE_COLLECTIONS_PATH: path.join(ROOT, 'var'), ANSIBLE_LOCALHOST_WARNING: 'false', ANSIBLE_INVENTORY_UNPARSED_WARNING: 'false', ANSIBLE_FORCE_COLOR: 'false' };
  if (demo || process.env.AGENTIA_MCP_DEMO === '1') {
    env.PATH = `${path.join(ROOT, 'tools', 'fake-agentia')}${path.delimiter}${env.PATH || ''}`;
    env.AGENTIA_FAKE_FIXTURES = path.join(ROOT, 'collection', 'tests', 'fixtures', 'agentia');
    // The fake answers job polls in sequence (running, then finished) by counting earlier calls in
    // this log, so every demo run gets a fresh one; without it a job would poll "In Progress" for ever.
    env.AGENTIA_FAKE_LOG = path.join(os.tmpdir(), `agentia-fake-calls-${process.pid}-${Date.now()}.jsonl`);
  }
  return env;
}

export function runPlaybook(name, extraVars, { demo = false, check = false } = {}) {
  const args = [playbookPath(name), '-e', JSON.stringify(extraVars)];
  if (check) args.push('--check');
  return new Promise((resolve) => {
    const child = spawn(PLAYBOOK_BIN, args, { env: buildEnv(demo), cwd: ROOT });
    let out = '';
    child.stdout.on('data', (d) => { out += d; });
    child.stderr.on('data', (d) => { out += d; });
    child.on('error', (err) => resolve({ ok: false, exitCode: -1, output: `cannot start ${PLAYBOOK_BIN}: ${err.message}` }));
    child.on('close', (code) => {
      const recap = out.split('\n').find((line) => line.startsWith('localhost')) || '';
      resolve({ ok: code === 0, exitCode: code, recap: recap.trim(), output: out.length > OUTPUT_LIMIT ? `${out.slice(0, OUTPUT_LIMIT)}\n... (${out.length - OUTPUT_LIMIT} more characters)` : out });
    });
  });
}

export async function listEvidence(root = EVIDENCE_ROOT) {
  let entries = [];
  try { entries = await fs.readdir(root, { withFileTypes: true }); } catch { return []; }
  const folders = entries.filter((e) => e.isDirectory()).map((e) => e.name).sort();
  const result = [];
  for (const folder of folders) {
    const files = (await fs.readdir(path.join(root, folder))).filter((f) => f.endsWith('.json')).sort();
    result.push({ folder, path: path.join(root, folder), files });
  }
  return result;
}

export async function releaseStatus(root = EVIDENCE_ROOT, folder) {
  const all = await listEvidence(root);
  if (!all.length) return { found: false, message: `no evidence folders under ${root}` };
  const chosen = folder ? all.find((e) => e.folder === folder) : all[all.length - 1];
  if (!chosen) return { found: false, message: `no evidence folder named ${folder}` };
  const summary = { found: true, folder: chosen.folder, path: chosen.path, files: {} };
  for (const file of chosen.files) {
    try {
      summary.files[file] = JSON.parse(await fs.readFile(path.join(chosen.path, file), 'utf8'));
    } catch (err) {
      summary.files[file] = { unreadable: err.message };
    }
  }
  const deployment = summary.files['deployment.json'];
  if (deployment) summary.deployment_status = deploymentStatus(deployment);
  const smoke = summary.files['smoke-tests.json'];
  if (smoke?.tests) summary.smoke_tests = smoke.tests;
  return summary;
}

// Story mode writes one deployment job per story; promotion mode writes the promotion after the run.
export function deploymentStatus(deployment) {
  const jobs = Array.isArray(deployment.deploy_jobs) ? deployment.deploy_jobs.map((j) => j?.status).filter(Boolean) : [];
  if (jobs.length) return jobs.every((st) => st === 'Successful') ? 'Successful' : jobs.find((st) => st !== 'Successful');
  return deployment.job?.status || deployment.promotion_after?.status || deployment.promotion?.status || 'unknown';
}

function text(value) {
  return { content: [{ type: 'text', text: typeof value === 'string' ? value : JSON.stringify(value, null, 2) }] };
}

export function createServer() {
  const server = new McpServer({ name: 'agentia-ansible', version: '0.1.0' });

  server.tool('list_playbooks', 'List the governed Copado release playbooks this server can run', {}, async () => text(PLAYBOOKS));

  server.tool('run_release_playbook',
    'Run the Copado release window playbook: validate each story and wait for its check-only deployment, run Robotic Testing smoke tests, then promote and deploy (story mode: the Copado Submit per story; promotion mode: merge_and_deploy on an existing promotion), wait and write evidence. Without approve=true the playbook stops at the human approval step, so an agent cannot deploy on its own.',
    {
      story_ids: z.array(z.string()).min(1).describe('Copado user story ids or names, for example ["US-0042"]'),
      deploy_mode: z.enum(['story', 'promotion']).default('story').describe('story: Copado Submit per story (default); promotion: run an existing promotion'),
      promotion_id: z.string().optional().describe('18-character Copado promotion id; required in promotion mode, must not be a validation promotion'),
      crt_job_id: z.string().optional().describe('Robotic Testing job id for the smoke suite'),
      crt_project_id: z.string().optional().describe('Robotic Testing project id'),
      repo_dir: z.string().describe('Git working copy of the Salesforce project'),
      evidence_dir: z.string().optional().describe('Folder for evidence files; default: a dated folder under the evidence root'),
      approve: z.boolean().default(false).describe('true skips the human approval pause; only with explicit human consent'),
      check: z.boolean().default(false).describe('Run in Ansible check mode (no changes)'),
      demo: z.boolean().default(false).describe('Run against the fake Agentia CLI with recorded answers'),
    },
    async (args) => {
      const stamp = new Date().toISOString().replace(/[:.]/g, '-');
      const evidenceDir = args.evidence_dir || path.join(EVIDENCE_ROOT, stamp);
      if (args.deploy_mode === 'promotion' && !/^[A-Za-z0-9]{18}$/.test(args.promotion_id || '')) {
        return text({ ok: false, error: 'promotion mode needs an 18-character promotion_id' });
      }
      const extra = { story_ids: args.story_ids, deploy_mode: args.deploy_mode, promotion_id: args.promotion_id || '', crt_job_id: args.crt_job_id || '', crt_project_id: args.crt_project_id || '', repo_dir: args.repo_dir, evidence_dir: evidenceDir, approve: args.approve };
      if (args.demo) { extra.poll_interval = 1; extra.wait_timeout = 60; }
      const result = await runPlaybook('release_window', extra, { demo: args.demo, check: args.check });
      return text({ ...result, evidence_dir: evidenceDir });
    });

  server.tool('run_playbook',
    'Run one of the collection playbooks with extra variables (nightly_validate or remediate_failed_job; release_window has its own tool)',
    {
      name: z.enum(['nightly_validate', 'remediate_failed_job']),
      extra_vars: z.record(z.any()).default({}).describe('Playbook variables, for example {"job_id": "a4N..."}'),
      check: z.boolean().default(false),
      demo: z.boolean().default(false),
    },
    async (args) => text(await runPlaybook(args.name, args.extra_vars, { demo: args.demo, check: args.check })));

  server.tool('list_evidence', 'List evidence folders written by the playbooks', {
    root: z.string().optional().describe('Evidence root; default from AGENTIA_EVIDENCE_ROOT'),
  }, async (args) => text(await listEvidence(args.root || EVIDENCE_ROOT)));

  server.tool('release_status', 'Summarize the latest (or a named) evidence folder: deployment status, smoke tests, health checks', {
    root: z.string().optional(),
    folder: z.string().optional().describe('Evidence folder name; default: the latest'),
  }, async (args) => text(await releaseStatus(args.root || EVIDENCE_ROOT, args.folder)));

  return server;
}

const invokedDirectly = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invokedDirectly) {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
