#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_health_check
short_description: Run Copado organization governance health checks
version_added: "0.1.0"
description:
  - Runs C(agentia cicd health-check --json) and returns the findings. Optionally also
    analyzes a local Git clone with git-sizer.
options:
  git_sizer:
    description: Also analyze a local Git clone with git-sizer.
    type: bool
    default: false
  path:
    description: Local Git clone for I(git_sizer). Defaults to the working directory.
    type: path
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
- name: Collect the governance health check as release evidence
  chamanswami555.agentia.agentia_health_check:
  register: health
"""

RETURN = r"""
health:
  description: The health-check result as the CLI returned it.
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


def run_module():
    spec = dict(agentia_argument_spec())
    spec.update({"git_sizer": {"type": "bool", "default": False}, "path": {"type": "path"}})
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    args = ["cicd", "health-check"]
    if module.params["git_sizer"]:
        args.append("--git-sizer")
        if module.params["path"]:
            args += ["--path", module.params["path"]]
    cli = AgentiaCli(module)
    try:
        result, tx = cli.run(args)
    except AgentiaError as exc:
        module.fail_json(**exc.as_dict())
    module.exit_json(changed=False, health=result, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()
