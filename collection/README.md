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
| `agentia_promotion` | Run or resume an existing promotion (merge or merge and deploy) and wait for it |
| `agentia_promotion_info` | Read one promotion (status, validation flag, last promotion and deployment job ids) or list a story's promotions |
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
| `release_window.yml` | Health check, validate each story and wait for its promote job and its check-only deployment job, smoke tests, human approval, then promote and deploy: in story mode (default) with the Copado Submit for each story (`work submit --done`), waiting for the promote job and the deployment job; in promotion mode with `merge_and_deploy` on an existing promotion; evidence folder |
| `nightly_validate.yml` | Validate every story in flight (waiting for each validation deployment), run the smoke suite, no deployment, nightly report; fails when any validation or smoke test failed |
| `remediate_failed_job.yml` | Read a failed job, ask the Copado AI Operate agent for a diagnosis, write an incident file, optionally resume |

Run the release window from the Git working copy of the Salesforce project:

```sh
# story mode (default): validate, approve, then Copado Submit (promote and deploy) per story
ansible-playbook chamanswami555.agentia.release_window -e '{"story_ids": ["US-0042"]}'
# promotion mode: run merge_and_deploy on an existing, non-validation promotion
ansible-playbook chamanswami555.agentia.release_window -e '{"story_ids": ["US-0042"], "deploy_mode": "promotion", "promotion_id": "a0B000000000001EAA"}'
```

Useful variables: `approve: true` skips the human pause, `skip_local_tests: true` skips the local
quality gates before the submit, `poll_interval` (seconds between job polls, default 15) and
`wait_timeout` (longest wait for one job, default 1800), `evidence_dir`.

## Event-Driven Ansible

The source `chamanswami555.agentia.agentia_jobs` polls Copado job executions (and optionally
promotions) through the CLI and emits an event on every status change. The rulebook
`extensions/eda/rulebooks/copado_release.yml` runs `remediate_failed_job` when a job ends in
Error or Failed. Start it with `ansible-rulebook --rulebook copado_release.yml -i inventory.yml`.
ansible-rulebook needs Java 17 and `ansible-galaxy` on the PATH; on macOS with Homebrew, point
`JAVA_HOME` at the JDK home itself (`/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home`),
not at the formula folder, or the engine starts without a JVM and never emits an event.

## Verified against a real Copado org

On 14 October 2026 the collection ran against a Copado Playground (Copado Pipelines, Salesforce
Source Format, region na) with Agentia CLI 1.0.0-beta.5:

- Modules: auth, health check, story create, idempotent re-run, update and delete, job reads.
- Release window in story mode, started through `agentia ansible scaffold` and
  `agentia ansible run --approve`: validation promotion created and its deployment job waited for,
  Copado Submit per story, promote job and deployment job waited for, the story's custom label
  promoted from the INT environment to the UAT environment (an earlier manual Copado Submit had
  taken it from Dev1 to INT), four evidence files written (`validations.json`, `deployment.json`,
  health checks before and after). Recap: 17 ok, 7 changed, 0 failed.
- Release window again, after the validation-deployment wait was added, on a second story
  (a custom permission) from Dev1 to INT: validation promotion with its promote job and its
  check-only deployment job, Copado Submit promotion with promote and deployment jobs, all
  Successful. Recap: 21 ok, 7 changed, 0 failed.
- Event source `agentia_jobs` inside `ansible-rulebook` 1.3.2: two polls, one event per job
  (eleven jobs, including the promote job that was running at the time), rule fired on each.
  The shipped rulebook `copado_release.yml` then ran for eight minutes during the second
  release: four status-change events (In Progress to Successful), the success rule fired on
  each, no remediation because nothing failed.

The scrubbed CLI answers of these runs are the `live/` fixtures under `tests/fixtures/agentia`.

## Offline demo and tests

`tools/fake-agentia/agentia` in the repository replays recorded CLI answers from
`tests/fixtures/agentia`, so the unit tests and the demo run without a Copado licence.
`make check` in the repository root runs lint, the tests and the module documentation check;
`make sanity` and `make integration` run `ansible-test` sanity and the five integration targets
under `tests/integration` (they use the fake CLI in `tests/integration/targets/setup_fake_agentia`).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the release notes of every version.
