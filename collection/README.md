# chamanswami555.agentia

Ansible modules, playbooks and an Event-Driven Ansible source for the Copado Agentia CLI.
Salesforce releases run in Copado; everything else in an enterprise release window runs in
Ansible. This collection puts both in one playbook, with approvals, retries and evidence.

## Requirements

- Ansible core 2.17 or newer, Python 3.10 or newer on the control node
- Copado Agentia CLI (`npm install -g @copado/agentia-cli@beta`) authenticated with
  `agentia auth set --cicd <api-key> --region <region>` or the `AGENTIA_CICD_API_KEY`
  environment variable. Copado AI and Robotic Testing credentials are optional.
- For the event source: ansible-rulebook (Event-Driven Ansible), which needs Java 17.

Credentials are never module options. The modules run the CLI, which reads them from its
keychain or the environment, and they never print them.

## Modules

| Module | Purpose |
| --- | --- |
| `agentia_auth_info` | Report which credentials are configured; fail early when one is missing |
| `agentia_work` | Create, update or delete a user story, idempotently, with check and diff mode |
| `agentia_work_submit` | Submit the active story for validation or promotion |
| `agentia_promotion` | Run or resume a promotion (merge or merge and deploy) and wait for it |
| `agentia_job_info` | Read one job execution with steps and logs, or list job executions |
| `agentia_job_wait` | Poll a job execution until it reaches a final status |
| `agentia_job_action` | Run, resume, pause or cancel a job execution |
| `agentia_test_run` | Run a Robotic Testing job and wait for the result |
| `agentia_metadata_compare` | Compare metadata between orgs or Git branches |
| `agentia_health_check` | Run the organization governance health check |
| `agentia_ai_ask` | Ask a Copado AI agent one question |

Every module accepts `cli_path`, `working_dir` and `timeout`, returns the CLI
`transaction_id`, and fails with the CLI's own error message when a call fails.

## Playbooks

| Playbook | What it does |
| --- | --- |
| `release_window.yml` | Health check, validate stories, merge, smoke tests, human approval, deploy, wait, evidence folder |
| `nightly_validate.yml` | Validate every story in flight and run the smoke suite, no deployment, nightly report |
| `remediate_failed_job.yml` | Read a failed job, ask the Copado AI Operate agent for a diagnosis, write an incident file, optionally resume |

Run a playbook with `ansible-playbook chamanswami555.agentia.release_window -e story_ids='["US-0042"]' -e promotion_id=a0B...`.

## Event-Driven Ansible

The source `chamanswami555.agentia.agentia_jobs` polls Copado job executions (and optionally
promotions) through the CLI and emits an event on every status change. The rulebook
`extensions/eda/rulebooks/copado_release.yml` runs `remediate_failed_job` when a job ends in
Error or Failed. Start it with `ansible-rulebook --rulebook copado_release.yml -i inventory.yml`.

## Offline demo and tests

`tools/fake-agentia/agentia` in the repository replays recorded CLI answers from
`tests/fixtures/agentia`, so the unit tests and the demo run without a Copado licence.
`make check` in the repository root runs lint, the tests and the module documentation check.
