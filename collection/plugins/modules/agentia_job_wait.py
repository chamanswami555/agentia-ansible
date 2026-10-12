#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_job_wait
short_description: Wait until a Copado job execution reaches a final status
version_added: "0.1.0"
description:
  - Polls C(agentia cicd job get) until the job status is one of I(final_statuses) or
    I(timeout) seconds pass. Fails when the final status is not in I(success_statuses),
    unless I(fail_on_error) is false.
options:
  id:
    description: Job execution id.
    type: str
    required: true
  status_field:
    description: Key of the status value in the job record.
    type: str
    default: status
  final_statuses:
    description: Statuses that end the wait.
    type: list
    elements: str
    default: [Success, Successful, Completed, Complete, Failed, Error, Cancelled, Canceled, Killed]
  success_statuses:
    description: Final statuses that count as success.
    type: list
    elements: str
    default: [Success, Successful, Completed, Complete]
  interval:
    description: Seconds between polls.
    type: int
    default: 15
  timeout:
    description: Maximum seconds to wait in total.
    type: int
    default: 1800
  fail_on_error:
    description: Fail the task when the job ends in a non-success status.
    type: bool
    default: true
  cli_path:
    description: Path to the C(agentia) executable.
    type: str
    default: agentia
  working_dir:
    description: Directory to run the CLI in.
    type: path
author:
  - Chaman Swami (@chamanswami555)
"""

EXAMPLES = r"""
- name: Wait for the deployment job
  chamanswami555.agentia.agentia_job_wait:
    id: "{{ promo.promotion.jobExecutionId }}"
    timeout: 3600
"""

RETURN = r"""
job:
  description: The last job record read.
  returned: always
  type: raw
status:
  description: The final (or last seen) status.
  returned: always
  type: str
polls:
  description: How many times the job was read.
  returned: always
  type: int
elapsed:
  description: Seconds spent waiting.
  returned: always
  type: int
"""

import time

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
        "status_field": {"type": "str", "default": "status"},
        "final_statuses": {"type": "list", "elements": "str",
                           "default": ["Success", "Successful", "Completed", "Complete", "Failed",
                                       "Error", "Cancelled", "Canceled", "Killed"]},
        "success_statuses": {"type": "list", "elements": "str",
                             "default": ["Success", "Successful", "Completed", "Complete"]},
        "interval": {"type": "int", "default": 15},
        "timeout": {"type": "int", "default": 1800},
        "fail_on_error": {"type": "bool", "default": True},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    cli = AgentiaCli(module)
    final = {s.lower() for s in params["final_statuses"]}
    success = {s.lower() for s in params["success_statuses"]}
    started = time.monotonic()
    polls = 0
    job, status = None, None
    try:
        while True:
            job, tx = cli.run(["cicd", "job", "get", params["id"]])
            polls += 1
            status = str((job or {}).get(params["status_field"], "")) if isinstance(job, dict) else ""
            elapsed = int(time.monotonic() - started)
            if status.lower() in final:
                break
            if elapsed >= params["timeout"]:
                module.fail_json(msg="Timed out after %ss waiting for job %s (last status: %s)"
                                     % (elapsed, params["id"], status or "unknown"),
                                 job=job, status=status, polls=polls, elapsed=elapsed, transaction_id=tx)
            time.sleep(params["interval"])
    except AgentiaError as exc:
        module.fail_json(polls=polls, **exc.as_dict())
    elapsed = int(time.monotonic() - started)
    out = {"changed": False, "job": job, "status": status, "polls": polls, "elapsed": elapsed}
    if status.lower() not in success and params["fail_on_error"]:
        module.fail_json(msg="Job %s ended with status %s" % (params["id"], status), **out)
    module.exit_json(**out)


def main():
    run_module()


if __name__ == "__main__":
    main()
