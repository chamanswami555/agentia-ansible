# Demo video script (5 minutes)

Rules from the hackathon: 5 minutes or less, uploaded as a file, 300 MB or less, original work, and
"functionality must match what is presented in the demo video". Everything below was rehearsed on
the Copado Playground; the numbers quoted are from those runs.

Recording setup: 1920 x 1080, terminal at 18 pt with a light theme, browser tab with the Copado
Playground open on the Promotions list, one take per section (sections are cut together).
Narration in plain English, short sentences. Nothing about how the project was built or with
what tools.

Demo story prepared on 16 October 2026: US-0000028 "Release operator permission set" in Dev1 of
the playground, one commit (a permission set), published, scaffold written to
`var/playground-repo/release-window.yml`. The run takes about four minutes of waiting in total,
so the two waits are shown as time-lapse cuts.

| Time | Screen | Say |
| --- | --- | --- |
| 0:00 to 0:25 | Slide 1 (title), then slide 2 (the problem) | "A Salesforce change rarely ships alone. The same change ticket carries a database migration, an infrastructure change, a feature flag. Platform teams already run all of those from Ansible, with one approval and one evidence trail. The Salesforce step is the exception: someone presses Submit in Copado and pastes screenshots into the ticket. agentia-ansible makes the Copado release one more step in that same run." |
| 0:25 to 0:50 | Slide 3 (what agentia-ansible is: collection, event source, plugin command, MCP server, skill) | "agentia-ansible puts the Copado Agentia CLI inside Ansible. Twelve modules, three playbooks, an event source, a CLI plugin command, an MCP server and an agent skill. Every call is a public agentia command with JSON output." |
| 0:50 to 1:20 | Terminal in the Salesforce project clone: `agentia cicd work get --json` (shows US-0000028), then `agentia ansible scaffold --stories US-0000028 --repo-dir . --out release-window.yml`; then `cat release-window.yml` | "The plugin command reads the active story and writes a playbook. Story mode: validate first, then the Copado Submit, the same action as the button." |
| 1:20 to 1:45 | `agentia ansible run --playbook release-window.yml --check` (recap 14 ok, 0 failed) | "Check mode first. Nothing changes in Copado; the playbook shows what it would do." |
| 1:45 to 3:15 | `agentia ansible run --playbook release-window.yml --approve`; time-lapse through the validation wait; pause on "Read each validation promotion until its deployment job exists" and "Wait for each validation deployment job"; time-lapse through the promote and deployment waits; end on the summary line and the recap (21 ok, 0 failed) | "Validation creates a check-only promotion. The playbook waits for the real validation deployment, not just the first job. Then the Copado Submit: promote job, deployment job, both waited for. The evidence folder holds the health checks, the validations and the deployment with Copado's transaction ids." |
| 3:15 to 3:35 | Browser: Copado Promotions list showing the two new promotions (validation run and the real one) and the deployment job Successful; switch to the INT org and show the permission set | "Here it is in Copado and in the INT org." |
| 3:35 to 4:05 | Terminal: `ansible-rulebook --rulebook collection/extensions/eda/rulebooks/copado_release.yml -i collection/extensions/eda/inventory.yml --print-events` with the fake CLI (`tools/demo/offline-rulebook-demo.sh`), cut to the moment a job turns to Error and the remediation playbook runs; show the incident file | "Event-Driven Ansible. The source polls Copado jobs. A job fails, the rule fires, the remediation playbook reads the log, asks Copado AI for a diagnosis and writes the incident. No human watching a console." |
| 4:05 to 4:30 | Terminal: `node mcp/live-check.mjs US-0000028 .` (recap of a check-mode run), then the test that runs without approval: `grep -n "Deployment not approved" mcp/test/server.test.mjs`; a one-line view of the skill file header | "An AI agent gets five governed tools, not 194 raw ones. Without approval the run stops at the gate and nothing deploys; there is a test for that. The skill teaches a coding agent the same rules." |
| 4:30 to 4:50 | Slide 8 (quality): 74 unit tests at 96 percent coverage, ansible-test sanity 24 tests, ansible-lint production profile, seven-step offline demo, CI badge green, four live rehearsals | "Everything here ran against a real Copado org. The tests fail when the code they protect is removed. The CI badge is on the README." |
| 4:50 to 5:00 | Slide 10 (links: repository, Galaxy name, what is next) | "agentia-ansible. Copado releases, run the way the rest of your platform already runs." |

## Before recording

1. Fresh story in Dev1 with one published commit (US-0000028 is ready; if it has been promoted
   already, create the next one the same way: `agentia cicd work create`, `work set`, commit a
   metadata file, `work publish`).
2. `agentia auth get --json` shows cicd configured; `agentia ansible --help` prints the two commands.
3. `bash tools/demo/offline-rulebook-demo.sh` once, so the rulebook section can be cut from
   `var/rulebook-demo/rulebook.log` if the live take runs long.
4. Close other windows; hide the Copado API key page; the terminal must never show the key.

## Cuts

Time-lapse the two waits (about 90 seconds each) to 10 seconds with a visible "waiting for job
JE-0xx" caption. Keep the recap lines and the summary line at full speed; judges read them.

## Length check

Total speaking text above is about 330 words, which is under four minutes at a calm pace; the
remaining time is the terminal output. Export at 1080p with a bitrate under 7 Mbps so that a
five-minute file stays well under 300 MB.
