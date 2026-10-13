#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_promotion_info
short_description: Read Copado promotions through Agentia CLI
version_added: "0.1.0"
description:
  - Returns one promotion when I(id) is given (status, validation flag, last promotion and
    deployment execution ids and statuses), otherwise the promotions of a user story or a
    filtered list.
options:
  id:
    description: 18-character Salesforce promotion id.
    type: str
  work_id:
    description: User story Salesforce id (18 characters) to list its promotions.
    type: str
  status:
    description: Promotion status filter for the list.
    type: str
  page_size:
    description: Records per page, 1 to 200.
    type: int
    default: 50
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
- name: Read the promotion created by a submit
  chamanswami555.agentia.agentia_promotion_info:
    id: a17i800000XXqQ4AAL
  register: promo

- name: Promotions of a story
  chamanswami555.agentia.agentia_promotion_info:
    work_id: a1vi80000006OHNAA2
"""

RETURN = r"""
promotion:
  description: The promotion record, when I(id) is given.
  returned: when id is given
  type: raw
promotions:
  description: The promotions found, when I(id) is not given.
  returned: when id is not given
  type: list
deployment_job_id:
  description: Last deployment execution id of the promotion, when present.
  returned: when id is given
  type: str
transaction_id:
  description: Transaction id of the CLI call.
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
        "work_id": {"type": "str"},
        "status": {"type": "str"},
        "page_size": {"type": "int", "default": 50},
    })
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    cli = AgentiaCli(module)
    try:
        if params["id"]:
            promotion, tx = cli.run(["cicd", "promotion", "get", params["id"]])
            deployment = promotion.get("lastDeploymentExecutionId") if isinstance(promotion, dict) else None
            module.exit_json(changed=False, promotion=promotion, deployment_job_id=deployment, transaction_id=tx)
        args = ["cicd", "promotion", "list", "--page-size", str(params["page_size"])]
        if params["work_id"]:
            args += ["--work-id", params["work_id"]]
        if params["status"]:
            args += ["--status", params["status"]]
        result, tx = cli.run(args)
        module.exit_json(changed=False, promotions=as_list(result), transaction_id=tx)
    except AgentiaError as exc:
        module.fail_json(**exc.as_dict())


def main():
    run_module()


if __name__ == "__main__":
    main()
