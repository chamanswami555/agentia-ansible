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
| work-list.json, work-get-US-0000024.json | the playground's first user story |
| job-list.json, job-get.json, job-log-get.json | the SFDX Git initialization job and its log |
| promotion-list.json | empty promotion list |
| user-get.json | the authenticated user |

Real shapes worth knowing: list commands return `result.data` plus `currentPage`, `pageSize`,
`totalPages`, `totalRecords`, `hasMore`, `nextCursor`; connection and stage-connection lists return
a plain list; a job carries `steps` (name, status) and `template` as an object; a job log is
`{jobId, log, resultId, stepId}`; a credential's default flag is `defaultCredential`.

## Synthetic files (top folder)

Hand-written before live access existed, shaped after the CLI README and help text. They cover
flows that have not been recorded yet (work submit, promotion run and resume, Robotic Testing runs,
Copado AI answers, error cases) and the multi-step job scenarios.

| File | Origin |
| --- | --- |
| work-get-US-0001.json, work-list-found.json, work-list-empty.json, work-create.json, work-update-US-0001.json, work-delete.json | Synthetic story flow |
| work-get-missing.json, work-get-nocreds.json | Synthetic error envelopes; the nocreds message is the real text the CLI prints without a key |
| work-set-US-0042.json, work-submit.json, work-submit-done.json | Synthetic; to be re-recorded after the first real submit |
| work-get-with-warning.txt, work-get-broken.txt | Synthetic warning-prefix and non-JSON outputs |
| auth-get-configured.json, auth-get-missing.json | Synthetic, shaped after the real `auth get` |
| health-check.json | Synthetic |
| promotion-run.json, promotion-resume.json, promotion-list-US-0042.json | Synthetic; to be re-recorded after the first real promotion |
| job-get-inprogress.json, job-get-success.json, job-get-error.json, job-get-deploy-success.json, job-log.json, job-list.json, job-list-cycle1.json, job-list-cycle2.json, job-resume.json | Synthetic job scenarios |
| metadata-compare.json, test-run-pass.json, test-run-fail.json, ai-ask.json | Synthetic |

Each synthetic file is replaced by a recording as soon as the corresponding real flow has run.
