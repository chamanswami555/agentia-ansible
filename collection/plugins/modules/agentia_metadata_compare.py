#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_metadata_compare
short_description: Compare Salesforce metadata between orgs or Git branches
version_added: "0.1.0"
description:
  - Runs C(agentia cicd metadata index compare) and returns the comparison, for use as a
    pre-release check or as release evidence.
options:
  comparison_mode:
    description: Comparison mode.
    type: str
    choices: [BRANCH_COMPARE, INDEX_FILE, MIX]
    default: BRANCH_COMPARE
  filter_type:
    description: Optional metadata type filter, for example C(ApexClass).
    type: str
  pipeline_id:
    description: Pipeline id.
    type: str
  source_credential_id:
    description: Source org credential id.
    type: str
  source_org_id:
    description: Source org id.
    type: str
  target_org_id:
    description: Target org id.
    type: str
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
- name: Compare Apex classes between UAT and production
  chamanswami555.agentia.agentia_metadata_compare:
    comparison_mode: INDEX_FILE
    filter_type: ApexClass
    pipeline_id: a0M000000000001EAA
    source_org_id: 00D000000000001
    source_credential_id: a0U000000000001
    target_org_id: 00D000000000002
  register: compare
"""

RETURN = r"""
comparison:
  description: The comparison result as the CLI returned it.
  returned: always
  type: raw
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
)

FLAGS = (("filter_type", "--filter-type"), ("pipeline_id", "--pipeline-id"),
         ("source_credential_id", "--source-credential-id"), ("source_org_id", "--source-org-id"),
         ("target_org_id", "--target-org-id"))


def run_module():
    spec = dict(agentia_argument_spec())
    spec["comparison_mode"] = {"type": "str", "choices": ["BRANCH_COMPARE", "INDEX_FILE", "MIX"],
                               "default": "BRANCH_COMPARE"}
    for option, _flag in FLAGS:
        spec[option] = {"type": "str"}
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    args = ["cicd", "metadata", "index", "compare", "--comparison-mode", module.params["comparison_mode"]]
    for option, flag in FLAGS:
        if module.params[option]:
            args += [flag, module.params[option]]
    cli = AgentiaCli(module)
    try:
        result, tx = cli.run(args)
    except AgentiaError as exc:
        module.fail_json(**exc.as_dict())
    module.exit_json(changed=False, comparison=result, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()
