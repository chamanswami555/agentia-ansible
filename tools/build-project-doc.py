"""Build docs/agentia-ansible-project.docx: the project document (problem, market solutions, our
solution, how it was built, setup, terminology, status). Fixed layout through the Python document library.

Run: .venv-tools/bin/python -I tools/build-project-doc.py
"""
import datetime
import pathlib

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "agentia-ansible-project.docx"
TODAY = datetime.date.today().strftime("%d %B %Y")

doc = Document()
styles = doc.styles
styles["Normal"].font.name = "Calibri"
styles["Normal"].font.size = Pt(11)
for level, size in ((1, 16), (2, 13)):
    style = styles[f"Heading {level}"]
    style.font.name = "Calibri"
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)


def heading(text, level=1):
    doc.add_heading(text, level=level)


def para(text):
    doc.add_paragraph(text)


def bullets(items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def table(rows, header=True, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.text = value
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9.5)
                    if header and r == 0:
                        run.bold = True
    doc.add_paragraph()


title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = title.add_run("agentia-ansible")
run.bold = True
run.font.size = Pt(26)
sub = doc.add_paragraph("Copado releases as Ansible automation. Project document.")
sub.runs[0].font.size = Pt(13)

table([
    ["Item", "Value"],
    ["Document", "Project document: problem, market solutions, our solution, how it was built, setup guide, terminology, status"],
    ["Version", "1.0"],
    ["Date", TODAY],
    ["Owner", "Chaman Swami"],
    ["Repository", "https://github.com/chamanswami555/agentia-ansible"],
    ["Status", "Submission candidate for the Copado Agentia Headless Virtual Hackathon 2026 (build window 12 to 26 October 2026)"],
])

heading("1. Decision")
para("Build and submit an Ansible collection, an Event-Driven Ansible source, an Agentia CLI plugin command, an MCP server and an Agent Skill that run Copado releases through the Copado Agentia Headless CLI. Idea fixed on 10 October 2026; core built and verified against a real Copado org on 14 October 2026; hardened on 15 and 16 October 2026.")

heading("2. The problem")
para("Platform and operations teams run their change windows from Ansible and Ansible Automation Platform: inventories, approvals, schedules, role-based access and a job history that doubles as evidence. Salesforce releases through Copado sit outside that world.")
bullets([
    "A person presses Submit in Copado, waits for the jobs and copies screenshots into the change ticket.",
    "Validation, smoke tests, approval and deployment are four separate manual steps.",
    "A Copado job that fails at night waits for someone to notice it in the morning.",
    "The Agentia Headless CLI makes each step scriptable with JSON output, but a scriptable CLI is not an automation building block: every team would still write its own polling, JSON parsing, error handling and approval logic.",
])

heading("3. Solutions on the market")
table([
    ["Option", "What it gives", "What is missing for a platform team"],
    ["Copado's own automations (Functions, Quality Gates, Slack notifications)", "Automation inside Copado", "Runs inside Copado only; the Salesforce leg stays separate from the rest of the change window"],
    ["CI pipelines (GitHub Actions, Jenkins) calling the CLI", "Scripted runs on push", "No approval nodes, inventories, credentials store, schedules or event-driven remediation; every pipeline re-implements polling and parsing"],
    ["Copado's Agentia local MCP server", "194 raw tools for AI agents", "Raw tools, no governed workflow, no approval gate, no evidence folder"],
    ["Manual operation in the Copado UI", "Works for one story", "Not repeatable, no evidence trail, no night-time reaction to failures"],
    ["Ansible Galaxy and GitHub (searched 9 October 2026)", "Nothing for Copado; zero Ansible content for Agentia", "This is the gap"],
])

heading("4. Our solution")
para("agentia-ansible puts the Copado Agentia Headless CLI where operations teams already work.")
table([
    ["Component", "Contents"],
    ["Ansible collection chamanswami555.agentia", "12 modules (user stories, submit, promotions, promotion info, job info, job wait, job actions, Robotic Testing, metadata comparison, health check, Copado AI), idempotent, check and diff mode, Copado transaction ids, the CLI's own error messages, a per-call timeout"],
    ["Playbooks", "release_window (validate each story and wait for its check-only deployment, smoke suite, approval gate that fails closed, Copado Submit with waits on the promote and deployment jobs, JSON evidence folder, health checks before and after; promotion mode for an existing promotion), nightly_validate, remediate_failed_job"],
    ["Event-Driven Ansible", "Source agentia_jobs polls job executions (and promotions) and emits status changes; rulebook copado_release runs the remediation playbook when a job ends in Error or Failed"],
    ["Agentia CLI plugin", "agentia ansible scaffold (reads the active story through the plugin SDK host, writes the playbook) and agentia ansible run (check, approve, JSON; finds the collection on its own; names the stop at the approval gate)"],
    ["MCP server", "Five governed tools: list_playbooks, run_release_playbook, run_playbook, list_evidence, release_status; without approve the run stops at the gate and nothing is deployed"],
    ["Agent Skill", "Teaches a coding agent the module order, the real shapes learned from Copado and the rules for safe playbooks"],
    ["Developer tools", "Fake CLI replaying recorded answers, seven-step offline demo, rulebook demo, fixture recorder with scrubbing, local quality gate script for Source Format projects"],
])
para("The approval gate deserves a line of its own: an Ansible pause alone does not stop a run without a terminal (Ansible warns and continues), so the playbook asks for a typed yes and asserts approval; MCP, AWX and CI runs pass approve=true after their own approval step. A run without approval and without a terminal is part of the offline demo and was also executed on the real org: validation ran, the gate stopped the run, nothing was deployed.")

heading("5. How it was built")
table([
    ["When (2026)", "What"],
    ["9 October", "Facts of the hackathon verified from the page and the Official Rules; competition mapped (about 30 repositories); the conflict-resolver idea killed (Copado has it); Ansible gap confirmed on Galaxy and GitHub"],
    ["10 October", "Idea fixed; registered; repository, names and MIT licence decided"],
    ["12 October", "Collection, fake CLI, unit tests, playbooks, skill, CI, plugin and MCP server built offline against synthetic answers; two mutation checks"],
    ["13 October", "Copado Playground created (the trial path gave no API key)"],
    ["14 October", "API key; 45 real CLI answers recorded and scrubbed; modules smoke-tested live; story flow by hand; four release rehearsals through the plugin (Dev1 to INT, INT to UAT); rulebook live; MCP in check mode; bugs found by the live runs fixed (validation promotion cannot be merged, the submit names the promote job not the deployment, duplicate command key, fixture key mismatch, unset call log)"],
    ["15 October", "ansible-lint (production profile), ansible-test sanity (24 tests), failure chain proved offline, local quality gate verified live, coverage floor, Galaxy importer check, judge-probe round: approval gate, real timeout, collection auto-detection, evidence root; CLI beta.6 re-verified"],
    ["16 October", "Promotion mode, two stories, failing nightly and check mode added to the offline demo; objections answered in the README; demo story, video script, deck, form text and this document"],
])
para("Verification at the end of the build: 75 unit tests at 96 percent coverage with a 90 percent floor; ansible-test sanity 24 tests; ansible-lint production profile; seven-step offline demo and the rulebook demo; MCP 6 tests; plugin 5 tests; CI green on every push; four live release rehearsals, the rulebook, the MCP server and the quality gate on a real Copado org.")

heading("6. Setup guide")
heading("6.1 Offline, without a Copado licence", 2)
bullets([
    "Requirements: Python 3.12 with uv, GNU make, Node.js 20 or newer; Java 17 for the rulebook demo.",
    "git clone git@github.com:chamanswami555/agentia-ansible.git; cd agentia-ansible",
    "make setup (creates .venv with ansible-core, pytest, ansible-lint, ansible-rulebook; links the collection under var/)",
    "make check (pyflakes, ansible-lint, unit tests with the coverage floor, ansible-doc)",
    "make demo (the seven-step playbook demo and the rulebook demo against the fake CLI)",
    "make sanity (ansible-test sanity on a copy outside the repository)",
    "cd mcp && npm ci && npm test; cd plugin && npm ci && npm test",
])
heading("6.2 Live, with a Copado org", 2)
bullets([
    "npm install -g @copado/agentia-cli@beta; agentia auth set --cicd <key> --region <na|emea|...>; agentia cicd health-check --json",
    "ansible-galaxy collection build collection --output-path var/build; ansible-galaxy collection install var/build/chamanswami555-agentia-0.1.0.tar.gz",
    "cd plugin && npm ci && npm run build && cd .. && agentia plugins link plugin",
    "In the clone of the Salesforce project, with a story that has published commits: agentia ansible scaffold --stories US-0001 --repo-dir . --out release-window.yml; agentia ansible run --playbook release-window.yml --check; agentia ansible run --playbook release-window.yml --approve",
    "Optional local quality gate: copy tools/quality-gates/agentia_quality_gates.sh to the project root as .agentia_quality_gates.sh",
    "Event-Driven Ansible: JAVA_HOME at the JDK home; ansible-rulebook --rulebook collection/extensions/eda/rulebooks/copado_release.yml -i collection/extensions/eda/inventory.yml",
    "MCP: node mcp/server.mjs over stdio; client configuration in mcp/README.md",
])

heading("7. Terminology")
table([
    ["Term", "What it is", "Why it matters here"],
    ["Copado Agentia Headless CLI", "Copado's command-line interface with JSON output for CI/CD, testing and AI", "Every module runs one of its public commands"],
    ["Copado Submit", "The action that moves a user story to the next environment: promotion, merge, deployment", "Story mode of the release playbook uses it (work submit --done)"],
    ["Validation promotion", "A check-only promotion created by work submit without --done; it cannot be merged later", "Why the playbook validates first and submits with --done afterwards"],
    ["Promote job, deployment job", "The two job executions behind one promotion", "The playbook waits for both; the promotion record names the deployment job"],
    ["Idempotent", "Running the same task twice changes nothing the second time", "agentia_work creates a story once and reports no change afterwards"],
    ["Check mode", "Ansible's dry run: tasks report what they would do", "Every module supports it; the release playbook runs clean in check mode"],
    ["Evidence folder", "JSON files written per run: health checks, validations, deployment, test results", "What goes into the change ticket"],
    ["Approval gate", "A typed yes or approve=true, asserted; a plain pause is skipped without a terminal", "Nothing deploys without a human decision, also from MCP, AWX and CI"],
    ["Event-Driven Ansible", "ansible-rulebook: sources emit events, rules match them, actions run playbooks", "A failed Copado job starts remediation"],
    ["MCP", "Model Context Protocol: how AI agents call tools", "Five governed tools instead of raw commands"],
    ["Agent Skill", "A Markdown file that teaches a coding agent a workflow", "Makes the collection usable by agents"],
    ["Fixture", "A recorded CLI answer replayed by the fake CLI in tests and demos", "45 real recordings, scrubbed, plus synthetic ones with their origin listed"],
    ["ansible-test sanity, ansible-lint", "Ansible's own quality suites for collections and playbooks", "Both pass; both run in CI"],
    ["Ansible Galaxy", "The public registry for Ansible collections", "Publish target after the submission is final"],
])

heading("8. Status and limitations")
bullets([
    "Done and verified: everything in section 4, on a real Copado org, with the test counts of section 5.",
    "Not in this version: rollback (the CLI has no rollback operation; Copado keeps it), a Windows control node, live runs of Robotic Testing and Copado AI (no licence in the playground; verified against recorded answers), promotion mode live (verified offline).",
    "Next: demo video, Galaxy publish after the submission is final, an AWX job template and an ephemeral environment playbook as stretch goals.",
])

# Document properties name the owner, not the library that wrote the file.
doc.core_properties.author = "Chaman Swami"
doc.core_properties.last_modified_by = "Chaman Swami"
doc.core_properties.title = "agentia-ansible: project document"
doc.core_properties.subject = "Copado releases as Ansible automation"
doc.core_properties.comments = ""
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print("wrote", OUT)
