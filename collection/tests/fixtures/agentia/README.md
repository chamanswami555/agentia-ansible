# Agentia CLI fixtures

Recorded answers replayed by `tools/fake-agentia/agentia` during unit tests and the offline demo.

Status of each file is tracked here, because the two kinds must never be confused:

| File | Origin |
| --- | --- |
| work-get-US-0001.json | Synthetic, shaped after the `cicd work get --json` example in the Agentia CLI README (1.0.0-beta.4) |
| work-get-missing.json | Synthetic, shaped after the CLI error envelope |
| work-list-found.json, work-list-empty.json | Synthetic; the real list shape is to be confirmed and re-recorded |
| work-create.json, work-update-US-0001.json, work-delete.json | Synthetic |
| work-get-with-warning.txt | Synthetic; reproduces the beta-update warning the CLI prints before JSON |
| work-get-broken.txt | Synthetic; non-JSON output |

When real Copado access is available, every synthetic file is replaced by a recording of the
real command with ids, names and secrets scrubbed, and this table is updated.
