# agentia-ansible

[![CI](https://github.com/chamanswami555/agentia-ansible/actions/workflows/ci.yml/badge.svg)](https://github.com/chamanswami555/agentia-ansible/actions/workflows/ci.yml)

Run Copado releases from Ansible. This repository turns the Copado Agentia Headless CLI into
first-class Ansible building blocks: a collection of idempotent modules and governed playbooks, an
Event-Driven Ansible source that reacts to Copado job events, an Agentia CLI plugin command that
scaffolds and runs the playbooks, an MCP server for AI agents, and an Agent Skill. Everything in
it has run against a real Copado org (section "Verified against a real Copado org").

## Why

Platform teams already run their change windows from Ansible and Ansible Automation Platform:
inventories, schedules, approvals, evidence. Salesforce releases through Copado sit outside that
world; somebody presses Submit in Copado, waits, and pastes screenshots into the change ticket.
Agentia Headless gives Copado a scriptable CLI with JSON output. This project puts that CLI where
operations teams already work:

- Modules that are idempotent and support check mode and diff mode, so a playbook can be dry-run.
- Playbooks with a human approval pause, a validation stage that waits for the real check-only
  deployment, and an evidence folder per run (health checks, validations, deployment, test results)
  with Copado's own transaction ids.
- An event source so a failed Copado job starts a remediation playbook on its own.
- Nothing bypasses Copado: every call is a public `agentia ... --json` command.

## What is inside

| Folder | Component | Contents |
| --- | --- | --- |
| `collection/` | Ansible collection `chamanswami555.agentia` | 12 modules, 3 playbooks, an Event-Driven Ansible source and rulebook, 59 unit tests, recorded CLI answers |
| `plugin/` | Agentia CLI plugin `agentia-plugin-ansible` | Commands `agentia ansible scaffold` and `agentia ansible run`, built with the official plugin SDK |
| `mcp/` | MCP server `agentia-ansible-mcp` | Five tools that let an AI agent run the governed playbooks and read the evidence; 5 tests |
| `skills/agentia-ansible/` | Agent Skill | Teaches a coding agent how to author and run playbooks with the collection |
| `tools/` | Development tools | Fake Agentia CLI that replays recorded answers, offline demos (playbooks and rulebook), a local quality gates script for Copado projects, fixture recorder with scrubbing, handbook PDF build |
| `docs/` | Project handbook | Decisions, facts, command log and terminology of the project (Markdown and PDF) |

### Modules

| Module | Purpose |
| --- | --- |
| `agentia_auth_info` | Report which credentials are configured; fail early when one is missing |
| `agentia_work` | Create, update or delete a user story, idempotently, with check and diff mode |
| `agentia_work_submit` | Submit the active story for validation, or promote and deploy it with the Copado Submit (`--done`) |
| `agentia_promotion` | Run or resume an existing promotion (merge, or merge and deploy) and wait for it |
| `agentia_promotion_info` | Read one promotion (status, validation flag, promote and deployment job ids) or list a story's promotions |
| `agentia_job_info` | Read one job execution with steps and logs, or list job executions |
| `agentia_job_wait` | Poll a job execution until it reaches a final status |
| `agentia_job_action` | Run, resume, pause or cancel a job execution |
| `agentia_test_run` | Run a Robotic Testing job and wait for the result |
| `agentia_metadata_compare` | Compare metadata between orgs or Git branches |
| `agentia_health_check` | Run the organization governance health check |
| `agentia_ai_ask` | Ask a Copado AI agent one question |

### Playbooks

| Playbook | What it does |
| --- | --- |
| `release_window.yml` | Health check; validate each story and wait for its promote job and its check-only deployment job; optional Robotic Testing smoke suite; human approval pause; then, in story mode, the Copado Submit per story (`work submit --done`) with waits on the promote job and the deployment job, or, in promotion mode, `merge_and_deploy` on an existing promotion; evidence folder; health check after |
| `nightly_validate.yml` | Validate every story in flight, wait for each validation deployment, run the smoke suite, write a report, fail if anything failed; no deployment |
| `remediate_failed_job.yml` | Read a failed job and its log, ask the Copado AI Operate agent for a diagnosis when AI is configured, write an incident file, optionally resume the job |

### Event-Driven Ansible

The source `chamanswami555.agentia.agentia_jobs` polls Copado job executions (and optionally
promotions) through the CLI and emits one event per status change. The rulebook
`collection/extensions/eda/rulebooks/copado_release.yml` runs `remediate_failed_job` when a job ends
in Error or Failed and records successful jobs.

## How it uses Agentia Headless

| Extensibility surface | Used how |
| --- | --- |
| CLI with `--json` | Every module runs a public command, parses the `{result, status, transactionId}` envelope (tolerating the warning line a linked plugin prints), returns the transaction id, and fails with Copado's own error message |
| Plugin command (plugin SDK and generator) | `agentia ansible scaffold` reads the active story through the host API (or takes `--stories`) and writes a playbook that imports the collection's release window; `agentia ansible run` runs it with `--check`, `--approve` and `--json` |
| MCP | `mcp/server.mjs` exposes `list_playbooks`, `run_release_playbook`, `run_playbook`, `list_evidence` and `release_status`, so an AI agent triggers the governed playbooks instead of raw commands and cannot skip the approval pause without `approve: true` |
| Agent Skill | `skills/agentia-ansible/SKILL.md` gives a coding agent the module order, the real shapes learned from Copado and the rules for safe playbooks |

## Verified against a real Copado org

On 14 October 2026 everything below ran against a Copado Playground (Copado Pipelines, Salesforce
Source Format, region na) with Agentia CLI 1.0.0-beta.5. The scrubbed CLI answers of these runs
are the `live/` fixtures under `collection/tests/fixtures/agentia`, and the unit tests assert on
those real shapes.

| Run | Result |
| --- | --- |
| Modules smoke test (auth, health check, story create, idempotent re-run, update, delete, job reads) | 8 ok, 3 changed, 0 failed |
| Release window through the plugin, story US-0000024 from INT to UAT (validation promotion, Copado Submit, promote and deployment jobs) | 17 ok, 7 changed, 0 failed |
| Release window again after the validation-deployment wait was added, story US-0000026 (a custom permission) from Dev1 to INT | 21 ok, 7 changed, 0 failed |
| Event source inside `ansible-rulebook` 1.3.2, two polls | 11 job events, rule fired on each |
| Shipped rulebook `copado_release.yml` for eight minutes during a release | 4 status-change events, success rule fired on each, no remediation because nothing failed |

Not yet run live: promotion mode (`merge_and_deploy` on an existing non-validation promotion),
Robotic Testing and Copado AI, which the playground has no licence for. Those modules are covered
by tests against answers shaped after the CLI documentation. The first live runs skipped the local
quality gates (`skip_local_tests: true`) because the CLI's stock sample gate fails on this machine;
with `tools/quality-gates/agentia_quality_gates.sh` installed in the project, a later validation
submit ran the gate (exit 0) and reached its check-only deployment job without the skip.

## Quick start

### Offline, without a Copado licence

Requirements: Python 3.12 with [uv](https://docs.astral.sh/uv/), GNU make.

```sh
git clone git@github.com:chamanswami555/agentia-ansible.git
cd agentia-ansible
make setup                      # .venv with ansible-core and pytest; links the collection under var/
make check                      # pyflakes, ansible-lint, 59 unit tests, ansible-doc for every module
make demo                       # the three playbooks, then the rulebook, against the fake CLI
make sanity                     # ansible-test sanity on a copy of the collection (installs its requirements)
```

The fake CLI (`tools/fake-agentia/agentia`) replays recorded answers, logs every call, and answers
job polls in sequence (running, then finished), so the demo shows the whole release flow in a few
seconds. It fails unless the release reaches a successful deployment job. The rulebook demo
(`tools/demo/offline-rulebook-demo.sh`, Java 17 needed) lets a job turn to Error on the second poll
and fails unless `remediate_failed_job` ran and wrote the incident file.

### Live, with a Copado CI/CD API key

Requirements: Node.js 20 or newer, the Agentia CLI (`npm install -g @copado/agentia-cli@beta`),
a Copado org with Copado Pipelines, and a clone of the Salesforce project repository that Copado
manages.

```sh
# 1. authenticate the CLI (the key comes from Copado's Account Summary, API Key tab)
agentia auth set --cicd <key> --region na
agentia cicd health-check --json

# 2. install the collection
ansible-galaxy collection build collection --output-path var/build
ansible-galaxy collection install var/build/chamanswami555-agentia-0.1.0.tar.gz

# 3. install the plugin command
cd plugin && npm install && npm run build && cd ..
agentia plugins link plugin

# 4. in the clone of the Salesforce project, with a story that has published commits:
agentia ansible scaffold --stories US-0001 --repo-dir . --out release-window.yml
agentia ansible run --playbook release-window.yml --check
agentia ansible run --playbook release-window.yml --approve
```

Without the plugin, the playbook runs directly:

```sh
ansible-playbook chamanswami555.agentia.release_window -e '{"story_ids": ["US-0001"], "repo_dir": "/path/to/clone"}'
```

Useful variables: `approve: true` skips the pause, `skip_local_tests: true` skips the local
quality gates, `deploy_mode: promotion` with `promotion_id` uses an existing promotion,
`poll_interval` and `wait_timeout` tune the waits, `evidence_dir` sets the evidence folder.

Local quality gates: `agentia cicd work test` and `work submit` run the project's
`.agentia_quality_gates.sh` when it exists, and the CLI's stock sample otherwise.
`tools/quality-gates/agentia_quality_gates.sh` is a deterministic, offline gate for Source Format
projects (well-formed XML, no org ids or credentials, a test class for every changed Apex class,
file size); copy it to the project root as `.agentia_quality_gates.sh`.

### Event-Driven Ansible

`ansible-rulebook` needs Java 17 and `ansible-galaxy` on the PATH. On macOS with Homebrew, set
`JAVA_HOME` to the JDK home itself (`/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home`).

```sh
uv pip install --python .venv/bin/python ansible-rulebook
ansible-rulebook --rulebook collection/extensions/eda/rulebooks/copado_release.yml \
  -i collection/extensions/eda/inventory.yml --print-events
```

### MCP server and Agent Skill

See [mcp/README.md](mcp/README.md) for the client configuration and
[skills/agentia-ansible/SKILL.md](skills/agentia-ansible/SKILL.md) for the skill.
`node mcp/live-check.mjs <story> <clone>` drives the server over stdio against a real org in
check mode and prints the recap and the latest evidence summary.

## Design notes

- Story mode is the default because it matches what Copado does on the Submit button: a `work
  submit` creates a validation promotion that can only validate, and `work submit --done` creates
  the promotion that promotes and deploys. Promotion mode exists for teams that already hold a
  promotion id.
- A submit returns the id of the promote job; the check-only deployment is a second job that the
  promotion record names once it exists. The playbooks read the promotion until that id appears
  and wait for the deployment job before anyone approves.
- Every list answer of the CLI comes back as `result.data` with pagination; the module helper
  (`collection/plugins/module_utils/agentia.py`) hides that, maps CLI errors to Ansible failures
  with the transaction id, and tolerates the warning line the CLI prints when a plugin is linked.
- The recorded answers are scrubbed before they enter the repository: every email address and
  Salesforce username becomes `user@example.com`; signature and token fields become `REDACTED`.
  `collection/tests/fixtures/agentia/README.md` lists the origin of every file.
- The tests were checked by removing the code they protect and watching them fail; the offline
  demo asserts on the fake CLI's call log and on the evidence files, not on the recap alone.

## Tests and CI

| Suite | Command | Count |
| --- | --- | --- |
| Collection unit tests (modules, helper, event source, real shapes, error paths) | `make test` | 59 |
| Plugin | `cd plugin && npm test` | 3 |
| MCP server (including the release window end to end in demo mode) | `cd mcp && npm test` | 5 |

`.github/workflows/ci.yml` runs `make check` (pyflakes, ansible-lint, unit tests, module docs),
the offline playbook demo, the offline rulebook demo with Java 17, the MCP server tests and the
plugin tests on every push, and keeps the demo evidence as an artifact.

## Repository layout

```
collection/                 the Ansible collection (galaxy.yml, plugins, playbooks, extensions/eda, tests)
plugin/                     the Agentia CLI plugin (TypeScript, oclif)
mcp/                        the MCP server (Node.js)
skills/agentia-ansible/     the Agent Skill
tools/fake-agentia/         fake CLI used by tests and the demo
tools/demo/                 offline demo script
tools/record-fixtures.py    turns recorded CLI answers into scrubbed fixtures
docs/                       project handbook (Markdown and PDF)
Makefile                    setup, lint, test, docs, check
```

## Licence

MIT. See [LICENSE](LICENSE).
