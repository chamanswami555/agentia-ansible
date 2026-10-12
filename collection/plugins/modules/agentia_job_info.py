#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_job_info
short_description: Read Copado job executions through Agentia CLI
version_added: "0.1.0"
description:
  - Returns one job execution with its ordered steps when I(id) is given, otherwise a
    page of job executions filtered by status, type, parent, name or owner.
options:
  id:
    description: Job execution id.
    type: str
  status:
    description: Exact Copado job status to filter the list by, for example C(In Progress).
    type: str
  type:
    description: Contains-match on the job template name, for example C(Deploy).
    type: str
  parent:
    description: Exact parent record id.
    type: str
  name:
    description: Contains-match on the job execution name.
    type: str
  mine:
    description: Only jobs owned by the current user.
    type: bool
    default: false
  page_size:
    description: Records per page, 1 to 200.
    type: int
    default: 50
  logs:
    description: Also fetch the log output of the job (only with I(id)).
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
- name: Read one job with its steps and logs
  chamanswami555.agentia.agentia_job_info:
    id: a4N000000000001AAA
    logs: true
  register: job

- name: List failed deploy jobs
  chamanswami555.agentia.agentia_job_info:
    status: Error
    type: Deploy
"""

RETURN = r"""
job:
  description: The job execution record, when I(id) is given.
  returned: when id is given
  type: raw
jobs:
  description: The list of job executions, when I(id) is not given.
  returned: when id is not given
  type: list
log:
  description: Log output of the job, when I(logs) is true.
  returned: when logs is true
  type: raw
transaction_id:
  description: Transaction id of the last CLI call.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.chamanswami555.agentia.plugins.module_utils.agentia import (
    AgentiaCli,
    AgentiaError,
    agentia_argument_spec,
    as_list,
)


def run_module():
    spec = dict(agentia_argument_spec())
    spec.update({
        "id": {"type": "str"},
        "status": {"type": "str"},
        "type": {"type": "str"},
        "parent": {"type": "str"},
        "name": {"type": "str"},
        "mine": {"type": "bool", "default": False},
        "page_size": {"type": "int", "default": 50},
        "logs": {"type": "bool", "default": False},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    cli = AgentiaCli(module)
    try:
        if params["id"]:
            job, tx = cli.run(["cicd", "job", "get", params["id"]])
            out = {"changed": False, "job": job, "transaction_id": tx}
            if params["logs"]:
                log, tx = cli.run(["cicd", "job", "log", "get", params["id"]])
                out.update(log=log, transaction_id=tx)
            module.exit_json(**out)
        args = ["cicd", "job", "list", "--page-size", str(params["page_size"])]
        for option, flag in (("status", "--status"), ("type", "--type"), ("parent", "--parent"), ("name", "--name")):
            if params[option]:
                args += [flag, params[option]]
        if params["mine"]:
            args.append("--mine")
        result, tx = cli.run(args)
        module.exit_json(changed=False, jobs=as_list(result), transaction_id=tx)
    except AgentiaError as exc:
        module.fail_json(**exc.as_dict())


def main():
    run_module()


if __name__ == "__main__":
    main()
