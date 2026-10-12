#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_work_submit
short_description: Submit the active Copado user story for validation or promotion
version_added: "0.1.0"
description:
  - Runs C(agentia cicd work submit) in a Git working copy. By default the submit is a
    validation only; with I(done=true) it promotes, matching the Copado UI Submit.
  - Optionally activates a story first with C(agentia cicd work set).
  - This is an action, so the task reports C(changed) whenever it runs. Check mode only
    reports what would run.
options:
  working_dir:
    description: The Git working copy of the Salesforce project (required).
    type: path
    required: true
  set_story:
    description: Story id or name to activate with C(work set) before submitting.
    type: str
  done:
    description: Promote instead of validate only (Copado UI Submit).
    type: bool
    default: false
  skip_local_tests:
    description: Skip the project's local quality-gate script.
    type: bool
    default: false
  skip_pull_request:
    description: Do not open the pull request compare URL (recommended in automation).
    type: bool
    default: true
  apex_test_classes:
    description: Apex test classes passed to the local quality gates.
    type: list
    elements: str
  skip_nested_metadata_detection:
    description: Do not detect nested metadata changed across the branch.
    type: bool
    default: false
  cli_path:
    description: Path to the C(agentia) executable.
    type: str
    default: agentia
  timeout:
    description: Seconds to wait for the CLI call.
    type: int
    default: 900
author:
  - Chaman Swami (@chamanswami555)
"""

EXAMPLES = r"""
- name: Validate the story in the pipeline
  chamanswami555.agentia.agentia_work_submit:
    working_dir: /srv/salesforce/crm
    set_story: US-0042

- name: Promote after approval
  chamanswami555.agentia.agentia_work_submit:
    working_dir: /srv/salesforce/crm
    done: true
"""

RETURN = r"""
submission:
  description: The submit result as the CLI returned it.
  returned: when not in check mode
  type: raw
commands:
  description: The CLI argument lists that ran, or would run in check mode.
  returned: always
  type: list
transaction_id:
  description: Transaction id of the last CLI call.
  returned: when not in check mode
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.chamanswami555.agentia.plugins.module_utils.agentia import (
    AgentiaCli,
    AgentiaError,
    agentia_argument_spec,
)


def build_commands(params):
    commands = []
    if params["set_story"]:
        commands.append(["cicd", "work", "set", params["set_story"]])
    submit = ["cicd", "work", "submit"]
    if params["done"]:
        submit.append("--done")
    if params["skip_local_tests"]:
        submit.append("--skip-local-tests")
    if params["skip_pull_request"]:
        submit.append("--skip-pull-request")
    if params["skip_nested_metadata_detection"]:
        submit.append("--skip-nested-metadata-detection")
    if params["apex_test_classes"]:
        submit += ["--apex-test-classes=%s" % ",".join(params["apex_test_classes"])]
    commands.append(submit)
    return commands


def run_module():
    spec = dict(agentia_argument_spec())
    spec["working_dir"] = {"type": "path", "required": True}
    spec.update({
        "set_story": {"type": "str"},
        "done": {"type": "bool", "default": False},
        "skip_local_tests": {"type": "bool", "default": False},
        "skip_pull_request": {"type": "bool", "default": True},
        "apex_test_classes": {"type": "list", "elements": "str"},
        "skip_nested_metadata_detection": {"type": "bool", "default": False},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    commands = build_commands(module.params)
    if module.check_mode:
        module.exit_json(changed=True, commands=commands)
    cli = AgentiaCli(module)
    result, tx = None, None
    try:
        for command in commands:
            result, tx = cli.run(command)
    except AgentiaError as exc:
        module.fail_json(changed=False, commands=commands, **exc.as_dict())
    module.exit_json(changed=True, submission=result, commands=commands, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()
