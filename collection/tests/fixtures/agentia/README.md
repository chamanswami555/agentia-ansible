# Agentia CLI fixtures

Recorded answers replayed by `tools/fake-agentia/agentia` during unit tests and the offline demo.
`index.json` maps a command line (arguments without `--json`) to a file and exit code; an entry
with `files` answers successive calls with successive files. `index-nocreds.json` is the index for
the "no credentials configured" scenario, selected with `AGENTIA_FAKE_INDEX`.

Origin of every file, because synthetic and recorded answers must never be confused:

| File | Origin |
| --- | --- |
| work-get-US-0001.json | Synthetic, shaped after the `cicd work get --json` example in the Agentia CLI README (1.0.0-beta.4) |
| work-get-missing.json, work-get-nocreds.json | Synthetic, shaped after the CLI error envelope; the nocreds message is the real text the CLI prints without a key |
| work-list-found.json, work-list-empty.json | Synthetic; list shape to be confirmed |
| work-create.json, work-update-US-0001.json, work-delete.json | Synthetic |
| work-set-US-0042.json, work-submit.json, work-submit-done.json | Synthetic; field names guessed from the CLI help text |
| work-get-with-warning.txt | Synthetic; reproduces the beta-update warning the CLI prints before JSON |
| work-get-broken.txt | Synthetic; non-JSON output |
| auth-get-configured.json, auth-get-missing.json | Synthetic, shaped after the real `auth get --json` output seen on 9 October 2026 (config files, credentials with set, type, issues, missing) |
| health-check.json | Synthetic |
| promotion-run.json, promotion-resume.json | Synthetic; field names guessed |
| job-get-inprogress.json, job-get-success.json, job-get-error.json, job-get-deploy-success.json, job-log.json, job-list.json, job-list-cycle1.json, job-list-cycle2.json, job-resume.json | Synthetic |
| metadata-compare.json | Synthetic |
| test-run-pass.json, test-run-fail.json | Synthetic |
| ai-ask.json | Synthetic, shaped after the `agentia_ai_ask` MCP notes (warnings, followups, links) |

When real Copado access is available, every synthetic file is replaced by a recording of the
real command with ids, names and secrets scrubbed, and this table is updated.
