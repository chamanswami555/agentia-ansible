# Agentia CLI fixtures

Recorded answers replayed by `tools/fake-agentia/agentia` during unit tests and the offline demo.
`index.json` maps a command line (arguments without `--json`) to a file and exit code; an entry
with `files` answers successive calls with successive files. `index-nocreds.json` is the index for
the "no credentials configured" scenario and `index-live.json` the index that points at real
recordings; both are selected with `AGENTIA_FAKE_INDEX`.

## Real recordings (`live/`)

Recorded on 14 October 2026 from the Copado Playground CS261013SFP (Copado Pipelines, Source
Format, region na) with Agentia CLI 1.0.0-beta.5, through `tools/record-fixtures.py`, which drops
the CLI's warning line and replaces the owner's email addresses and usernames with
`user@example.com`. Salesforce record ids, org names and the owner's display name are kept.

| File | Command |
| --- | --- |
| auth-get.json, auth-set.json | `auth get`, `auth set --cicd ... --region na` (no key in the output) |
| health-check.json | `cicd health-check` |
| pipeline-list.json, pipeline-get.json, pipeline-connection-list.json, stage-list.json, stage-connection-list.json | pipeline, connection and stage reads |
| environment-list.json, credential-list-copado.json, credential-list-dev1.json, environment-auth-status-dev1.json | environments and credentials |
| project-list.json, project-default-get.json, repository-list.json, function-list.json, data-template-list.json | projects, defaults, repository, functions, data templates |
| work-list.json, work-get-US-0000024.json, work-set-US-0000024.json, work-status.json, work-status-after-submit.json | the playground's first user story, its activation and status |
| work-publish.json | `cicd work publish` registering the custom-label commit |
| work-submit.json, work-submit-done.json | `cicd work submit` (validation) and `cicd work submit --done` (promote and deploy) |
| job-list.json, job-get.json, job-log-get.json, job-list-after-submit.json, job-list-latest.json, job-get-validation.json, job-get-validation-1.json, job-log-validation.json, job-get-deploy.json, job-log-deploy.json, job-get-promote-done.json, job-get-deploy-done.json, job-log-deploy-done.json | the Git initialization, promote, validation and deployment jobs with logs (`-1` is the same validation job polled a second time) |
| promotion-list.json, promotion-list-by-story.json, promotion-get.json, promotion-get-XX9ja.json, promotion-get-done.json | promotions: validation runs P00001 and P00002, and the real promotion P00004 with its deployment job |
| user-get.json | the authenticated user |
| auth-set.json, work-test.json | the auth set confirmation and a failed local quality gate (error envelope) |

Real shapes worth knowing: list commands return `result.data` plus `currentPage`, `pageSize`,
`totalPages`, `totalRecords`, `hasMore`, `nextCursor`; connection and stage-connection lists return
a plain list; a job carries `steps` (name, status) and `template` as an object; a job log is
`{jobId, log, resultId, stepId}`; a credential's default flag is `defaultCredential`.

## Synthetic files (top folder)

Hand-written before live access existed, shaped after the CLI README and help text. They cover
flows that have not been recorded yet (promotion run and resume, Robotic Testing runs, Copado AI
answers, error cases) and the multi-step job scenarios.

| File | Origin |
| --- | --- |
| work-get-US-0001.json, work-list-found.json, work-list-empty.json, work-create.json, work-update-US-0001.json, work-delete.json | Synthetic story flow |
| work-get-missing.json, work-get-nocreds.json | Synthetic error envelopes; the nocreds message is the real text the CLI prints without a key |
| work-set-US-0042.json, work-get-US-0042.json, work-submit.json, work-submit-done.json | Synthetic ids; the submit and done files were reshaped on 14 October 2026 after the real recordings (`submit.jobId`, `done.jobId`, a message carrying `promotion_id=` and `job_execution_id=`) |
| work-get-with-warning.txt, work-get-broken.txt | Synthetic warning-prefix and non-JSON outputs |
| auth-get-configured.json, auth-get-missing.json | Synthetic, shaped after the real `auth get` |
| health-check.json | Synthetic |
| promotion-run.json, promotion-resume.json, promotion-run-error.json, promotion-list-US-0042.json, promotion-get-synthetic.json | Synthetic; the promotion get is shaped after the real promotion-get-done.json (`lastDeploymentExecutionId`); run and resume are still to be re-recorded, because the playground only produced validation promotions, which refuse the merge operation |
| job-get-inprogress.json, job-get-success.json, job-get-error.json, job-get-error-6.json, job-get-deploy-success.json, job-log.json, job-list.json, job-list-cycle1.json, job-list-cycle2.json, job-resume.json | Synthetic job scenarios; job-get-error-6.json is the failed job that appears in job-list-cycle2.json, used by the rulebook demo |
| metadata-compare.json, test-run-pass.json, test-run-fail.json, ai-ask.json, ai-ask-string.json | Synthetic; ai-ask-string.json is an answer that comes back as a plain string |

Each synthetic file is replaced by a recording as soon as the corresponding real flow has run.
