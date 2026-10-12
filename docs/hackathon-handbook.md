# Copado Agentia Headless Virtual Hackathon: Project Handbook

| Item | Value |
| --- | --- |
| Document | Project handbook: everything known, done and decided so far |
| Version | 1.4 |
| Date | 2026-10-12 19:44 IST |
| Project owner | chamanswami555 (GitHub) |
| Project folder | /Users/chaman/copado-agentia-hackathon |
| Status | Working draft. Facts marked "verified" were checked against the source on 9 October 2026. Facts marked "not verified" were not. |

How to read this file: Section 1 says where we are and what to do today. Section 10 (Terminology) explains every technical word used anywhere in this file. Section 11 (Command log) lists every command that was run, where, why, and what its output meant. Everything else is reference.

## Contents

1. Decisions and status
2. Actions, in order, with dates
3. The hackathon, complete
4. Access to Copado and the CLI
5. Agentia Headless explained
6. Competition map
7. Idea research
8. Red Hat Certified Professional of the Year 2027
9. Risks and failure modes
10. Terminology
11. Command log
12. Sources
13. Open decisions

## 1. Decisions and status

Decided so far:

| Decision | Value | Basis |
| --- | --- | --- |
| Enter the Copado Agentia Headless Virtual Hackathon | Yes | Owner's call |
| Project folder | /Users/chaman/copado-agentia-hackathon | Owner's pick, 9 October 2026 |
| Idea | Fixed on 10 October 2026: Ansible collection plus Event-Driven Ansible for Agentia CLI (section 7.4). Stretch goals, only after the core is done: an ephemeral per-story environment playbook inside the collection (7.5) and an AWX job template for the demo. | Owner's pick after the research in section 7 |
| Idea lock | Done 10 October 2026 (the earlier rule was: lock within one day of a working CI/CD key, or on 11 October). The feasibility probe in 7.5 now only decides whether the stretch playbook is built. | Owner |
| Red Hat award | Handle separately. Do not merge it with the hackathon project. | Section 8 |
| Build start | Allowed now. The rules only fix the submission window (12 to 26 October 2026). | Official Rules, section 3.2 |

Not decided yet (owner's call): project name, open-source licence, content of the Red Hat nomination.

Done: all research in this file; Agentia CLI installed on this Mac (section 5.10); registration completed by the owner on 10 October 2026 with the company email and the idea text of section 7.10 (idea fixed: Ansible collection plus Event-Driven Ansible; AWX job template kept as a stretch goal); nothing else submitted; nothing deleted.

Where we are (status written 2026-10-12 19:26 IST): registration done (10 October); idea locked; trial started 11 October (Agentia Pipeline) but the CLI API key is blocked on Copado (email from chamanswami555@gmail.com, AppExchange request, community); Git repository chamanswami555/agentia-ansible (private) with SSH alias github-agentia, author Chaman Swami <chamanswami555@gmail.com>.

Build progress, offline (no Copado access needed), all pushed to main (commits c2a2531, 0c0ba56, 4a3b421):
- Ansible collection `chamanswami555.agentia` in `collection/`: 11 modules (agentia_auth_info, agentia_work, agentia_work_submit, agentia_promotion, agentia_job_info, agentia_job_wait, agentia_job_action, agentia_test_run, agentia_metadata_compare, agentia_health_check, agentia_ai_ask), shared CLI helper in `plugins/module_utils/agentia.py` (JSON envelope parsing, warning-line tolerance, error mapping with transaction id), three playbooks (`release_window.yml`, `nightly_validate.yml`, `remediate_failed_job.yml`), an Event-Driven Ansible source `agentia_jobs` with the rulebook `copado_release.yml`, and `collection/README.md`.
- Fake CLI `tools/fake-agentia/agentia` replaying fixtures from `collection/tests/fixtures/agentia` (all synthetic so far; table in its README); 43 unit tests, pyflakes clean, `ansible-doc` valid for all modules (`make check`); two mutation checks proved key tests go red without their code.
- Offline demo `tools/demo/offline-demo.sh` runs the three playbooks end to end against the fake CLI and writes evidence JSON files to `var/demo` (verified locally on 12 October).
- Agent Skill `skills/agentia-ansible/SKILL.md`. GitHub Actions workflow `.github/workflows/ci.yml` (setup, check, offline demo, evidence artifact); its first run was not yet verified from this machine (no gh CLI here).
- Agentia plugin `plugin/` (generated with @copado/create-agentia-plugin 0.4.0, SDK 0.1.1, TypeScript): commands `agentia ansible scaffold` (reads the active story through the SDK host or takes `--stories`, finds the promotion through the public CLI, writes a playbook that imports the collection's release window) and `agentia ansible run` (runs ansible-playbook, `--check`, `--approve`, `--json`); linked into the real CLI with `agentia plugins link`; 3 unit tests; verified end to end against the fake CLI (commit 2bf74b2).
- MCP server `mcp/` (Node, @modelcontextprotocol/sdk): tools list_playbooks, run_release_playbook (stops at the approval pause unless approve=true), run_playbook, list_evidence, release_status; 3 smoke tests over stdio (commit 3a15df5).
- Bugs found and fixed by the tests and runs: explicit story id that does not exist must fail, not create (agentia_work); event source treated interval 0 as missing (30 s sleeps); release playbook was not check-mode safe; plugin run must return structured JSON on failure.
- Python environment `.venv` (ansible-core 2.18.19, pytest 9, pyflakes) via uv, ignored by Git; `var/` ignored. Java is not installed on this Mac, so ansible-rulebook has not been run yet.

Next, in order: (1) owner confirms the CI run is green on GitHub; (2) root README (needs owner approval to replace the GitHub stub); (3) Agentia plugin command `agentia ansible scaffold|run` with the official generator; (4) our MCP server (run release playbook, release status); (5) Java 17 + ansible-rulebook to run the rulebook for real; (6) when Copado answers: `agentia auth set --cicd`, record real fixtures, replace synthetic ones, feasibility probe for the stretch playbook; (7) second Developer Edition org, pipeline, live demo; (8) video, deck, submission by 25 October.

Not done, needs the owner: CI/CD API key (waiting on Copado), Red Hat nomination form (has a reCAPTCHA on page 1).

## 2. Actions, in order, with dates

| When | Action | Who | Notes |
| --- | --- | --- | --- |
| 9 October | Pick the registration email (section 3.5.3) | Owner | Gmail is rejected by the form code and by the server |
| 9 October | Create a free Salesforce Developer Edition org (any email works), then start the Copado trial at app.copado.com/trial with "Connect with Salesforce" | Owner | Section 4.3. Whether the trial yields a CI/CD API key is not verified |
| 9 October | Give the CI/CD API key to the CLI: `agentia auth set --cicd <key> --region <region>` or set `AGENTIA_CICD_API_KEY`, then `agentia cicd health-check --json` | Owner or the build side | Section 4.1 |
| Same day as key | Feasibility probe for the alternative idea (environment create, credential create, pipeline connection create in the trial org) | Build side | Section 7.5 |
| Done 10 October | Idea locked (section 1) | Owner | |
| Done 10 October | Registered on developer.copado.com/hackathon with the text in section 7.10 | Owner | Same email must be used for submission |
| 12 to 23 October | Build (section 7.7) | Build side with owner | |
| 24 to 25 October | Demo video (5 minutes or less), deck, README, submit | Owner with the build side | Do not wait for 26 October in Central time |
| By 31 October 2026 | Red Hat nomination form, if the owner wants to enter | Owner | Section 8 |

## 3. The hackathon, complete

### 3.1 Identity

| Item | Value (verified) |
| --- | --- |
| Name | Agentia Headless Virtual Hackathon (page title "Agentia Headless Hackathon") |
| Organizer / sponsor | Copado, Inc., 200 E. Randolph St., Suite 6675, Chicago, IL 60601, USA |
| Site | https://developer.copado.com/hackathon (the page content is rendered by a JavaScript bundle; all text below was read from that bundle and from the Official Rules inside it) |
| Format | Fully virtual, individual participation only, no teams, no travel |
| Audience named by Copado | "developers, QA engineers and platform teams" who "build with Agentia Headless end to end, from the terminal to a released change" |
| Contact | hackathon@copado.com |
| Discussion group | Copado Success Community group "Agentia Headless (CLI, MCP, IDE)" (login required) |
| Page status on 9 October 2026 | "Registration open". The page code also contains an "Invite only" gate (sign in with a Copado Google account); it was not active. |

### 3.2 Timeline

| Phase | Dates (2026) | Copado's description |
| --- | --- | --- |
| Registration | 28 September to 12 October | "Sign up and set up your environment." |
| Build and submission | 12 October to 26 October | "Build your CLI workflow or plugin." Submissions are accepted only in this window. |
| Evaluation | 26 October to 3 November | "Submissions are reviewed and scored by the judging panel." |
| Announcement | 4 November | Winner, runners-up and top 10 announced by email, on the site, and on Copado's LinkedIn |

Time zone: the Official Rules say "The Sponsor's clock will be the official timekeeping device" and "All times are Central Standard Time (CST)". The exact closing hour is not published, so the safe plan is to register by the night of 11 October India time and submit by 25 October.

Extension clause: "if we receive an exceptionally high number of submissions, the evaluation period may be extended so every entry gets a fair review", and the announcement would move later, with notice by email and on the page.

### 3.3 Prizes

| Place | Prize (verified) |
| --- | --- |
| 1st | 1,000 US dollars plus winner certificate |
| 2nd and 3rd | 500 US dollars each plus runner-up certificate |
| 4th to 10th | Copado-branded laptop bag (rules: "premium laptop backpack"), shipped to your address, plus top-10 certificate |
| Everyone else with a valid entry | Participation certificate |

Taxes: all taxes on a prize are the winner's responsibility; prizes are not grossed up; the winner must return tax documentation in the time Copado sets or forfeit the prize (Official Rules, section 7).

### 3.4 Eligibility (Official Rules, section 2)

Open to individuals who are 18 or older (or the age of majority where they live), are legal residents of a country where participation is not prohibited, register during the registration period, and register with an active company or organizational email address. Quoted: "personal webmail and disposable email services are not accepted. If you are a student, please register with your university or college email address instead of a corporate email address." Each registered individual works independently.

Not eligible: employees and contractors of Copado, its affiliates, subsidiaries or investors; judges and companies employing judges; government employees or officials; residents of countries where participation is prohibited.

### 3.5 Registration

#### 3.5.1 Form fields (all required)

| Field | Limit or rule (verified from the form code) |
| --- | --- |
| Full name | Text |
| Company email | Must not be on the free-mail blocklist (3.5.3); must look like an email |
| Mobile number with country code | 10 digits for India (+91) and US/Canada (+1); 6 to 14 digits elsewhere |
| Job title | Text (placeholder "Salesforce Developer") |
| LinkedIn profile URL | Must match linkedin.com/... |
| Years of experience | One of: Fresher, 0-1, 1-3, 3-5, 5-8, 8-12, 12-15, 15-20, 20-25, 25+ years |
| Solution title | 200 characters |
| Problem statement | 2,000 characters ("The specific gap or problem you want to focus on") |
| Abstract / description of solution | 4,000 characters ("What do you plan to build?") |
| Problem solved | 4,000 characters ("How does your solution address the problem statement?") |
| Tools / technologies planned to use | 500 characters |
| I have read and accept the Official Rules | Checkbox, required |

After registering, Copado emails the key dates and a copy of your answers.

#### 3.5.2 Registration is not a lock

The submission form says: "Final version, update it if the solution changed since you registered" and "it can differ from your registration answer." So the idea can change between registration and submission. Only the email must stay the same: "Use the same work email you registered with, only registered participants can submit."

#### 3.5.3 The email problem and the options

The form rejects free-mail domains in the browser (list in the page code: gmail.com, googlemail.com, yahoo.com, yahoo.co.in, yahoo.co.uk, ymail.com, rocketmail.com, outlook.com, hotmail.com, hotmail.co.uk, live.com, msn.com, icloud.com, me.com, mac.com, aol.com, protonmail.com, proton.me, pm.me, gmx.com, gmx.de, mail.com, zoho.com, yandex.com, yandex.ru, rediffmail.com, qq.com, 163.com, 126.com, naver.com, hanmail.net, daum.net, mailinator.com, and more). The server also rejects: a database error containing "company_email" is mapped to the same message "Please use your company/organization email address." One specific address is whitelisted in the code, which shows that exceptions are granted case by case.

So chamanswami555@gmail.com cannot be used. Options:

1. A company or organization email the owner already has.
2. A university or college email (the rules name this option for students).
3. Write to hackathon@copado.com and ask for an exception as an independent developer.
4. An email on a personal domain. It passes the form check (only free-mail domains are blocked) but the rules say "company or organizational email", so ask Copado first.

#### 3.5.4 How the form works (detail)

The page is a single-page app. The form posts to a Supabase backend and then calls a "hackathon-sync" function (a Drive sync). Field lengths are cut on the client (title 200, problem 2,000, abstract 4,000, problem solved 4,000, tools 500). None of this changes what to write; it only explains why the browser rejects some inputs instantly.

### 3.6 The challenge

There is no fixed problem statement. Quoted: "Your challenge is to design and build an extension, integration, workflow, or other solution powered by Agentia CLI." The eleven directions Copado lists (any one or more):

1. Address an unmet user need or product gap.
2. Extend or improve an existing Agentia CLI capability.
3. Simplify setup, configuration, onboarding, command discovery, or troubleshooting.
4. Improve productivity, reliability, usability, or the overall developer experience.
5. Automate a repetitive or complex workflow, coordinate tasks across environments, or provide intelligent recommendations.
6. Connect Agentia CLI with development, collaboration, observability, or other internal or third-party tools.
7. Enable notifications, reporting, or event-driven workflows.
8. Strengthen quality, security, or governance through validation, policy checks, safeguards, auditability, or risk detection.
9. Create reusable templates or guided workflows that help teams apply standards consistently.
10. Introduce a new agent-powered experience or apply Agentia CLI in a new domain.
11. Combine existing capabilities in an unexpected way or prototype an idea that could inspire a future product capability.

Closing line from Copado: "demonstrate how their solution could create real value."

Sample ideas, "for inspiration only", from CopadoCon 2026 (no judging advantage for using them): Track A "The headless CLI" (build copado-hx, a unified terminal CLI wrapping the full Copado API surface); Track B "The agentic orchestrator" (extend Track A with SKILL.md so any AI agent can drive copado-hx); Track C "Your headless idea" (VS Code extension, Git hooks, Slack bot, Raycast extension, native MCP server, "if it eliminates the browser tab using the Copado API surface, it qualifies"); Track D "Data rollback with versioning".

FAQ facts (verified): anyone in the global community can take part except Copado employees; multiple submissions are allowed, one entry per problem statement; any location or time zone; install and extension guidance is at developer.copado.com/docs; a submission can be updated within the window by submitting again and emailing hackathon@copado.com so the panel takes the latest version; only organizers and judges see submissions, and judges never see name, email, phone or job title.

### 3.7 What to submit (Official Rules sections 3C and 4, and the submission form)

Three artefacts, all required:

1. A demo video of up to 5 minutes, uploaded as a file (not a link), 300 MB maximum, original work. "Functionality must match what is presented in the demo video submitted."
2. A presentation deck, uploaded as a file, 50 MB maximum.
3. A publicly accessible GitHub repository link containing the project source code.

Plus a short written description. All submission materials must be in English (or include an English translation). The entry must not violate anyone's IP, must contain no prohibited material (libelous, obscene, malicious code), no third-party confidential information, and every open-source component must be declared and licence-compliant.

Submission form fields: full name; email (same as registration); LinkedIn URL; submission title; problem statement ("judges read this first"); abstract; problem solved / gap addressed; tools used ("what you actually built with"); GitHub repository link; demo video file; presentation deck file; optional comments; accept the Official Rules. The form checks that the email is registered before it accepts anything.

### 3.8 Judging (Official Rules section 5, FAQ)

"A panel of Copado judges" scores blind. Five criteria, each 1 to 10, 50 points total; the top ten become the winners.

| Criterion | Copado's definition |
| --- | --- |
| Innovation | "Originality of the solution" |
| Impact | "Real business value" |
| Technical Execution | "Quality and completeness of the solution" |
| Use of Agentia Extensibility | "Use of Agentia's skills, commands, and MCP capabilities" |
| Presentation Quality | "Clarity of the solution and story based on demo and presentation deck" |

What this means for us: a strong entry uses commands, ships an Agent Skill, and touches MCP; it solves a real gap; it is complete and tested; and the 5-minute video tells the story on its own.

### 3.9 Rules that bite

| Clause | What it says (verified) | Why it matters |
| --- | --- | --- |
| IP (section 6) | Entrants keep ownership, but grant Copado an exclusive, worldwide, perpetual, irrevocable, royalty-free licence to use, reproduce, modify, publish, display and create derivative works from the submission (prototype, video, description), including commercialization | "Exclusive" means you cannot licence the same work to someone else. Decide whether that is acceptable before submitting. |
| Publicity (section 9) | Consent to use of name, likeness and demo materials for promotion, without payment | Normal for contests |
| Entry conditions (section 8) | Bound by rules and judges' decisions; release Copado from liability; submissions must be original and free of harmful code | |
| Liability (section 11) | Indemnify Copado for IP breaches; follow Copado's Acceptable Use Policy; Copado's total liability is capped at the grand prize value | |
| General (section 10) | Copado may cancel, suspend or modify the hackathon; may disqualify for rule violations or unsportsmanlike conduct; decisions final | |
| Governing law (section 12) | Illinois law; courts of Cook County, Illinois | |
| Personal information (section 13) | Used to run the hackathon, promote future events, and market Copado products, per Copado's privacy policy | |
| Multiple entries (section 3A) | "Entrants may submit multiple unique solutions" | One excellent entry beats two average ones for a solo builder |

### 3.10 Corrections to the earlier research notes

| The earlier notes said | What the official sources say |
| --- | --- |
| Dates as above | Correct. Times are CST. Evaluation can be extended. |
| Prizes as above | Correct, plus certificates for all valid entries |
| "Invite-only" confusion | Resolved; registration open |
| Submit repo + README + 5-minute video, English | Incomplete: a slide deck is also required; the video is a file upload (300 MB max); deck 50 MB max; functionality must match the video |
| "Copado hasn't published a scoring rubric" | Wrong: five criteria, 1 to 10 each, 50 points, blind judging |
| Company email required | Incomplete: personal webmail explicitly rejected; students may use a university email; 18+; Copado staff, judges and government employees excluded |
| 239 CLI commands | The docs page says 246; the installed 1.0.0-beta.4 manifest has 234 (numbers move with releases) |
| Akshara Thakur, Fleet Radar, Slacktia | Real: Copado blog of 29 September 2026 |
| Multiple submissions allowed | Correct; resubmission within the window allowed |
| No PPO (job offer) promised | Correct; nothing in the rules. The earlier notes did not mention the exclusive IP licence, the publicity clause, or the tax clause. |
| "CopadoCon Jaipur 2025 hackathon", "94K LinkedIn followers" | Not verified by us |
| Recommended ideas (Release Doctor, PR agent, risk score, Slack bot) | Already built by others or crowded (section 6) |

## 4. Access to Copado and the CLI

### 4.1 How the CLI authenticates (verified from the CLI itself)

| Credential | What it is | How to set |
| --- | --- | --- |
| Copado API key (CICD) | Key for the Copado CI/CD gateway; needed by every `cicd` command and most MCP tools | `agentia auth set --cicd <api-key> --region na` (or `--custom-url <url>`), or environment variable `AGENTIA_CICD_API_KEY` (plus `AGENTIA_CICD_BASE_URL` in some flows) |
| Copado AI PAT | Personal access token for Copado AI agents; needed by `ai` commands | `agentia auth set --ai <pat> --ai-domain robotic.copado.com --ai-org <org-id>`; the PAT comes from the Copado AI web app (Profile, PAT key) |
| CRT PAK | Personal access key for Copado Robotic Testing; needed by `testing` commands | `agentia auth set --crt <pak> --crt-domain <domain> --crt-org <org-id>`; readiness is reported by `agentia auth get --crt --json` (`ready: true`) |

Credentials are stored in the macOS keychain. Project settings live in `.agentia/config.json` (project) and `.agentia/config.user.json` (user) in the current folder. Without a key, `agentia cicd work list --json` returns a clean JSON error: "CICD API key is not configured. Run `agentia auth set --cicd <key> [--region <region> | --custom-url <url>]` or set AGENTIA_CICD_API_KEY."

`agentia setup` is interactive only. Its first prompt is "Configure global CICD authentication for all projects? (Y/n)". With input closed it exits (we tested this).

### 4.2 The contradiction in Copado's own pages

| Source | Statement (verified) |
| --- | --- |
| developer.copado.com/docs, Prerequisites | "An active Copado license (CI/CD, Testing, or AI Context Hub)", "Your Copado product configured and ready to use", "No license? Open a playground in the Success Community", "Or request an Agentia Testing / AI trial on copado.com" |
| developer.copado.com home | "Free for individual developers" |
| developer.copado.com/support FAQ | "Is Agentia free for individual developers? Yes. The full Plan, Build, Test, Release, and Operate agents are free for individual use in VS Code and Cursor." and "Do I need an existing Copado account? No. Agentia auto-provisions a workspace on first launch. If you do have a Copado org, run `agentia auth set` to link it." |
| The CLI as installed | Asks for a CICD API key first; no auto-provisioning step appeared |

Reading: the "free for individuals" wording is about the IDE agents; the CLI's CI/CD commands need a Copado org with a key. Which is true today for a brand-new user is not verified; only trying it answers it.

### 4.3 The trial path (verified page content, outcome not verified)

- copado.com/agentia: "Agentia Advanced" has a "14-day free trial, no credit card"; "Agentia Pro" is contact sales. Trial link login.copado.com/trial redirects to app.copado.com/trial.
- app.copado.com/trial (rendered in a browser): "Welcome to Agentia. Start your 14 Day trial by connecting with Salesforce." One button: "Connect with Salesforce". By clicking you accept the "Copado AI Platform Trial Agreement". There is no email form, so the free-mail problem does not apply here.
- The support FAQ lists supported Salesforce editions: "Enterprise, Unlimited, Developer, and Partner Developer editions. Sandboxes and scratch orgs work out of the box." A free Salesforce Developer Edition org (developer.salesforce.com/signup, any email) should therefore be accepted. Not verified.
- Evidence that trial orgs can have pipelines: a Copado employee's public repos (joecopado/sdo-agentia-pipeline and sdo-agentia-crt-tests) describe a "copado-trial" org with a dev1 + dev2 -> qa -> prod pipeline and CRT tests. This is an inference from repo descriptions, not a verified fact about our trial.
- Not verified: whether the trial gives a CI/CD API key, pipelines, Robotic Testing, and Copado AI; whether 14 days is enough (build window is 14 days: start the trial on or just before 12 October).
- Observed on 11 October 2026 (owner's trial, started 11 October, 14 days): the trial opens "Agentia Pipeline" at us.pipeline.copado.com (Work Manager, Deployments, History, Automations, Back Deployments, Connections, Pipelines, Projects, AI Context Hub, Jira and Slack integrations). The onboarding asks for a Git repository, at least two Salesforce orgs and a pipeline. No API key page exists there or on app.copado.com. The CLI's own setup prompt says: "Create a Copado API key on the API Key tab of the Account Summary page" and links to the Salesforce tab copado__Account_Summary; that tab does not exist in the owner's Developer Edition org, so the trial did not install the Copado managed package. Result: the CI/CD key source is blocked until Copado answers (hackathon@copado.com asked on 11 October). The owner's Developer Edition org App Launcher confirmed no Copado app (11 October). AppExchange listing "Agentia by Copado AI-Powered Salesforce AgentOps" (Paid, managed package v27.41.0, listing a0N3000000B3dgGEAR): "Get It Now" opens a provider-assisted installation form; after submitting it the page said Copado will contact the owner (11 October). Copado Essentials (free, formerly ClickDeploy) is a different product and does not feed the CLI. Open channels to Copado: hackathon@copado.com email, the AppExchange request, and the Success Community group. CLI updated to 1.0.0-beta.5 on 11 October; its changelog adds nothing about trial authentication; `auth set` regions are na, emea, emea2, apac, apac2, plus `--custom-url`.

### 4.4 Other access paths

- Success Community "playground" (docs wording). Login required; not inspected.
- Request an "Agentia Testing / AI trial" on copado.com (docs wording).
- Ask hackathon@copado.com how participants without a licence are expected to get access.

### 4.5 Steps

1. Owner: create a Salesforce Developer Edition org.
2. Owner: app.copado.com/trial, "Connect with Salesforce", log in with that org, accept the trial agreement.
3. Owner: find the CI/CD API key in Copado (location not verified yet) and run `agentia auth set --cicd <key> --region <region>`; or hand the key to the build side.
4. Build side: `agentia auth get --json`, `agentia cicd health-check --json`, `agentia cicd environment list --json`, `agentia cicd pipeline list --json`. If these answer, access is real.
5. Build side: record real JSON outputs as fixtures (secrets scrubbed) for offline tests.

## 5. Agentia Headless explained

### 5.1 What it is

Copado is a company that sells DevOps tools for Salesforce (section 10 explains Salesforce and DevOps). Agentia is Copado's AI-era product line: AI agents named Plan, Build, Test, Release, Operate and Knowledge. Agentia Headless is the part you use without a browser: a command-line tool (CLI), a local MCP server, Agent Skills, and companion IDE extensions. Copado's own words: "The CLI performs the operation, MCP exposes it as a tool, and the skill tells the agent which operation to choose and in which order."

Status: "Product Preview, Alpha. Commands, flags and behavior may change without notice." Press release of 14 September 2026: early access now; "available directly through Copado and its global partner network starting November 2026". The hackathon runs during this beta.

IDE extensions: VS Code (Marketplace item Copado.agentia-idex) and Cursor via Open VSX (copado/agentia-idex); the site also advertises support for AI coding assistants.

### 5.2 The four pieces and why each matters for judging

| Piece | What it is | How you use it | Why it matters |
| --- | --- | --- | --- |
| CLI (`agentia`) | 234 commands in the installed version; every command has `--json` | `agentia <topic> <command> --json` from a terminal or a script | "Commands" in the judging criterion |
| MCP server (`agentia mcp start`) | 194 tools over stdio that mirror the commands, so an AI coding agent (for example Cursor) can call Copado directly | Configure the agent with `{"command": "agentia", "args": ["mcp", "start"]}` | "MCP" in the judging criterion |
| Agent Skills | Markdown playbooks (`SKILL.md` plus reference files) that teach a coding agent the right command order and guardrails | `agentia setup skills create --target <target>` | "Skills" in the judging criterion |
| Plugins | Extra commands added to the CLI with the official generator and SDK | `npm init @copado/agentia-plugin my-plugin`, build, `agentia plugins link .` | The hackathon's "extension" path |

### 5.3 The CLI in detail (verified from the installed 1.0.0-beta.4)

Topics and counts: cicd 143, testing 73, ai 9, auth 3, setup 3, mcp 1, runtime 1, update 1 (total 234). Docs page claims 246 (General 30, CI/CD 132, Testing 75, AI 9); versions differ.

Every JSON response has the shape `{"result": ..., "status": 0, "transactionId": "..."}` or `{"error": {"message": ..., "name": ...}, "transactionId": "..."}`.

Main workflows, as the shipped skills describe them:

- Local repository flow (one user story per feature branch): `work list` -> `work get` -> `work set` (creates or checks out `feature/<story-name>`) -> code and `git commit` -> `work test` (local quality gates script `.agentia_quality_gates.sh`) -> `work publish` (registers commits with Copado, merges into the dev org branch) -> `work submit` (validation; `--done` or `--deploy` promotes) -> `work status`.
- Cloud flow: `cloud commit <story-id> --metadata-category SFDX ...` (Copado retrieves metadata itself), then `cloud promote <story-id> [--deploy]`. Local and cloud flows must never be mixed on one story.
- Promotions: `promotion list/get/run --operation merge|merge_and_deploy --wait`, `--resume <job-execution-id>` after a conflict; conflicts via `promotion conflict list/get/resolve --mode auto|manual --file/unresolve`.
- Jobs (Copado job executions): `job list --status "In Progress" --mine`, `job get`, `job log get --step`, `job run/resume/pause/kill`, `job result-file list/get`.
- Environments, credentials, pipelines: `environment create NAME --type "Production/Developer|Sandbox|Scratch Org|Custom Domain" --platform SFDX`, `environment auth web login` (browser OAuth, CLI only), `credential create --environmentid --name --default`, `pipeline create NAME --platform SFDX --main-branch main --git-repository-id ... --enable-smart-conflict-resolution`, `pipeline connection create --pipeline-id --source-environment-id --destination-environment-id --branch`, `stage create`, `pipeline stage-connection create`.
- Back-promotion and sync: `work environment-sync` (creates a back-promotion for every story behind the destination environment; warns about stories behind that may cause conflicts).
- Metadata: `metadata list`, `metadata content get/compare`, `metadata index compare --comparison-mode BRANCH_COMPARE|INDEX_FILE|MIX`, `metadata dependency list`, `metadata refresh run/status/deleted`.
- Data (release data templates): template list/get/get-detail/create/save-detail/convert-old/delete, records search/match, filters, formulas, sobject fields/relationships, sync preview-updates/apply, data commit create/list, dataset-file list/content.
- Notifications: `notification configure --pipeline-id --event <Promotion_Failed|Deploy_Failed|Quality_Gate_Failed|Test_Failed|...> --destination-type user|channel --destination-id --subscription user|all` (Slack).
- Functions (Copado Functions): list/get/defaults/upsert/run/run-local (Docker)/result get/result log get.
- Governance: `health-check [--git-sizer --path]`.
- Testing (Copado Robotic Testing): projects, robots, jobs (file upload or Git-backed), `test run --wait-for-result`, builds (list/get/latest/search/logs/abort), schedules, data tables, variables, user parameters, live sessions (start/execute/inspect/screenshot/stop).
- AI: `ai agent ask --agent plan|build|test|release|operate|knowledge -p "..." [--user-story --sf-org --component --workspace --dialogue] --json`, `ai agent chat` (interactive only), `ai quota get`, `ai workspace list/get/create/update/member list/invite`.
- Setup: `setup` (interactive), `setup skills create|update --cicd --testing --ai --target <target> --no-prompt`, `cicd project default set/get/unset` (project defaults so you do not repeat IDs), `update`, `runtime` (NDJSON process used by the IDE).

Help quirk: `agentia cicd work list --help` prints "Command cicd work list not found"; use `agentia help cicd:work:list` instead.

### 5.4 The MCP server (verified by starting it)

`agentia mcp start` answered `initialize` with server `@copado/agentia-cli 1.0.0-beta.4` and listed 194 tools, all named `agentia_*`, without any credentials (the tools need credentials when called). Categories: AI (`agentia_ai_ask`), auth, credential, data (24), environment, function, governance (`agentia_health_check`), job, pipeline and stage, project and project defaults, repository, promotion (including conflicts), user, navigation, work (20, including `agentia_work_set`, `agentia_work_publish`, `agentia_work_submit`, `agentia_work_test`), cloud (`agentia_cloud_commit`, `agentia_cloud_promote`), metadata, testing (30 plus live tools). Every tool carries MCP annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) so clients can auto-approve safe reads. Browser login and CRT live view/recorder are CLI only. Client configuration for MCP clients is in the CLI README (section 11 lists where we read it).

### 5.5 Agent Skills (verified from the shipped templates)

`agentia setup skills create` writes `AGENTS.md` and three skills into the project: `agentia-cicd` (SKILL.md plus references work.md, promotions.md, jobs.md, environments-and-credentials.md, pipelines.md, data.md), `agentia-testing` (tests.md), `agentia-ai` (ai-agents.md). AGENTS.md states the workflow "list -> get -> set -> (implement and git commit) -> test -> publish -> submit [--done|--deploy]" and rules such as "Do not skip `work set` before coding; use one story per feature branch", "Never print credentials", "Read records before changing them". The skills are "managed": refresh with `agentia setup skills update`, do not hand-edit.

### 5.6 Plugins: what they can and cannot do (verified from docs and changelog)

- Scaffold: `npm init @copado/agentia-plugin my-plugin` (package @copado/create-agentia-plugin 0.3.0, MIT). It creates an oclif plugin in TypeScript: `src/commands/<topic>/<command>.ts`, `package.json` with an `agentia` block (`hostApi: 1`, `requires: [...]`, `permissions: {network: [], files: "none", commands: [], env: []}`, `hooks: []`).
- SDK: @copado/agentia-plugin-sdk 0.1.0 (published 7 October 2026). `AgentiaCommand` gives `--json` and spinners; `getAgentiaHost({requires})` exposes a curated host: `work.getWorkItem`, `organization.healthCheck`, `auth.status`, `format.table`. "Results are allowlisted and redacted" and "plugins never receive credentials."
- Develop: `npm run build`, `agentia plugins link .`, run `agentia <topic> <command>`. Publish: `npm publish --provenance`. Marketplace submission: "coming soon".
- Supported today: add new commands; oclif flags and args; read a user story; run the org health check; check which integrations are set up; print tables and return JSON; link or install like any oclif plugin.
- Not supported: importing the CLI or its internals or calling Copado endpoints directly; receiving API keys or credentials; extending or wrapping existing Agentia commands; registering MCP tools through a plugin (`agentia mcp start` loads only built-in tools).
- Accepted practice in the visible entries: a plugin command spawns the public `agentia ... --json` commands as child processes and parses the JSON. Copado's "not supported" list does not forbid this.

### 5.7 Known limitations that affect idea choice (from the docs page)

- `cicd work test --cloud` (remote Copado quality gates): "not implemented yet".
- Local development needs a fully configured user story (credential, project, pipeline, environment).
- Local and cloud flows cannot be mixed on one story.
- Data deployments: no data-specific rollback, retry, resume, validation-only or status commands; template detail updates replace the whole document; no offline mode.
- CRT: credentials are separate (PAK, domain, org id); `--stream-logs`/`--watch` cannot combine with `--json`; data-table runs cannot combine with wait/artifacts/xUnit; some live operations are CLI only; destructive operations need `--yes` (MCP: `confirm: true`).
- Profiles can be very large; reports and dashboards can have folder dependency issues; Experience Cloud partially supported; Salesforce Industries, Omnistudio and Vlocity not supported in local development; only the tip commit is registered on `work push`; find-and-replace adds a commit.
- Local quality gates need a Copado admin to create an "Extension Configuration" named Local Quality Gate (phase Test, tool None, type Unit Test).

### 5.8 Release velocity (from the shipped CHANGELOG)

1.0.0-beta.0 on 23 September 2026 (alpha to beta), beta.1 on 29 September, beta.2 on 2 October (adds `cicd work promote`, `environment-sync`, health checks, MCP annotations), beta.3 on 6 October (repository auth flows, auto-resolve by taking the feature branch during environment-sync), beta.4 on 7 October (adds `agentia runtime` and the plugin host plus SDK). Earlier alphas go back to at least mid-September. Expect changes during the build window; pin the CLI version in our tests.

### 5.9 Licence (EULA shipped as LICENSE.md), in plain words

The CLI is not open source. It is licensed "only for your internal business purposes in connection with your authorized use of Copado's products or services". You may not copy or distribute it, modify it, reverse engineer or decompile it, use it to build a competing product, publish benchmarks without consent, or circumvent licence keys. Copado owns any derivative works of the software. For us: build on the documented commands, the plugin SDK and the public JSON output; do not read or ship the CLI's compiled code; declare every open-source component we use (the hackathon rules require that too).

### 5.10 What is installed on this Mac (verified)

Node v26.6.0, npm 11.18.0, npm prefix /opt/homebrew (writable, no sudo). `npm install -g @copado/agentia-cli@beta` added 366 packages in 22 seconds, exit code 0, with deprecation warnings (rimraf, fstream, inflight, lodash.isequal, glob, uuid) and an allow-scripts notice about yarn's preinstall script. `agentia --version` prints `@copado/agentia-cli/1.0.0-beta.4 darwin-arm64 node-v26.6.0`. Package folder: /opt/homebrew/lib/node_modules/@copado/agentia-cli (CHANGELOG.md, LICENSE.md, README.md, bin, dist, node_modules, oclif.manifest.json, package.json, templates, theme.json, vendor). npm registry: @copado/agentia-cli dist-tags latest 1.0.0-beta.0, beta 1.0.0-beta.4 (package created 28 July 2026, modified 7 October 2026; homepage github.com/Copado/agentia-cli returns 404, so the source is private). Nothing else was installed. Nothing was written outside the project folder except throwaway files in a temporary folder.

## 6. Competition map (GitHub, searched 9 October 2026)

About 30 public repositories already mention Agentia; most were pushed between 30 September and 8 October 2026 and several say they are for this hackathon. The build window has not opened, so early movers are building now.

| Repository | Pushed | What it does (from README or description) |
| --- | --- | --- |
| gitanjalivanshiv/agentia-timemachine | 5 Oct | Version control for Release Data Templates: snapshot, diff, safe concurrent edit, verified restore, lint; Agent Skill and MCP server; 220+ unit tests against a "stateful fake org"; 2-minute offline demo; GitHub Actions; HTML report |
| gitanjalivanshiv/agentia-mutant | 6 Oct | Mutation testing for Salesforce configuration through Copado (plan, run, report, heal with Copado AI); Agent Skill; scrubbed recordings for a one-minute demo; Node 22, TypeScript, Vitest |
| shreyanshgoy/Agentia-Sentinel | | Governance for AI agents: policy, approvals, hash-chained audit; MCP proxy that normalizes 192 Agentia tools; editor hooks; 13 tests; demo without an org |
| sVaidikk/shipguard-agentia | 6 Oct | Policy gate (PASS/WARN/BLOCK) for AI-driven releases; Agent Skill; MCP server with 3 tools; 21 tests; zero dependencies; CI |
| KarthikKKulkarni/agentia-release-guardian | 2 Oct | Pre-deployment risk scoring 0-100, blast radius, test recommendation, policy as code; 39 tests; CI; no skill or MCP mentioned |
| vamshikrish97/agentia-salesforce-release-intelligence | 7 Oct | AI release risk analysis and test recommendation (README not readable by our tools) |
| devkdas/agentia-org-graph | 3 Oct | Blast radius from metadata dependencies (Mermaid or JSON); live demo only |
| devkdas/agentia-env-drift | 3 Oct | Metadata drift between environments with AI explanation; live demo only |
| devkdas/agentia-data-vault | 1 Oct | Snapshot, diff, gated restore for data deployments; approval codes |
| devkdas/agentia-rollback-dryrun | 1 Oct | Destructive-change preview files for metadata undo plans |
| devkdas/agentia-gov-guard | 1 Oct | Pre-promotion policy checks, PROD approval gates, audit reports |
| devkdas/agentia-release-audit | 1 Oct | Compliance audit reports aggregating stories, promotions, test evidence |
| devkdas/agentia-fls-guard, agentia-profile-trim | 3 Oct | Field-level-security scanner; noise-free Profile diffs |
| devkdas/agentia-auto-poll | 1 Oct | Headless CRT data-table runs with polling, reports, notifications |
| devkdas/agentia-doctor-dx | 1 Oct | Setup, auth and skills health check |
| devkdas/agentia-skills-pack | 1 Oct | Ten Agent Skills plus templates and guardrails, built on four companion plugins |
| devkdas/agentia-promote-path | 30 Sep | Guided promotions with narrated receipts |
| devkdas/agentia-fleet-radar | 3 Oct | Multi-org failure correlation (same concept as the Copado blog's Fleet Radar) |
| mcshipdev-design/mc-ship | 5 Oct | Marketing Cloud releases on Agentia CLI; Agent Skill; MCP server with 6 tools; mock fixtures plus live smoke tests; CI |
| ShibPrakash/COPADO-NEXUS | 3 Jun | MCP server over Copado AI agents (CopadoCon 2026 era) |
| joecopado/sdo-agentia-pipeline, sdo-agentia-crt-tests | 6 Oct | Copado employee demo repos: trial org with dev1+dev2 -> qa -> prod pipeline, CRT tests, AGENTS.md |
| Others | | gmeekscopado/Agentia_Advanced_SF (demo), jaideep86/AgentiaPipeline (SFDX template), netter233/copado-agentia-pipeline, harishkommula7/CopadoAgentia, Kumar-s-v/Copado-Agentia-Learning, parthraghu/CopadoAgentiaRepo, Techn0-M0nk/Agentia_Copado_Trail (certification practice), Ansar2578/Agentia-Copado |

Copado blog, 29 September 2026: Akshara Thakur, 17, built Fleet Radar (monitors many Copado orgs, correlates failures, Slack alerts, AI fix suggestions from the Plan agent) and Slacktia (Agentia Headless CLI on a server behind a Slack app; plain-English slash commands create Copado user stories).

Taken spaces: governance, policy gates, approvals, audit (at least 5 entries); data snapshot and rollback (3); risk, blast radius, dependencies (3); environment drift; fleet monitoring; setup doctor; profile and FLS tools; CRT polling; skills packs and templates; promotion guidance; mutation testing; Marketing Cloud; MCP proxy over Copado AI agents.

Quality bar set by the best entries: hundreds of unit tests against recorded fixtures, a one-command offline demo, live verification in a real org, CI, architecture and decision docs, both an Agent Skill and an MCP server, honest limitation statements, MIT licence.

## 7. Idea research

### 7.1 Method

Read the official challenge and rubric; read Copado's own product docs, known limitations and changelog (gaps Copado admits); installed the CLI and listed every command and MCP tool; read the shipped skills (the exact workflows Copado wants agents to follow); searched GitHub for every Agentia-related repository and read the strongest READMEs; checked Ansible Galaxy and GitHub for existing Copado automation; checked Copado's own conflict-resolution features; matched everything against the owner's stack (TypeScript, Node, Python, Flutter) and a two-week solo build.

### 7.2 Ideas rejected and why

| Idea | Why not |
| --- | --- |
| Release Doctor (root-cause analysis of failed deployments), PR risk agent, risk score, Slack bot (earlier suggestions) | Already built or crowded: release-guardian, release-intelligence, shipguard, gov-guard, Slacktia |
| Element-level merge-conflict resolver for Salesforce metadata | Copado already ships it. Docs article "Merge Conflict Resolution Overview and Types" (updated 6 August 2026), read in full: Auto-Resolve (if the conflicted file was committed on the user story, the feature branch wins, otherwise the promotion branch wins); Semantic Merge for Nested Metadata (the same rule applied per element with de-duplication, for profiles, permission sets, labels, translations, sharing rules, workflow, escalation, duplicate and matching rules; Copado recommends not resolving nested metadata manually); Online Conflict Resolution (manual); Exclude From Auto Resolve; Smart Conflict Resolution (a manual resolution is fingerprinted and re-applied next time; enabled by default). Limit: a conflicting file up to 50 MB. Promotions can resume from the conflicting story (Source Format Pipelines v9.8 and later). The pipeline create command even has `--enable-smart-conflict-resolution`. |
| Data rollback, drift detection, blast radius, governance gates | Taken (section 6) |
| Terminal release board (k9s-style) | Not taken, but judges would read it as a UI over the CLI; weak on skills and MCP |
| Plugin test kit (record and replay) | Useful ecosystem tool, weaker business impact; we will build the recording harness anyway for our own tests |
| Fake local Copado gateway for licence-free development | Legal grey zone under the EULA (reverse engineering, circumventing); dropped |
| Mobile approvals app | New surface, but uses commands only; weak on the extensibility criterion |

### 7.3 Shortlist with estimated scores (our estimate against the official 50-point rubric; not a prediction)

| Idea | Innovation | Impact | Technical | Extensibility | Presentation | Total | Main risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ansible collection plus Event-Driven Ansible for Agentia CLI | 9 | 8 | 8 | 8 | 8 | 41 | Judges may see it as infrastructure tooling rather than developer tooling |
| Ephemeral environment per user story | 8 | 9 | 7 | 9 | 8 | 41 | Setup is heavy (Dev Hub, trial pipeline); Copado docs mention a Scratch Org Wizard and "DX Scratch Org Operations", so part of this may already exist in the product (currency not verified) |
| Acceptance criteria to Robot Framework tests run on CRT | 8 | 8 | 7 | 8 | 8 | 39 | CRT may not be in the trial (not verified) |
| Terminal release board | 6 | 7 | 8 | 6 | 10 | 37 | "UI over CLI" |

### 7.4 Recommended idea, in plain words

Name: not decided (owner's pick). Candidates in plain English: "Agentia Ansible", "Release Conductor", "Copado Playbooks".

The problem. Big companies run release nights that touch many systems at once: Salesforce, databases, integration servers, websites. Salesforce releases run inside Copado. Everything else is usually run by Ansible Automation Platform (Red Hat's enterprise automation product). Today nobody has connected the two: Ansible Galaxy has zero Copado collections and GitHub has zero Copado-Ansible repositories (checked 9 October 2026). Release managers switch tools, re-type steps, and keep evidence in several places. When a Copado job fails, nothing outside Copado reacts.

The solution. One installable Ansible collection whose modules wrap Agentia CLI commands, plus an Event-Driven Ansible source that turns Copado job and promotion status changes into events, plus example playbooks and a rulebook, plus an Agent Skill, plus a small Agentia plugin command.

What is in the box (scope, fixed):

1. Collection modules (Python, each calling `agentia ... --json`, each idempotent, with check mode and diff where meaningful): work item create/update/get, work submit (validate or done), promotion run with wait and resume, job get/wait/log, CRT build run with polling and result, metadata compare, health check, Copado AI agent ask.
2. Event-Driven Ansible source plugin: polls `agentia cicd job list --json` and promotion lists, emits events on status transitions (for example Promotion_Failed, Deploy_Success, Quality_Gate_Failed).
3. Rulebook: on job failed, run a remediation playbook (resume the job, notify, open a ticket); on success, continue the release.
4. Playbooks: release window with an approval pause and evidence collection; nightly validation (validate-only promotions plus CRT smoke tests).
5. Agent Skill (`SKILL.md`): teaches a coding agent how to author and run these playbooks from a pipeline's current state, using Agentia MCP tools to read state.
6. Agentia plugin command (oclif, TypeScript): `agentia ansible scaffold` writes a playbook from the current pipeline and promotable stories; `agentia ansible run` wraps execution.
7. A small MCP server exposing "run release playbook" and "release status" tools, so an AI agent triggers releases through governed playbooks rather than raw commands.
8. Tests: recorded JSON fixtures from real commands (secrets scrubbed) replayed through a fake `agentia` executable; ansible-test sanity and units; GitHub Actions CI; offline demo script; live demo in the trial org.
9. Docs: README (install, 5-minute quickstart, module reference), architecture, decisions, limitations; published to Ansible Galaxy with provenance on npm for the plugin.

How it uses Agentia: commands (deeply), skills (one shipped), MCP (consumed by the agent in the demo, and one of our own). Challenge directions hit: 5 (coordinate tasks across environments), 6 (third-party tools), 7 (event-driven workflows), 10 (new domain).

Why judges should score it: nobody has it (innovation); it reaches enterprise platform teams, which Copado names as an audience (impact); the Agentia pieces are used as designed (extensibility); it can be shown end to end in a terminal in five minutes (presentation).

Risks: judges' taste (see 7.3); Event-Driven Ansible needs Java 17 and Python on the build machine; the trial must give a working CI/CD key and at least one pipeline for the live part; scope creep (hold the list above).

### 7.5 Alternative idea: ephemeral environment per user story

One command creates a fresh Salesforce scratch org for a user story, registers it in Copado (`environment create --type "Scratch Org"`, `credential create`, `pipeline connection create`), sets the story's source environment, deploys the branch, runs tests; one command tears it down when the story is done. Like "preview environments" in web development, for Salesforce. Higher ceiling on impact and extensibility; higher execution risk. Feasibility probe (one day, needs the trial key): confirm that environment create, credential create and pipeline connection create succeed in the trial org and that a Developer Edition org can be a Dev Hub. Also check how current Copado's Scratch Org Wizard is, to avoid duplicating a product feature.

### 7.6 Lock rule

Within one day of a working CI/CD key: run the probe in 7.5. If it passes cleanly, the owner picks between 7.4 and 7.5. If it fails or the key is not available by 11 October 2026, lock 7.4 on 11 October.

### 7.7 Two-week plan

| Dates (October 2026) | Work | Output |
| --- | --- | --- |
| 9 to 11 | Email decision, registration, trial, API key, access probe, fixtures recorded, repository skeleton, CI | Registered; `agentia cicd health-check` passes; fixtures folder |
| 12 to 16 | Collection modules with replay tests; ansible-test sanity | Modules pass offline and against the trial org |
| 17 to 20 | Event-Driven Ansible source and rulebook; release-window and nightly playbooks; Agent Skill | Rulebook reacts to a real failed job in the trial org |
| 21 to 23 | Plugin command, our MCP server, docs, Galaxy publish | `agentia ansible scaffold` works; collection installable from Galaxy |
| 24 to 25 | Video (5 minutes or less, under 300 MB), deck (under 50 MB), README polish, submission | Submitted by 25 October, India time |

### 7.8 Demo plan (5-minute video)

0:00-0:30 the problem (two tools, one release night); 0:30-1:30 one playbook run: story validated, promotion run with wait, CRT smoke test, Slack notification, evidence file written; 1:30-2:30 a failure injected on purpose, the rulebook catches the Copado event and resumes the job, then the release continues; 2:30-3:30 an AI coding agent reads the pipeline through Agentia MCP and writes a new playbook using our skill, then `agentia ansible run` executes it; 3:30-4:30 how it is built (modules, fixtures, tests, Galaxy); 4:30-5:00 what this means for a platform team and what is next.

Deck outline (under 50 MB): problem, who has it, the solution in one picture, demo screenshots, what uses Agentia (commands, skill, MCP), architecture, tests and quality, limitations and roadmap, links.

### 7.9 Definition of done

Working prototype that matches the video; public GitHub repository with README in English; tests that fail without the code they protect; offline demo script; live run in the trial org recorded; CI green; no secrets in the repository; every open-source dependency declared with its licence; video 5 minutes or less and 300 MB or less; deck 50 MB or less; submission form fields written in English and final.

### 7.10 Registration text draft (English, for the form; only if the owner picks 7.4; the title is a placeholder)

Solution title: Ansible Collection and Event-Driven Automation for Copado Agentia CLI

Problem statement: Enterprise release windows span Salesforce and non-Salesforce systems, but Salesforce releases run in Copado while the rest of the estate is orchestrated in Ansible Automation Platform. Release managers switch between tools, re-key steps by hand, and keep release evidence in several places. Failed Copado jobs are noticed late because nothing outside Copado reacts to them.

Abstract: An Ansible collection that wraps Agentia CLI commands as idempotent modules (user stories, submit and validate, promotions with wait and resume, job logs, Copado Robotic Testing runs, metadata compare, health checks, Copado AI agent prompts), an Event-Driven Ansible source plugin that turns Copado job and promotion status changes into events, example playbooks for an approved release window and nightly validation, a rulebook that auto-remediates or escalates failed jobs, an Agent Skill so coding agents can author release playbooks, and an Agentia plugin command that scaffolds a playbook from the current pipeline state.

Problem solved: Salesforce releases become one step in an enterprise-wide, auditable Ansible playbook with approvals, retries and evidence collection, instead of a separate manual process. Copado events trigger automation in the rest of the estate within seconds. Teams that already run Ansible get Copado without learning a new tool, and AI agents trigger releases through governed playbooks rather than raw commands.

Tools / technologies planned to use: Agentia Headless CLI (cicd, testing, ai commands with --json), Agentia Agent Skills, Agentia plugin SDK (oclif, TypeScript), Ansible collection (Python modules), Event-Driven Ansible (ansible-rulebook), Salesforce CLI, GitHub Actions, replay fixtures for offline tests.

## 8. Red Hat Certified Professional of the Year 2027

Facts (verified from redhat.com/en/services/certification/rhcp/rhcp-of-the-year and its Official Rules page):

| Item | Value |
| --- | --- |
| What | A yearly award for "current Red Hat Certified Professionals who demonstrate ingenuity, hard work, and expertise". Not a hackathon. |
| Window | 1 September 2026, 12:01 a.m. EDT to 31 October 2026, 11:59 p.m. EDT. The page's "nomination period is closed" sentence is a commented-out template for after the deadline; the live page shows a countdown and a "Submit a nomination" button. |
| Eligibility | Hold a current Red Hat certification before 1 September 2026 and still during Red Hat Summit (25 to 27 May 2027); legal resident of a listed country (India is listed); above the age of majority. Not eligible: Red Hat employees and contractors and their households, government officials and employees, employees of state-owned enterprises. |
| How to enter | Online form at feedback.redhat.com (Qualtrics; page 1 is an eligibility check with a reCAPTCHA, so it cannot be automated). Self-nomination is allowed; a third party can nominate, and the nominee then accepts by email. One nomination per nominee. |
| What the form needs | Name, email, employer, department, manager's name and email, job title, job role, Red Hat certification ID, city/state/zip/country, phone, date of birth, certifications held, whether the nominee's employer is a Red Hat customer or a partner, and open-ended answers "explaining why the Nominee should receive the award". |
| Judging | Round 1 (2 to 10 November 2026): experts rate "how well a Submission articulates the extent to which that Nominee's RHCP certification allowed him/her to succeed, including quantifiable metrics and outcomes", with special consideration for certification level, customer or partner story, Red Hat products used, services used, project-based results and metrics, and open source community outreach. Round 2 (12 November to 4 December): the top five are interviewed by Red Hatters. Winner notified about 11 December 2026. |
| Prize | Red Hat Summit 2027 pass, airfare, four hotel nights, a one-year Red Hat Learning Subscription (Premium), trophy; approximate value 15,000 US dollars; plus a video spotlight, press release mention, badge. |
| Licence | Non-exclusive licence to Red Hat to use the submission; name may be published. |
| Recent winners | 2026 Firas Benbelgacem, Orange, 17 Red Hat certifications including two Red Hat Certified Architect levels; 2025 Daniel Carvalho dos Santos, Banco Bradesco; 2024 Gang Cheng, Sopra Steria, large-scale patching with Ansible Automation Platform; 2023 Jasper Wiegratz, SVA, 17 certifications; 2022 Neil D'Souza, ServiceNow, RHCA within a year. |

Verdict: do not merge the two efforts. The award judges a person's certification-driven career story with numbers, not a project. Against the past winners' profiles, a first-time entrant with few certifications has low odds; the entry is still free and the form is short, so enter before 31 October with the owner's real story. If the hackathon project is built on Ansible (idea 7.4) and published on Ansible Galaxy, it becomes one honest bullet under "project-based results" and "open source community outreach". That is the only sensible overlap. The owner's claim of eligibility (a current Red Hat certification) was not verified by us.

## 9. Risks and failure modes

| Risk | Effect | Mitigation |
| --- | --- | --- |
| No acceptable registration email | Cannot enter | Decide on 9 October; write to hackathon@copado.com if needed |
| Trial does not provide a CI/CD key or a pipeline | No live demo; only fixtures | Ask hackathon@copado.com for participant access; keep the offline demo first-class and label it honestly |
| Trial expires before 26 October | Live demo lost | Start the trial on or just before 12 October; record the live run early |
| CLI changes during beta | Tests break | Pin `@copado/agentia-cli@1.0.0-beta.4` in tests; re-record fixtures after upgrades |
| Judges' taste | Lower innovation or impact score | Lead the video with a platform-team pain, show a real failure handled; state why Copado inside Ansible matters to Copado customers |
| Scope creep | Nothing finished | Hold the box in 7.4; cut the plugin command and our MCP server first if time runs out, never the tests |
| Video over 5 minutes or 300 MB, deck over 50 MB | Upload refused | Render at 1080p with a bitrate under 7 Mbps; export the deck as PDF |
| Central time deadline | Late submission | Submit on 25 October India time |
| Exclusive IP licence | Cannot licence the same work elsewhere | Decide before submitting; keep anything you want to reuse out of the submitted work |
| EULA | Building on CLI internals would breach it | Use public commands, JSON output and the SDK only |

## 10. Terminology

Each row: what the word means, and what it means for this project.

| Term | What it is | Why it matters here |
| --- | --- | --- |
| Hackathon | A time-boxed contest where people build a working piece of software and submit it for judging | This one is two weeks, solo, judged on five criteria |
| Virtual hackathon | A hackathon with no physical venue; everything happens online | No travel; submission is a form upload |
| Salesforce | A cloud platform companies use to run sales, service and business processes; it is configured and extended with code and metadata | Copado's whole business is deploying changes to Salesforce safely |
| Salesforce org | One Salesforce environment (a tenant) with its own users, data and configuration | A company has several: production, sandboxes, developer orgs |
| Developer Edition org | A free, small Salesforce org for learning and building | Our way into the Copado trial without a company |
| Sandbox | A copy of a production org used for development or testing | Copado pipelines move changes between sandboxes and production |
| Scratch org | A temporary Salesforce org created from a definition file and deleted later | Core of the alternative idea (7.5) |
| Dev Hub | A Salesforce org setting that allows creating scratch orgs | Needed for 7.5 |
| Metadata | Salesforce's description of configuration and code (objects, fields, layouts, profiles, flows, Apex classes), stored as XML and code files | What gets deployed; what conflicts in merges |
| Apex | Salesforce's programming language, similar to Java | Apex tests are part of quality gates |
| SOQL | Salesforce's query language, similar to SQL | Not needed for our idea |
| Flow | Salesforce's low-code automation | Deployment steps can run Flows |
| Profile, Permission Set | Salesforce access-control metadata; large XML files with many nested entries | The classic source of merge conflicts; Copado has special handling |
| Layout | Page layout metadata | Another conflict-prone type |
| DevOps | The practice of building, testing and releasing software with automation and shared responsibility | The domain of this hackathon |
| CI/CD | Continuous Integration (merge and test often) and Continuous Delivery or Deployment (release in small automated steps) | Copado CI/CD is the product behind the `cicd` commands |
| Copado | Vendor of DevOps tools for Salesforce; organizer of the hackathon | Our judges work there |
| Copado CI/CD | Copado's pipeline product: user stories, promotions, deployments, quality gates, Git integration | The gateway the CLI talks to |
| Copado Robotic Testing (CRT) | Copado's automated UI testing product built on Robot Framework | The `testing` commands; may not be in the trial |
| Robot Framework | An open-source test automation framework with keyword-based test files (.robot) | CRT runs these |
| Copado AI, Agentia agents | Copado's AI agents: Plan, Build, Test, Release, Operate, Knowledge, Orchestrate (chat only) | The `ai` commands; our modules can call them |
| AI Context Hub | A Copado AI product name in the licence list | Appears in the docs prerequisites |
| Agentia | Copado's AI-era product line | The hackathon's subject |
| Agentia Headless | Agentia without a browser: CLI, MCP server, skills, IDE extensions | The thing we must use |
| Headless | Software used without its graphical interface, through commands or APIs | The hackathon's theme: "eliminate the browser tab" |
| CLI | Command-line interface: a program you run by typing commands in a terminal | `agentia` is a CLI |
| Terminal, shell | The text window where commands are typed; zsh on this Mac | Where the demo runs |
| Node.js, npm | Node.js runs JavaScript outside a browser; npm installs JavaScript packages | The CLI is a Node program installed with npm |
| oclif | A framework for building CLIs in TypeScript/JavaScript | The CLI and all plugins are oclif programs |
| beta channel | A pre-release line of versions; `@beta` tag on npm | We install `@copado/agentia-cli@beta` |
| Manifest (oclif.manifest.json) | A file listing every command, description and flag of an oclif CLI | How we counted 234 commands |
| JSON, `--json` | A text format for structured data; the CLI flag that makes every command print JSON | Our modules parse this output |
| JSON envelope | The fixed shape of the CLI's JSON: result, status, transactionId, or error | Our parser relies on it |
| Transaction ID | A unique id printed with every CLI response for support tracing | Include it in evidence logs |
| API | A way for programs to talk to a system without a screen | The Copado gateway is an API the CLI calls |
| API key | A secret string that identifies you to an API | The CI/CD key the CLI needs |
| PAT, PAK | Personal Access Token (Copado AI) and Personal Access Key (CRT): secrets for those APIs | Separate from the CI/CD key |
| Gateway | Copado's server endpoint the CLI calls; chosen by `--region` (na, eu) or `--custom-url` | Where every `cicd` command goes |
| Keychain | macOS's secure store for secrets | Where `agentia auth set` keeps keys |
| Environment variable | A named value given to a program by the shell, such as `AGENTIA_CICD_API_KEY` | How CI and Ansible will pass the key |
| Config files (.agentia/config.json, config.user.json) | Per-project settings and per-user state (active story, branches) | Created by `agentia setup` and `work set` |
| Project defaults | Stored credential, environment, project, sprint, team values so commands need fewer flags | `agentia cicd project default set` |
| User story (work item) | Copado's record for one unit of work; has a feature branch, source environment, status | The unit everything is attached to |
| Pipeline | The ordered chain of environments changes move through (dev -> qa -> prod), with connections between them | Promotions run along it |
| Pipeline connection | One edge from a source environment to a destination environment, with a branch | Created with `pipeline connection create` |
| Stage, stage connection | Named stages (Build, Test, Production) and their order inside a pipeline | Optional structure |
| Environment (Copado) | A Copado record for one Salesforce org; types Production/Developer, Sandbox, Scratch Org, Custom Domain | Created with `environment create` |
| Credential (Copado environment credential) | The stored login Copado uses to reach an org; authorized by browser OAuth | Different from the CLI's API key |
| Promotion | Moving one or more user stories from one environment to the next: merge, optionally deploy | `promotion run --operation merge or merge_and_deploy` |
| Back-promotion | Bringing newer changes from a higher environment back down to keep lower environments current | `work environment-sync` |
| Deployment | Pushing metadata into a Salesforce org | The "deploy" half of a promotion |
| Validate-only | A deployment that checks but does not apply changes | `work submit` without `--done` |
| Job execution | Copado's record of a running or finished operation, with ordered steps and logs | What our event source watches |
| Quality gate | A check that must pass before a change moves on (tests, code analysis) | Local gates are a shell script run by `work test` |
| Local quality gates | `.agentia_quality_gates.sh` in the repository root, run by `work test` and `work submit` | Needs an Extension Configuration record in Copado |
| Extension Configuration | A Copado admin record that registers a tool or gate | Needed for local gates to be recorded |
| Deployment step | An extra action attached to a story that runs during promotion (manual task, Flow, Function, Apex, data) | `work deployment-step` commands |
| Copado Function | A script Copado runs in a container as part of a pipeline | `cicd function` commands; `run-local` uses Docker |
| Release data template | A definition of which records to move between orgs with data deployments | The `data` commands; crowded idea space |
| Git | Version control: a history of file changes in commits on branches | Every story has a feature branch |
| GitHub | A hosting service for Git repositories | The submission must be a public GitHub repository |
| Feature branch | A branch named `feature/<story-name>` holding one story's changes | Created by `work set` |
| Commit | One saved change set in Git | `work publish` registers commits with Copado |
| Merge conflict | Two branches changed the same part of a file and Git cannot combine them | Copado resolves many automatically |
| Semantic merge | Combining XML by meaning (elements) rather than by lines | Copado already has it for nested metadata |
| Smart Conflict Resolution, Auto-Resolve, Online Conflict Resolution | Copado's automatic and manual conflict features | Why the resolver idea was dropped |
| Metadata index compare, dependency list | CLI commands that compare metadata between orgs or branches and list what depends on what | Used by risk and drift entries |
| Health check | `cicd health-check`: organization-scoped governance checks, optionally git-sizer | Useful as a playbook step |
| git-sizer | A tool that reports repository size problems | Optional flag on health check |
| Slack notification subscription | Copado can post pipeline events to Slack users or channels | `notification configure`; also the event list our source plugin mirrors |
| MCP (Model Context Protocol) | A standard that lets AI assistants call tools and read data from programs | Agentia exposes 194 tools over it |
| MCP server, MCP tool, stdio | The program that offers tools; one callable tool; the pipe (standard input/output) the client talks over | `agentia mcp start` |
| MCP annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint) | Labels on tools that tell the client whether a tool only reads, can destroy, is safe to repeat, or reaches the outside world | Our MCP server should set them too |
| Agent Skill, SKILL.md | A Markdown playbook that teaches an AI coding agent how to use a tool safely and in what order | A judging criterion; we ship one |
| AGENTS.md | A project file with instructions for AI agents | Generated by `agentia setup` |
| Coding agent | An AI assistant that edits code and runs commands (Cursor, Copilot and similar) | Reads skills, calls MCP tools |
| Cursor, VS Code | AI code editor; Microsoft's editor | Supported Agentia clients |
| Open VSX | An open registry of VS Code-compatible extensions used by Cursor | Where the Agentia IDE extension lives for Cursor |
| Plugin (Agentia) | An oclif package that adds commands to `agentia` | The official "extension" path |
| Plugin SDK, host API, hostApi | The library plugins use; the curated methods the CLI offers plugins; its version number | `getAgentiaHost({requires})` |
| Scaffold, generator | A tool that creates a starter project | `npm init @copado/agentia-plugin` |
| npm provenance | A signed proof of where a package was built | `npm publish --provenance` |
| Marketplace (Copado) | Copado's planned list of plugins ("submit a plugin: coming soon") | Future distribution |
| Runtime (`agentia runtime`) | A long-lived CLI process the IDE reuses to avoid starting Node for every call | Not needed by us |
| EULA | End User License Agreement: the licence text shipped with the CLI | Section 5.9 |
| Reverse engineering | Working out how software is built from its binaries | Forbidden by the EULA |
| Open source | Software whose source is public under a licence that allows use and change | Our project will be open source (MIT or Apache-2.0, owner's pick) |
| MIT, Apache-2.0 licences | Permissive open-source licences | Used by the strongest competitors |
| Exclusive licence | A licence that forbids the owner from granting the same rights to others | The hackathon's IP clause |
| Royalty-free, perpetual, irrevocable | No payment, forever, cannot be taken back | Same clause |
| Rubric | The published list of judging criteria and points | Five criteria, 1 to 10 each |
| Blind judging | Judges do not see who built the entry | Only the work counts |
| Demo video | The 5-minute screen recording that shows the prototype working | Must match the real functionality |
| Presentation deck | The slide file uploaded with the entry (PDF or PowerPoint, under 50 MB) | Judged under Presentation Quality |
| README | The front page of a repository explaining what it is and how to run it | Judged, implicitly, under Technical Execution |
| Fixture | Recorded sample data used by tests instead of a live system | Lets tests and demos run without a Copado licence |
| Record and replay, fake CLI | Recording real command outputs once, then replaying them from a fake `agentia` executable | Our testing approach |
| Unit test | A small automated check of one piece of code | Hundreds in the strongest entries |
| CI (GitHub Actions) | Automated runs of tests on every push | Expected by judges |
| Idempotent | Running the same action again changes nothing further | Required of good Ansible modules |
| Orchestration | Running steps across several systems in order, with approvals and error handling | The idea's core |
| Ansible | An open-source automation tool (Red Hat) that runs playbooks against systems | Our integration target |
| Ansible Automation Platform (AAP) | Red Hat's commercial product around Ansible with a web UI, schedules and approvals | The enterprise buyer of our collection |
| Playbook | A YAML file of ordered tasks Ansible runs | Our release-window file |
| Module | A unit of work in Ansible (written in Python) with parameters and a result | One per Agentia command group |
| Collection | A packaged set of modules, plugins, roles and docs, installable with `ansible-galaxy` | Our deliverable |
| Ansible Galaxy | The public registry of collections | Where we publish; today it has no Copado collection |
| Event-Driven Ansible (EDA), ansible-rulebook | Ansible's event system: sources emit events, rulebooks match them and run actions | Our Copado event source and rulebook |
| Source plugin | The EDA component that produces events (here: by polling Copado jobs) | Part 2 of the box |
| Check mode, diff mode | Ansible's dry-run and change-preview features | Our modules support them where Copado allows (validate-only) |
| Ephemeral environment | A temporary environment created for one change and destroyed afterwards | The alternative idea |
| Terminal UI (TUI) | A full-screen interface drawn in the terminal | The rejected board idea |
| CST, EDT, IST | Central Standard Time (Copado's clock), Eastern Daylight Time (Red Hat's clock), India Standard Time (ours) | Deadlines |
| Trial | A time-limited free use of a product | Copado's 14-day Agentia Advanced trial |
| Work email, personal webmail, disposable email | Company-domain email; free providers such as Gmail; throwaway addresses | The registration rule |
| Single-page app, JavaScript bundle | A website whose content is drawn by a script after loading | Why the hackathon page had to be read from its script |
| Supabase | A hosted backend (database plus functions) | Stores the hackathon registrations |
| Qualtrics | A survey platform | Hosts the Red Hat nomination form |
| reCAPTCHA | A "prove you are human" check | Blocks automating the Red Hat form |
| Headless browser, CDP | A browser run without a window, driven by the Chrome DevTools Protocol | How we read JavaScript-only pages (Brave on this Mac) |
| Nomination | Putting a person's name forward for an award (self-nomination allowed here) | The Red Hat award's entry method |
| RHCP, RHCSA, RHCE, RHCA | Red Hat Certified Professional (anyone with a Red Hat certification); System Administrator; Engineer; Architect (highest) | Eligibility and the winners' profiles |
| Red Hat Summit | Red Hat's yearly conference (25 to 27 May 2027) | Where the award is given |
| Red Hat Learning Subscription | Red Hat's paid online training subscription | Part of the prize |
| Salesforce Demo Org (SDO) | A demo org Salesforce gives partners | Seen in a Copado employee's repo names |
| copado-hx | The CopadoCon 2026 sample CLI idea wrapping the Copado API | Inspiration only |
| Fleet Radar, Slacktia | Akshara Thakur's two Agentia Headless projects featured by Copado | Examples of what Copado likes |
| TypeScript | JavaScript with types: the compiler catches wrong data shapes before the program runs | The language of the Agentia CLI, the plugin SDK and our plugin command |
| Python | A general-purpose programming language | The language of Ansible modules and our event source |
| YAML | A plain-text format for structured data, using indentation | Playbooks and rulebooks are YAML |
| Markdown | A plain-text format for documents with simple symbols for headings and lists | Skills, README and this handbook are Markdown |
| REST API | An API style over HTTP where each URL is a resource and actions are GET, POST, PUT, DELETE | The Copado gateway behind the CLI is a REST API; we never call it directly |
| SDK | Software Development Kit: a library that makes an API easy to use from code | The Agentia plugin SDK |
| Authentication vs authorization | Proving who you are (login) vs what you are allowed to do (permissions) | API keys authenticate the CLI; Copado permissions authorize what it may do |
| OAuth | A standard where you log in through the provider's own screen and the tool receives a token instead of your password | `environment auth web login` and the Copado trial's "Connect with Salesforce" use it |
| Token | A secret string that proves a login happened, used instead of a password | PAT, PAK and OAuth tokens are tokens |
| Webhook vs polling | Webhook: the system calls you when something happens. Polling: you ask the system again and again | The Agentia CLI offers no webhook, so our event source polls job lists |
| LLM | Large Language Model: the AI model behind AI assistants | Copado AI agents and coding agents are built on LLMs |
| AI agent | An LLM that can use tools and take actions, not only answer | Agentia's agents; the coding agents that read skills |
| RAG | Retrieval-Augmented Generation: giving an LLM relevant documents before it answers | Copado AI "Knowledge" workspaces work this way (conceptually) |
| Salesforce CLI (sf) | Salesforce's own command-line tool for orgs, metadata and tests | `work test apex` runs `sf apex run test`; scratch orgs are created with `sf` |
| Docker, container | A packaged, isolated program environment | `cicd function run-local` runs a Copado Function in Docker |
| Java 17 | A runtime needed by ansible-rulebook (Event-Driven Ansible) | Install on the build machine before the EDA part |
| Acceptance criteria | The user story field that states when the story is done (255 characters max in Copado) | Set with `work create --acceptance-criteria` |
| Sprint, epic, feature, release (Copado) | Planning records a user story can belong to | Flags on `work create` and project defaults |
| Approval pause | A playbook step that waits for a human yes before continuing | The release-window playbook uses one before deploying to production |
| Evidence | Saved proof of what ran and what happened (logs, JSON results, transaction ids) | Our playbooks write it to a folder for audits |

## 11. Command log

Where: "Mac" means this laptop's terminal; "web" means a page fetch or a web search; "browser" means headless Brave driven by a script.

| Command or action | Where | Why | What the output meant |
| --- | --- | --- | --- |
| Read the owner's working rules | Mac | Working rules for this owner (ask where to work, verify facts, English files, no em dash) | Rules applied |
| `date "+%Y-%m-%d %H:%M %Z (%A)"` and `TZ=Asia/Kolkata date` | Mac | Verify today's date before stating deadlines | 2026-10-09, Friday, IST |
| Fetch https://developer.copado.com/hackathon | web | Verify dates, prizes, eligibility, submission, judging | Open registration; dates and prizes confirmed; slide deck required; rubric published |
| `curl -o web/hackathon.html https://developer.copado.com/hackathon` then list `href`s | Mac | Find the Official Rules link | 8 KB shell page; content lives in `/assets/index-BML2g4wS.js` |
| `curl -o web/index.js https://developer.copado.com/assets/index-BML2g4wS.js` then Python extraction of the `en:` blocks | Mac | Read the full page text, forms, FAQ and Official Rules | 1.69 MB bundle; all text in this file's section 3 |
| Python search for `gmail` and `errFreeEmail` in the bundle | Mac | Check whether a Gmail address can register | Client-side blocklist plus server check; one whitelisted address |
| Fetch press release (prnewswire, 14 September 2026) | web | Product status and availability | Early access; general availability from November 2026 |
| Fetch developer.copado.com, /docs, /support | web | Install, prerequisites, licence wording, FAQ | Contradiction in section 4.2; 246 commands claimed; plugin rules |
| Fetch Copado blog about Akshara Thakur | web | Verify a claim from the earlier notes | Real; 29 September 2026 |
| Fetch Success Community group | web | Playground details | Login required |
| `npm view @copado/agentia-cli`, `@copado/agentia-plugin-sdk`, `@copado/create-agentia-plugin` | Mac | Confirm the packages are public and current | beta.4 on 7 October; SDK 0.1.0 on 7 October; generator 0.3.0 |
| `node -v`, `npm -v`, `npm config get prefix`, writability check | Mac | Make sure a global install works without sudo | Node 26.6.0, npm 11.18.0, /opt/homebrew writable |
| `npm install -g @copado/agentia-cli@beta > npm-install-agentia.log` | Mac | Install the CLI (owner approved) | Exit 0, 366 packages, deprecation warnings only |
| `agentia --version` | Mac | Confirm install | 1.0.0-beta.4 darwin-arm64 |
| `agentia --help`, `agentia setup --help`, `agentia auth --help`, `agentia mcp --help`, `agentia plugins --help`, `agentia cicd --help`, `agentia cicd work --help`, `agentia testing --help`, `agentia ai agent ask --help` | Mac | Learn topics and flags | Topics and flags in section 5.3 |
| `agentia auth get --json < /dev/null` (30 s cap) | Mac | See auth state without credentials | CICD not set; CRT missing domain, org, PAK; config file paths shown |
| `agentia setup < /dev/null` (25 s cap) | Mac | See what setup asks first | "Configure global CICD authentication for all projects? (Y/n)", then exit |
| MCP probe: JSON-RPC initialize + tools/list piped into `agentia mcp start` (first attempt) | Mac | List MCP tools | Failed because of a typo in my stderr path (`2>/tmp/../private/...`); no result |
| MCP probe, second attempt with a correct path | Mac | Same | 194 tools listed (section 5.4) |
| `agentia cicd work list --help` and others with `--help` after a nested topic | Mac | Flags | "Command cicd work list not found": oclif parsing quirk, not a missing command |
| `agentia help cicd:work:list` and 27 other `agentia help <topic:command>` calls, saved to probe/cli-help-deep.txt | Mac | Exact flags for environment, credential, pipeline, work, job, promotion, notification, metadata, MCP, runtime, skills, AI, testing commands | Flags quoted in section 5.3 |
| `agentia cicd work list --json < /dev/null` (30 s cap) | Mac | Error shape without a key | Clean JSON error naming `AGENTIA_CICD_API_KEY` and `--custom-url` |
| Python dump of /opt/homebrew/lib/node_modules/@copado/agentia-cli/oclif.manifest.json | Mac | Count and list every command | 234 commands; topic counts in 5.3 |
| `sed -n` on README.md, LICENSE.md, CHANGELOG.md; `cat` of templates/AGENTS.md and the three skills with their reference files, saved to probe/cli-deep.txt | Mac | Licence terms, MCP configuration, local quality gates, release history, exact agent workflows | Sections 5.3, 5.5, 5.8, 5.9 |
| `find` for markdown and skill folders in the package | Mac | Locate shipped skills | templates/skills/agentia-ai, agentia-cicd, agentia-testing |
| GitHub search API: `agentia copado`, `agentia-plugin`, `copado agentia cli`, `agentia headless`, `copado conflict`, `agentia conflict`, `copado merge conflict`, `copado ansible`, `agentia ansible`, `salesforce ansible collection devops` | Mac (curl) | Map the competition and check white space | Section 6; zero results for conflict tools and for Ansible |
| GitHub API: public repos of chamanswami555 | Mac (curl) | Fit the idea to the owner's stack | 33 repos: TypeScript, JavaScript, Dart, Python, Java; several hackathons |
| Fetch READMEs: Agentia-Sentinel, agentia-timemachine, agentia-data-vault, sdo-agentia-pipeline, agentia-release-guardian, shipguard-agentia, agentia-mutant, agentia-org-graph, agentia-env-drift, agentia-skills-pack, COPADO-NEXUS, mc-ship; raw README of release-intelligence | web | Quality bar and taken spaces | Section 6. mc-ship at manojkusikar returned 404 (it lives under mcshipdev-design); release-intelligence README not readable |
| Fetch github.com/Copado/agentia-cli | web | Source availability | 404: private |
| Fetch copado.com/agentia; `curl` app.copado.com/trial and its bundle; browser render of app.copado.com/trial | web, Mac, browser | How the trial works and whether Gmail is blocked | 14-day trial via "Connect with Salesforce"; no email form |
| Fetch login.copado.com/trial | web | Trial link | 301 redirect to app.copado.com/trial |
| Ansible Galaxy API search `copado`, `salesforce` | Mac (curl) | Existing collections | Zero Copado collections |
| Web searches on Copado conflict resolution; `curl` and browser renders of docs.copado.com article "Merge Conflict Resolution Overview and Types" | web, Mac, browser | Does Copado already merge metadata semantically | First two renders captured only the article index; the third render (shadow DOM capture) got the body: Auto-Resolve, Semantic Merge for Nested Metadata, Smart Conflict Resolution, 50 MB limit, resume from the conflicting story |
| Web search on Copado scratch org support (docs.copado.com) | web | Duplication risk for idea 7.5 | Scratch Org Wizard and DX Scratch Org Operations exist in the docs; currency unknown |
| Fetch Red Hat award page; `curl` of the page; `curl` of its rules page; browser render of the Qualtrics form; web search on the 2026 winner | web, Mac, browser | Award facts, status, judging, past winners | Section 8. The rules page returned 404 to the fetch tool but 200 to curl |
| `curl` of the CopadoCON Bangalore June 2026 spec (twice) | Mac | Earlier Copado hackathon spec | HTTP 503 both times; not available |
| Wrote a temporary cdp-dump.mjs (Node script: launch Brave headless, load URL, scroll, capture text, form fields, console, screenshot, shadow DOM and iframes) | Mac | Read pages that only render with JavaScript | Used for the three browser renders above |
| `mkdir -p /Users/chaman/copado-agentia-hackathon/docs` | Mac | Project folder (owner's pick) | This file lives there |

Mistakes made and corrected during the research: the first MCP probe failed on my own path typo; `--help` after nested topics misled me for one round until `agentia help topic:command` worked; a first attempt to extract the Official Rules used the wrong text pattern and found nothing until the search anchor was changed; an early `grep` pattern was too complex for the Mac's grep and was replaced by a Python script.

## 12. Sources

- https://developer.copado.com/hackathon (page and its script bundle /assets/index-BML2g4wS.js, including the Official Rules)
- https://developer.copado.com/ , https://developer.copado.com/docs , https://developer.copado.com/support
- https://www.prnewswire.com/news-releases/copado-brings-governed-agentops-directly-to-salesforce-developers-with-agentia-headless-302877066.html
- https://www.copado.com/resources/blog/a-17-year-old-student-just-showed-us-what-agentia-headless-is-really-for
- https://www.copado.com/agentia , https://app.copado.com/trial
- https://docs.copado.com/articles/copado-ci-cd-publication/merge-conflict-resolution-overview-and-types
- https://www.npmjs.com/package/@copado/agentia-cli , @copado/agentia-plugin-sdk , @copado/create-agentia-plugin
- Installed package /opt/homebrew/lib/node_modules/@copado/agentia-cli (README.md, LICENSE.md, CHANGELOG.md, oclif.manifest.json, templates/)
- https://success.copado.com/s/group/0F9P70000000ZNZKA2/agentia-headless-cli-mcp-ide (login required)
- GitHub repositories listed in section 6; https://api.github.com/search/repositories
- https://galaxy.ansible.com/api/v3/plugin/ansible/search/collection-versions/
- https://www.redhat.com/en/services/certification/rhcp/rhcp-of-the-year and /rules ; https://www.feedback.redhat.com/jfe/form/SV_7QfJpDtnbJGkuvc
- The owner's earlier research notes (used only as a list of claims to check)

## 13. Open decisions

1. Registration email: done, company email <registration email> used (10 October 2026). Submission must use the same address. Git author for the repository is Chaman Swami <chamanswami555@gmail.com> (owner's pick). GitHub repository: private chamanswami555/agentia-ansible, SSH access from this Mac still to be set up (no key for this account is configured yet). Name decided: repository agentia-ansible, collection chamanswami555.agentia, plugin command `agentia ansible`. Licence decided: MIT.
2. Project name: done (see item 1).
3. Idea lock: done 10 October 2026 (section 1).
4. Open-source licence: done, MIT.
5. Whether the exclusive IP licence in the hackathon rules is acceptable.
6. Working files of the build: kept on the owner's machine only, outside the repository (owner's instruction).
7. Whether to enter the Red Hat award and what the real story is.
8. When to create the project .docx (problem, market solutions, our solution, how it was built, setup guide) that every project folder keeps; proposed: at the end of the first build week.
