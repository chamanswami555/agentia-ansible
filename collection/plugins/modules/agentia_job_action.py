#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_job_action
short_description: Run, resume, pause or cancel a Copado job execution
version_added: "0.1.0"
description:
  - Runs one of C(agentia cicd job run), C(resume), C(pause) or C(kill) for a job
    execution id. This is an action, so the task reports C(changed) whenever it runs.
options:
  id:
    description: Job execution id.
    type: str
    required: true
  action:
    description: What to do with the job.
    type: str
    choices: [run, resume, pause, kill]
    required: true
  restart:
    description: With I(action=run), restart from the first step.
    type: bool
    default: false
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
- name: Resume the outstanding steps of a failed job
  chamanswami555.agentia.agentia_job_action:
    id: a4N000000000002AAA
    action: resume
"""

RETURN = r"""
job:
  description: The result as the CLI returned it.
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


def run_module():
    spec = dict(agentia_argument_spec())
    spec.update({
        "id": {"type": "str", "required": True},
        "action": {"type": "str", "choices": ["run", "resume", "pause", "kill"], "required": True},
        "restart": {"type": "bool", "default": False},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    command = ["cicd", "job", params["action"], params["id"]]
    if params["action"] == "run" and params["restart"]:
        command.append("--restart")
    if module.check_mode:
        module.exit_json(changed=True, command=command)
    cli = AgentiaCli(module)
    try:
        result, tx = cli.run(command)
    except AgentiaError as exc:
        module.fail_json(changed=False, command=command, **exc.as_dict())
    module.exit_json(changed=True, job=result, command=command, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()
