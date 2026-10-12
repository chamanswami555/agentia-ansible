---
name: agentia-ansible
description: Use this skill when a coding agent must author, review or run Ansible playbooks that drive Copado through the Agentia CLI with the chamanswami555.agentia collection: release windows, nightly validation, failed-job remediation, and Event-Driven Ansible rulebooks reacting to Copado job events. Use it whenever the user mentions Ansible, playbooks, rulebooks or Ansible Automation Platform together with Copado, Agentia or Salesforce releases.
---

# Agentia Ansible

Use this skill to turn Copado pipeline state into a governed Ansible playbook, and to run or
troubleshoot the collection's playbooks, without guessing module names, order or options.

## Start Here

1. Confirm the collection is available: `ansible-galaxy collection list chamanswami555.agentia`
   (or `ANSIBLE_COLLECTIONS_PATH` points at a checkout). Confirm the CLI is authenticated with
   `agentia auth get --json`; never print the key.
2. Read the pipeline state before writing a playbook. Prefer Agentia MCP tools
   (`agentia_work_list`, `agentia_promotion_list`, `agentia_pipeline_get`, `agentia_job_list`);
   fall back to `agentia cicd work list --json`, `agentia cicd promotion list --json`.
3. Pick the playbook shape below. Do not invent story ids, promotion ids, job ids or CRT ids;
   use the values read in step 2.
4. Run in check mode first: `ansible-playbook <playbook> --check`. Then run for real.

## Module Order For A Release

`agentia_auth_info (require: [cicd])` -> `agentia_health_check` -> `agentia_work_submit`
(validate, one task per story, `set_story`) -> `agentia_promotion (operation: merge)` ->
`agentia_test_run` (Robotic Testing smoke suite) -> `ansible.builtin.pause` (human approval) ->
`agentia_promotion (operation: merge_and_deploy)` -> `agentia_job_wait` -> `agentia_health_check`
-> write evidence files with `ansible.builtin.copy`.

The reference playbook is `chamanswami555.agentia.release_window`; copy its structure instead of
writing a new one when the user wants a release window.

## Modules

| Need | Module | Notes |
| --- | --- | --- |
| Fail early without credentials | `agentia_auth_info` | `require: [cicd]`; add `ai` or `crt` when those modules are used |
| Create or update a story | `agentia_work` | Idempotent; `id` for an existing story, `title` to create; `state: absent` deletes |
| Validate or promote a story | `agentia_work_submit` | Needs `working_dir` (the Git checkout); `done: true` promotes, only after approval |
| Merge or deploy a promotion | `agentia_promotion` | `operation: merge` first, `merge_and_deploy` after approval; `resume` after a conflict |
| Watch a job | `agentia_job_info`, `agentia_job_wait` | `job_wait` fails on Error unless `fail_on_error: false` |
| Act on a job | `agentia_job_action` | `resume`, `run`, `pause`, `kill` |
| Run Robotic Testing | `agentia_test_run` | Fails the task when the run fails unless `fail_on_test_failure: false` |
| Compare metadata | `agentia_metadata_compare` | Pre-release drift evidence |
| Governance check | `agentia_health_check` | Before and after the release |
| Explain a failure | `agentia_ai_ask` | `agent: operate`; needs AI credentials |

Every module takes `cli_path`, `working_dir`, `timeout` and returns `transaction_id`; put the
transaction id in evidence files so Copado support can trace a call.

## Guardrails

- Never run `agentia_work_submit` with `done: true` or `agentia_promotion` with
  `merge_and_deploy` before a human approval step, unless the user explicitly asked for an
  unattended deployment.
- Never put API keys, PAKs or tokens in playbooks, inventories or extra vars. The CLI reads
  them from its keychain or `AGENTIA_*` environment variables.
- Keep `skip_pull_request: true` in automation; browser steps have no place in a playbook.
- Write evidence (health checks, validations, test results, deployment job) to a dated folder;
  a release without evidence is not finished.
- For Event-Driven Ansible, use the `chamanswami555.agentia.agentia_jobs` source and the
  `copado_release.yml` rulebook as the template; route Error and Failed to
  `remediate_failed_job`, and keep `resume_on_failure` false until the team agrees.

## Report Back

After running a playbook, report: which stories, promotion and jobs were touched, the final job
status, where the evidence folder is, and every CLI transaction id from failed tasks. Do not
include secrets.
