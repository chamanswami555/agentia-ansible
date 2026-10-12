#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_promotion
short_description: Run or resume a Copado promotion through Agentia CLI
version_added: "0.1.0"
description:
  - Runs C(agentia cicd promotion run) for a promotion id, with merge or merge-and-deploy,
    optionally waiting for the executions to finish, or resumes an existing execution.
  - This is an action, so the task reports C(changed) whenever it runs. Check mode only
    reports the command that would run.
options:
  id:
    description: 18-character Salesforce promotion id.
    type: str
    required: true
  operation:
    description: Promotion operation. Required unless I(resume) is given.
    type: str
    choices: [merge, merge_and_deploy]
  resume:
    description: Resume this existing job execution id instead of starting a new run.
    type: str
  wait:
    description: Poll the promotion and deployment executions until they finish.
    type: bool
    default: true
  wait_timeout:
    description: Maximum seconds to wait when I(wait) is true.
    type: int
    default: 900
  deployment_step_ids:
    description: Ordered deployment-step ids to pass to the run.
    type: list
    elements: str
  cli_path:
    description: Path to the C(agentia) executable.
    type: str
    default: agentia
  working_dir:
    description: Directory to run the CLI in.
    type: path
  timeout:
    description: Seconds to wait for the CLI call.
    type: int
    default: 900
author:
  - Chaman Swami (@chamanswami555)
"""

EXAMPLES = r"""
- name: Merge and deploy the release promotion and wait for it
  chamanswami555.agentia.agentia_promotion:
    id: a0BXXXXXXXXXXXXXXX
    operation: merge_and_deploy
    wait_timeout: 1800
  register: promo

- name: Resume after a merge conflict was resolved
  chamanswami555.agentia.agentia_promotion:
    id: a0BXXXXXXXXXXXXXXX
    resume: a4NXXXXXXXXXXXXXXX
"""

RETURN = r"""
promotion:
  description: The run result as the CLI returned it (execution ids and statuses).
  returned: when not in check mode
  type: raw
command:
  description: The CLI argument list that ran, or would run in check mode.
  returned: always
  type: list
transaction_id:
  description: Transaction id of the CLI call.
  returned: when not in check mode
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.chamanswami555.agentia.plugins.module_utils.agentia import (
    AgentiaCli,
    AgentiaError,
    agentia_argument_spec,
)


def build_command(params):
    command = ["cicd", "promotion", "run", params["id"]]
    if params["resume"]:
        command += ["--resume", params["resume"]]
    else:
        command += ["--operation", params["operation"]]
    command.append("--wait" if params["wait"] else "--no-wait")
    if params["wait"]:
        command += ["--wait-timeout", str(params["wait_timeout"])]
    for step in params["deployment_step_ids"] or []:
        command += ["--deployment-step-id", step]
    return command


def run_module():
    spec = dict(agentia_argument_spec())
    spec.update({
        "id": {"type": "str", "required": True},
        "operation": {"type": "str", "choices": ["merge", "merge_and_deploy"]},
        "resume": {"type": "str"},
        "wait": {"type": "bool", "default": True},
        "wait_timeout": {"type": "int", "default": 900},
        "deployment_step_ids": {"type": "list", "elements": "str"},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True,
                           required_one_of=[["operation", "resume"]],
                           mutually_exclusive=[["operation", "resume"]])
    command = build_command(module.params)
    if module.check_mode:
        module.exit_json(changed=True, command=command)
    cli = AgentiaCli(module)
    try:
        result, tx = cli.run(command)
    except AgentiaError as exc:
        module.fail_json(changed=False, command=command, **exc.as_dict())
    module.exit_json(changed=True, promotion=result, command=command, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()
