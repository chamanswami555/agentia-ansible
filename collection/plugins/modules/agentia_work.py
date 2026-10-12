#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_work
short_description: Create, update or delete a Copado user story through Agentia CLI
version_added: "0.1.0"
description:
  - Manages a Copado user story (work item) with the C(agentia cicd work) commands.
  - Reads the story first and only sends an update when a managed field differs, so a
    play can be re-run safely.
  - Supports check mode and diff mode.
options:
  id:
    description:
      - Salesforce record id or story name (for example C(US-0001)) of an existing story.
      - When omitted and I(state=present), a story is created, unless I(lookup_by_title)
        finds one with the same title.
    type: str
    aliases: [name]
  title:
    description: Story title. Required when creating.
    type: str
  status:
    description: Story status, for example C(Draft) or C(Development In Progress).
    type: str
  acceptance_criteria:
    description: Acceptance criteria. Copado accepts fewer than 255 characters.
    type: str
  project:
    description: Copado project id for a new story.
    type: str
  team:
    description: Team value for a new story.
    type: str
  assignee:
    description: Assignee id.
    type: str
  epic:
    description: Epic.
    type: str
  feature:
    description: Feature.
    type: str
  sprint_id:
    description: Sprint id.
    type: str
  priority:
    description: Priority.
    type: str
  source_credential:
    description: Source credential id. Copado derives the source environment from it.
    type: str
  functional_requirements:
    description: Functional requirements text.
    type: str
  technical_specifications:
    description: Technical specifications text.
    type: str
  lookup_by_title:
    description:
      - When I(id) is omitted, search existing stories by exact title before creating one.
    type: bool
    default: true
  state:
    description: Whether the story should exist.
    type: str
    choices: [present, absent]
    default: present
  cli_path:
    description: Path to the C(agentia) executable.
    type: str
    default: agentia
  working_dir:
    description: Directory to run the CLI in, where C(.agentia) project defaults live.
    type: path
  timeout:
    description: Seconds to wait for one CLI call.
    type: int
    default: 900
notes:
  - Credentials come from the Agentia keychain or the C(AGENTIA_CICD_API_KEY) and
    related environment variables of the Ansible process. They are never module options.
  - Fields the CLI does not echo back in C(work get) are sent on every run when provided;
    the module then reports C(changed). Keep such fields in a one-off task.
author:
  - Chaman Swami (@chamanswami555)
"""

EXAMPLES = r"""
- name: Ensure the release story exists
  chamanswami555.agentia.agentia_work:
    title: "Release 2026.10: account service hardening"
    status: Draft
    acceptance_criteria: "All account tests pass in UAT"
  register: story

- name: Move the story to development
  chamanswami555.agentia.agentia_work:
    id: "{{ story.work_item.name }}"
    status: Development In Progress

- name: Remove a story created by a dry run
  chamanswami555.agentia.agentia_work:
    id: US-0042
    state: absent
"""

RETURN = r"""
work_item:
  description: The story record as the CLI returned it after the operation.
  returned: when state is present
  type: dict
transaction_id:
  description: Transaction id of the last CLI call, for Copado support.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.chamanswami555.agentia.plugins.module_utils.agentia import (
    AgentiaCli,
    AgentiaError,
    agentia_argument_spec,
    as_list,
    is_not_found,
)

# Module option -> (CLI flag, key in the record the CLI returns, or None when unknown).
# A None key means the value cannot be compared yet, so it is sent whenever provided.
FIELDS = {
    "title": ("--title", "title"),
    "status": ("--status", "status"),
    "acceptance_criteria": ("--acceptance-criteria", "acceptanceCriteria"),
    "project": ("--project", "project"),
    "team": ("--team", "team"),
    "assignee": ("--assignee", "assignee"),
    "epic": ("--epic", None),
    "feature": ("--feature", None),
    "sprint_id": ("--sprint-id", "sprintId"),
    "priority": ("--priority", "priority"),
    "source_credential": ("--source-credential", "sourceCredential"),
    "functional_requirements": ("--functional-requirements", "functionalRequirements"),
    "technical_specifications": ("--technical-specifications", "technicalSpecifications"),
}


def _record_value(record, key):
    """Read a field from the CLI record; nested records (epic, feature) compare by id."""
    value = record.get(key) if isinstance(record, dict) else None
    if isinstance(value, dict):
        return value.get("id") or value.get("name")
    return value


def _get(cli, story_id):
    """Return (record, transaction_id, not_found_message); record is None when missing."""
    try:
        result, tx = cli.run(["cicd", "work", "get", story_id])
        return result, tx, None
    except AgentiaError as exc:
        if is_not_found(exc):
            return None, exc.transaction_id, exc.message
        raise


def _find_by_title(cli, title):
    result, tx = cli.run(["cicd", "work", "list", "--title", title, "--page-size", "50"])
    for item in as_list(result):
        if isinstance(item, dict) and item.get("title") == title:
            return item, tx
    return None, tx


def _desired_changes(params, current):
    """Return (flags, before, after) for fields that differ or cannot be compared."""
    flags, before, after = [], {}, {}
    for option, (flag, key) in FIELDS.items():
        wanted = params.get(option)
        if wanted is None:
            continue
        if key is not None and current is not None:
            have = _record_value(current, key)
            if have == wanted:
                continue
            before[option] = have
        after[option] = wanted
        flags += [flag, wanted]
    return flags, before, after


def run_module():
    spec = dict(agentia_argument_spec())
    spec.update({
        "id": {"type": "str", "aliases": ["name"]},
        "lookup_by_title": {"type": "bool", "default": True},
        "state": {"type": "str", "choices": ["present", "absent"], "default": "present"},
    })
    for option in FIELDS:
        spec[option] = {"type": "str"}
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    cli = AgentiaCli(module)
    result = {"changed": False, "transaction_id": None}

    try:
        current, tx, missing = (None, None, None)
        if params["id"]:
            current, tx, missing = _get(cli, params["id"])
            if current is None and params["state"] == "present":
                # An explicit id names an existing record; never create in its place.
                module.fail_json(msg=missing or "User story %s not found" % params["id"],
                                 transaction_id=tx, changed=False)
        elif params["state"] == "present" and params["lookup_by_title"] and params["title"]:
            current, tx = _find_by_title(cli, params["title"])
        result["transaction_id"] = tx

        if params["state"] == "absent":
            if current is None:
                module.exit_json(**result)
            story_id = current.get("id") or params["id"]
            result["changed"] = True
            result["diff"] = {"before": {"id": story_id, "present": True}, "after": {"present": False}}
            if not module.check_mode:
                _, tx = cli.run(["cicd", "work", "delete", story_id])
                result["transaction_id"] = tx
            module.exit_json(**result)

        if current is None:
            if not params["title"]:
                module.fail_json(msg="title is required to create a story", **result)
            flags, _, after = _desired_changes(params, None)
            result["changed"] = True
            result["diff"] = {"before": {}, "after": after}
            if module.check_mode:
                result["work_item"] = after
                module.exit_json(**result)
            created, tx = cli.run(["cicd", "work", "create"] + flags)
            result["transaction_id"] = tx
            result["work_item"] = created
            module.exit_json(**result)

        flags, before, after = _desired_changes(params, current)
        result["work_item"] = current
        if not flags:
            module.exit_json(**result)
        story_id = current.get("id") or params["id"]
        result["changed"] = True
        result["diff"] = {"before": before, "after": after}
        if module.check_mode:
            module.exit_json(**result)
        updated, tx = cli.run(["cicd", "work", "update", story_id] + flags)
        result["transaction_id"] = tx
        result["work_item"] = updated if isinstance(updated, dict) and updated else current
        module.exit_json(**result)
    except AgentiaError as exc:
        module.fail_json(changed=result["changed"], **exc.as_dict())


def main():
    run_module()


if __name__ == "__main__":
    main()
