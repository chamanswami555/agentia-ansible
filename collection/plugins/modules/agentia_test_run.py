#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_test_run
short_description: Run a Copado Robotic Testing job and wait for its result
version_added: "0.1.0"
description:
  - Runs C(agentia testing test run) for a CRT job, waits for the terminal build result
    and returns it. Fails when the run fails, unless I(fail_on_test_failure) is false.
  - This is an action, so the task reports C(changed) whenever it runs.
options:
  job_id:
    description: CRT job (test) id.
    type: str
    required: true
  project_id:
    description: CRT project id.
    type: str
    required: true
  branch:
    description: Git branch or ref for a Git-backed job.
    type: str
  wait_timeout:
    description: Seconds to wait for the run.
    type: int
    default: 1800
  fail_on_test_failure:
    description: Fail the task when the CRT run fails.
    type: bool
    default: true
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
    default: 2000
author:
  - Chaman Swami (@chamanswami555)
"""

EXAMPLES = r"""
- name: Run the smoke suite in QA
  chamanswami555.agentia.agentia_test_run:
    job_id: "196473"
    project_id: "112901"
    branch: feature/login-smoke
  register: smoke
"""

RETURN = r"""
run:
  description: The build result as the CLI returned it.
  returned: when not in check mode
  type: raw
passed:
  description: Whether the CLI exit code reported a passing run.
  returned: when not in check mode
  type: bool
command:
  description: The CLI argument list that ran.
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
    spec["timeout"] = {"type": "int", "default": 2000}
    spec.update({
        "job_id": {"type": "str", "required": True},
        "project_id": {"type": "str", "required": True},
        "branch": {"type": "str"},
        "wait_timeout": {"type": "int", "default": 1800},
        "fail_on_test_failure": {"type": "bool", "default": True},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    command = ["testing", "test", "run", params["job_id"], "--project", params["project_id"],
               "--wait-for-result", "--timeout", str(params["wait_timeout"])]
    if params["branch"]:
        command += ["--branch", params["branch"]]
    if module.check_mode:
        module.exit_json(changed=True, command=command)
    cli = AgentiaCli(module)
    try:
        # The CLI exits nonzero when the waited run fails but still prints the result.
        result, tx = cli.run(command, ok_exit_codes=(0, 1, 100))
    except AgentiaError as exc:
        module.fail_json(changed=False, command=command, **exc.as_dict())
    passed = cli.last_rc == 0
    out = {"changed": True, "run": result, "passed": passed, "command": command, "transaction_id": tx}
    if not passed and params["fail_on_test_failure"]:
        module.fail_json(msg="Robotic Testing run for job %s failed (CLI exit code %s)" % (params["job_id"], cli.last_rc), **out)
    module.exit_json(**out)


def main():
    run_module()


if __name__ == "__main__":
    main()
