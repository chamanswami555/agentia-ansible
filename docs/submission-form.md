# Submission form text

Fields as listed on the hackathon submission form (handbook section 3.7). Submit with the
registration email. Every value below is final English text; paste as is. Nothing here names the
tools the project was built with.

| Field | Value |
| --- | --- |
| Full name | Chaman Swami |
| Email | (the registration address, filled in by the owner) |
| LinkedIn URL | (owner fills in) |
| Submission title | agentia-ansible: Copado releases as Ansible automation |
| GitHub repository link | https://github.com/chamanswami555/agentia-ansible |
| Demo video file | agentia-ansible-demo.mp4 (5 minutes or less, under 300 MB) |
| Presentation deck file | agentia-ansible-deck.pdf (under 50 MB) |

## Problem statement (judges read this first)

Platform and operations teams already run their change windows from Ansible and Ansible Automation
Platform: inventories, approvals, schedules, role-based access and a job history that doubles as
evidence. Salesforce releases through Copado sit outside that world. A person presses Submit in
Copado, waits for the jobs, and copies screenshots into the change ticket. Validation, smoke tests,
approval and deployment are four separate manual steps, and a failed Copado job at night waits for
someone to notice it in the morning. Copado's Agentia Headless CLI makes every one of those steps
scriptable with JSON output, but a scriptable CLI is not yet an automation building block: every
team would still write its own shell loops, polling, JSON parsing, error handling and approval
logic.

## Abstract

agentia-ansible turns the Copado Agentia Headless CLI into first-class Ansible building blocks. The
collection `chamanswami555.agentia` provides twelve idempotent modules (user stories, submit,
promotions, job executions, waits, Robotic Testing, metadata comparison, health check, Copado AI)
with check and diff mode, Copado transaction ids and the CLI's own error messages. Three playbooks
cover the release window (validate each story and wait for its check-only deployment, smoke suite,
an approval gate that fails closed without a human, then the Copado Submit with waits on the
promote and deployment jobs, and a JSON evidence folder), nightly validation, and remediation of a
failed job. An Event-Driven Ansible source polls Copado job executions and a rulebook starts the
remediation playbook when a job fails. An Agentia CLI plugin adds `agentia ansible scaffold` and
`agentia ansible run`, an MCP server exposes five governed tools for AI agents, and an Agent Skill
teaches coding agents to author playbooks with the collection. Every part ran against a real Copado
org: four full release rehearsals, the rulebook live, the MCP server in check mode.

## Problem solved / gap addressed

Salesforce releases become one job template in the same Ansible workflow as everything else, with
the same approval node, evidence folder and schedule, and a failed Copado job triggers remediation
on its own. Teams get a tested, idempotent layer instead of a shell loop per team, and AI agents get
governed workflows with an approval gate instead of raw commands. No equivalent exists on Ansible
Galaxy or GitHub.

## Tools used (what the project was actually built with)

Copado Agentia Headless CLI 1.0.0-beta.5 and beta.6 (`@copado/agentia-cli`), the Agentia plugin SDK
and generator (`@copado/agentia-plugin-sdk`, `@copado/create-agentia-plugin`), Copado Playground
(Copado Pipelines, Salesforce Source Format), Ansible (ansible-core 2.18), ansible-rulebook 1.3 with
Java 17, Python 3.12, Node.js, the Model Context Protocol SDK, pytest, ansible-test, ansible-lint,
GitHub Actions.

## Optional notes for the judges

The README section "Why not just..." answers the expected objections with evidence. The fixtures
README lists where every recorded CLI answer came from. Rollback, a Windows control node and live
runs of Robotic Testing and Copado AI are outside this version and are listed as such.
